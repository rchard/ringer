#!/bin/bash
# Ringer engine wrapper: run OpenCode under a Linux bubblewrap sandbox.
#
# Linux counterpart of opencode-sandboxed.sh (macOS Seatbelt). Same contract:
# OpenCode has no OS-level sandbox of its own — its --dangerously-skip-permissions
# flag (required for headless runs) disables ALL of its interactive approval
# prompts. This wrapper supplies the real containment: full network and reads,
# writes confined to the task dir, a per-run scratch/cache dir, and OpenCode's
# own state dirs.
#
# Usage (as a ringer engine bin):
#   opencode-sandboxed-linux.sh <taskdir> [--no-sandbox] <opencode args...>
#
# The first argument is the task directory (pass "{taskdir}" first in
# args_template). "--no-sandbox" as the second argument skips bubblewrap
# entirely — wire it as the engine's full_access_args so ringer's
# allow_full_access gate still applies.
set -euo pipefail

TASKDIR="${1:?usage: opencode-sandboxed-linux.sh <taskdir> [--no-sandbox] <args...>}"; shift
SANDBOX=1
if [ "${1:-}" = "--no-sandbox" ]; then SANDBOX=0; shift; fi

# Resolve opencode without tripping `set -e` (command -v returns nonzero when absent).
if ! OPENCODE_BIN="$(command -v opencode)" || [ -z "$OPENCODE_BIN" ]; then
  echo "opencode-sandboxed-linux.sh: opencode not found on PATH" >&2
  exit 127
fi

if [ "$SANDBOX" = "0" ]; then
  exec "$OPENCODE_BIN" "$@" < /dev/null
fi

if ! command -v bwrap > /dev/null 2>&1; then
  echo "opencode-sandboxed-linux.sh: bwrap (bubblewrap) not found." >&2
  echo "Install it (apt install bubblewrap), use the engine's full-access mode" >&2
  echo "(--no-sandbox), or add your own sandbox." >&2
  exit 1
fi

TASKDIR_REAL="$(cd "$TASKDIR" && pwd -P)"

# Per-run scratch root — becomes both TMPDIR and XDG_CACHE_HOME for OpenCode, so
# we never have to open all of /tmp or ~/.cache to the sandboxed agent.
SCRATCH="$(cd "$(mktemp -d -t ringer-opencode-scratch.XXXXXX)" && pwd -P)"
cleanup() { rm -rf "$SCRATCH"; }
trap cleanup EXIT

mkdir -p "$SCRATCH/cache"

# OpenCode's state and config dirs must stay writable. Create any that are
# missing so the bind never fails.
OC_SHARE="$HOME/.local/share/opencode"
OC_STATE="$HOME/.local/state/opencode"
OC_CONFIG="$HOME/.config/opencode"
mkdir -p "$OC_SHARE" "$OC_STATE" "$OC_CONFIG"

# Per-run private data dir (XDG_DATA_HOME). OpenCode keeps one SQLite session DB
# under its data dir and writes to it at startup without waiting on a busy
# lock, so parallel workers sharing ~/.local/share/opencode/opencode.db die
# with "database is locked" (reproduced 2026-10-04 on opencode 1.18.34: 1 of 6
# simultaneous starts). Each worker gets its own DB instead; auth.json is
# bind-mounted read-only from the real data dir, never copied.
DATA_DIR="$SCRATCH/data/opencode"
mkdir -p "$DATA_DIR"
AUTH_BIND=()
if [ -f "$OC_SHARE/auth.json" ]; then
  : > "$DATA_DIR/auth.json"
  AUTH_BIND=(--ro-bind "$OC_SHARE/auth.json" "$DATA_DIR/auth.json")
fi

export TMPDIR="$SCRATCH"
export XDG_CACHE_HOME="$SCRATCH/cache"
export XDG_DATA_HOME="$SCRATCH/data"

# Whole filesystem readable, nothing writable, then punch through exactly the
# writable paths. Paths are passed as separate argv elements, never interpolated
# into a shell string, so a task dir containing spaces/quotes/newlines is inert.
# Network is deliberately NOT unshared: the agent must reach its model API.
# --die-with-parent ensures a ringer timeout kill tears the sandbox down too.
set +e
bwrap \
  --ro-bind / / \
  --dev /dev \
  --proc /proc \
  --tmpfs /tmp \
  --bind "$TASKDIR_REAL" "$TASKDIR_REAL" \
  --bind "$SCRATCH" "$SCRATCH" \
  "${AUTH_BIND[@]}" \
  --bind "$OC_STATE" "$OC_STATE" \
  --bind "$OC_CONFIG" "$OC_CONFIG" \
  --unshare-pid \
  --die-with-parent \
  --chdir "$TASKDIR_REAL" \
  -- "$OPENCODE_BIN" "$@" < /dev/null
status=$?
set -e
exit "$status"
