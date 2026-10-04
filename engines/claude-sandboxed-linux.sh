#!/bin/bash
# Ringer engine wrapper: run Claude Code headless (`claude -p`) under a Linux
# bubblewrap sandbox, on the user's Claude subscription (OAuth), not an API key.
#
# Same contract as opencode-sandboxed-linux.sh: headless runs need
# --dangerously-skip-permissions, so this wrapper supplies the real
# containment — full network and reads, writes confined to the task dir, a
# per-run scratch dir, and Claude Code's own state (~/.claude, ~/.claude.json),
# which it needs to read and refresh its OAuth credentials.
#
# Usage (as a ringer engine bin):
#   claude-sandboxed-linux.sh <taskdir> [--no-sandbox] <claude args...>
#
# Claude Code prints one JSON result object (--output-format json). After it
# exits, this wrapper appends two summary lines derived from that object so
# ringer's default token regex and a model_report_regex can read them:
#   tokens used: <input + cache + output tokens>
#   model: <model id that actually served the run>
set -euo pipefail

TASKDIR="${1:?usage: claude-sandboxed-linux.sh <taskdir> [--no-sandbox] <args...>}"; shift
SANDBOX=1
if [ "${1:-}" = "--no-sandbox" ]; then SANDBOX=0; shift; fi

if ! CLAUDE_BIN="$(command -v claude)" || [ -z "$CLAUDE_BIN" ]; then
  echo "claude-sandboxed-linux.sh: claude not found on PATH" >&2
  exit 127
fi
CLAUDE_BIN="$(readlink -f "$CLAUDE_BIN")"

# A worker must be its own top-level session, not a child of the orchestrating
# Claude Code session ringer may have been launched from.
unset CLAUDECODE CLAUDE_CODE_ENTRYPOINT CLAUDE_CODE_SSE_PORT

TASKDIR_REAL="$(cd "$TASKDIR" && pwd -P)"
SCRATCH="$(cd "$(mktemp -d -t ringer-claude-scratch.XXXXXX)" && pwd -P)"
cleanup() { rm -rf "$SCRATCH"; }
trap cleanup EXIT
mkdir -p "$SCRATCH/cache"
export TMPDIR="$SCRATCH"
export XDG_CACHE_HOME="$SCRATCH/cache"

CL_DIR="$HOME/.claude"
CL_JSON="$HOME/.claude.json"
mkdir -p "$CL_DIR"
[ -e "$CL_JSON" ] || echo '{}' > "$CL_JSON"

OUT="$SCRATCH/claude-output.json"

set +e
if [ "$SANDBOX" = "0" ]; then
  (cd "$TASKDIR_REAL" && "$CLAUDE_BIN" "$@" < /dev/null) | tee "$OUT"
  status=${PIPESTATUS[0]}
else
  if ! command -v bwrap > /dev/null 2>&1; then
    echo "claude-sandboxed-linux.sh: bwrap (bubblewrap) not found." >&2
    exit 1
  fi
  # Whole filesystem readable, nothing writable, then punch through exactly the
  # writable paths. Network stays shared: the agent must reach its model API.
  bwrap \
    --ro-bind / / \
    --dev /dev \
    --proc /proc \
    --tmpfs /tmp \
    --bind "$TASKDIR_REAL" "$TASKDIR_REAL" \
    --bind "$SCRATCH" "$SCRATCH" \
    --bind "$CL_DIR" "$CL_DIR" \
    --bind "$CL_JSON" "$CL_JSON" \
    --unshare-pid \
    --die-with-parent \
    --chdir "$TASKDIR_REAL" \
    -- "$CLAUDE_BIN" "$@" < /dev/null | tee "$OUT"
  status=${PIPESTATUS[0]}
fi
set -e

python3 - "$OUT" <<'PY' || true
import json, sys
try:
    text = open(sys.argv[1]).read()
    obj = json.loads(text[text.index("{"):])
except Exception:
    sys.exit(0)
u = obj.get("usage") or {}
total = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens",
                                          "cache_read_input_tokens", "output_tokens"))
if total:
    print(f"tokens used: {total}")
models = list((obj.get("modelUsage") or {}).keys())
if models:
    # The main model carries the most output; helper calls (e.g. a small model) carry less.
    main = max(models, key=lambda m: (obj["modelUsage"][m] or {}).get("outputTokens", 0))
    print(f"model: {main}")
PY
exit "$status"
