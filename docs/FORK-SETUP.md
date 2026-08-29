# This checkout's fork setup

This repo was originally developed by NateBJones-Projects. This checkout
carries local-only changes (the Linux bubblewrap sandbox wrapper for the
opencode engine, mainly) needed to run Ringer on this machine, which are
not intended to be sent back upstream. Set up 2026-08-29 to fix a recurring
problem: those local changes lived only on this one machine with no backup
and no clean way to pull the original's updates.

## Remotes

- `origin` -> `https://github.com/rchard/ringer` (your fork; push here)
- `upstream` -> `https://github.com/NateBJones-Projects/ringer` (the
  original; pull-only, never push here — you likely don't have write
  access anyway)

Check with `git remote -v`.

## Branches

- `main` -> tracks `upstream/main` directly. Treat this as a pure mirror
  of the original. Don't commit here; just pull it.
- `local` -> your actual working branch. Sits on top of `main` plus your
  own commits (currently includes `engines/opencode-sandboxed-linux.sh`,
  which the `[engines.opencode]` block in `~/.config/ringer/config.toml`
  points at — losing this branch breaks the opencode engine on this
  machine). This is the branch you should normally be checked out on.

## Pulling the original developer's updates

```bash
git fetch upstream
git checkout main
git pull                      # fast-forwards main from upstream/main
git checkout local
git merge main                # brings upstream's new commits into local
```

If `git merge main` conflicts, stop and get help before resolving —
don't guess on a rebase/merge conflict here.

## Backing up your own changes

Your `local` branch only exists on your fork once you've pushed it:

```bash
git push origin local
```

Do this after any session where you (or an agent) added or changed files
in this repo. `local` is already set up to track `origin/local`, so a
plain `git push` from that branch does this.

## Checking whether you're behind the original

```bash
git fetch upstream
git log main..upstream/main --oneline
```

Empty output means you're already current. As of 2026-08-29, `local`'s
fork point was exactly `upstream/main`'s tip (commit `a1a91b8`), so
nothing was behind at setup time.

## Why not just work on `main`?

Ringer's own self-update mechanism (see README.md's "Self-update"
section) only auto-pulls when the checkout is on `main` with a clean
tracked tree. Since this checkout needs to carry local-only commits
indefinitely, it can never just live on `main` — hence the `local`
branch and the manual sync steps above.
