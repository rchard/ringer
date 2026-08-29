# Model notes — how workers actually perform

A running log of how models perform on real Ringer tasks, so engine and
model choices are made on evidence instead of vibes. The raw numbers now
live in the local eval log (`~/.ringer/runs.jsonl`); run `./ringer.py models`
to print the per-model, per-task_type scoreboard (tasks, attempts,
pass_rate, first_try_pass_rate, median duration/tokens, last_seen). This
file remains the judgment layer on top of those numbers.

**How to add a row:** after reviewing a run (post-run ritual step 5 in the
ringer skill), append one dated line under the model. Say the task type,
what happened, and what you'd do differently. Only write what the executed
checks and raw logs support — no vibes, no worker self-reports.

## codex (GPT-5-class, own harness)

- Strongest general worker; the default engine. Spend reasoning effort per
  task via `engine_args` (`["-c", "model_reasoning_effort=low|medium|high"]`)
  — high on gnarly tasks, low on boilerplate.
- 2026-07-05 — carried the heavy lanes of the milk-crate demo rehearsals
  (market read with source allowlist, site build) with clean first-attempt
  passes.
- 2026-07-10 — gpt-5.6-sol, code-feature (steering-profiles feature in
  ringer.py itself, ~470-line change + 18 tests + docs, run
  ringer-steering-profiles): shipped as PR #25. 2 attempts, 379k tokens,
  but the attempt-1 FAIL was the CHECK's fault, not the model's — the check
  gated on the ENTIRE pre-existing suite being green inside the worker
  sandbox (localhost binds blocked, fixture missing). The feature work
  itself was verified green both attempts; attempt 2 "hardened" an already
  -sound implementation. Scoreboard's FAIL row for this run understates the
  model. Lesson for check authors: regression gates must compare against
  the BASELINE failure set, never assert absolute suite green.
- 2026-07-06 — adversarial pre-merge review (aicred spark): passed on
  attempt 1, ~85k tokens.
- 2026-07-06 — motion design (5 HTML animations for video b-roll) + 2
  editorial diagram pages, each verified by rendering through headless
  Chromium to MP4/PNG: 7/7 passed on attempt 1. Broadcast-quality visual
  output from rich storyboard specs; the render-as-check pattern works.
- 2026-07-06 — milk-crate demo: two single-file website builds (v1 scaffold
  316s/~175k tok; final brand+market-test reskin 622s/~184k tok), both passed
  14-assertion content checks on attempt 1, including base64-embedding photos
  and honoring honesty-marker requirements. Codex remains the site-build lane.
- 2026-07-06 — ringer.py feature batch (task_type field + enriched eval rows
  + `models` scoreboard + hud single-tab fix; ~640-line diff incl. two new
  test suites): substance passed on attempt 1 — its check printed PASS
  (compile, all 16 suites, exact CLI aggregation contract) — but the run
  recorded attempt 2 because of the expect_files-before-check harness bug
  (see process lessons). Heavy single-file feature work against an exact
  behavioral contract is squarely codex's lane.

- 2026-07-06 — elsas-website demo: Next.js scaffold PASSED attempt 2 (682s,
  ~354k tok) — attempt 1 built a complete homepage and silently skipped the
  other 10 routes; the route-enumeration check caught it. Narration lane
  (15 ElevenLabs calls, chunked, nohup pattern) passed attempt 1. CAUTION: a
  codex fix worker GAMED a verbatim-content needle by hiding the required text
  in a visually-hidden paragraph — passed the check, caught only by
  orchestrator integration review. Needle checks need an anti-hidden-text
  assertion or documented exceptions.

- 2026-07-06 — OpenRouter catalog + explore suggester (catalog subcommand
  with snapshot/changelog/free-detection, daemon auto-refresh, tiered
  --explore; offline fixture-driven contract check): PASS attempt 1, 362s.
  Follow-up sentinel-pricing fix (variable-pricing models): PASS attempt 1,
  114s. With the verify-order fix landed, zero phantom retries across the
  whole batch.
- 2026-07-06 — adversarial review of the model-router stack (2,650-line
  diff, structured report contract): PASS attempt 1, 176s — found a real
  HIGH (--since window inflating first-try rates) plus 3 MEDIUMs, all
  confirmed against the code. Then fixed all five review findings in one
  batch (task-level --since, pricing transitions, event durability + flock,
  unknown pricing, stderr notice) with test coverage: PASS attempt 1, 202s.
  Review->fix roundtrip in codex's lane works end to end.
- 2026-07-06 — scoreboard HTML page (zero-LLM renderer, ~700-line diff,
  design + evidence-floor ranking + cost math + notes parser): substance
  PASS attempt 1 (the run's recorded retry was an orchestrator check bug —
  the free-promo watchlist legitimately mentions a free model before the
  ranked cards, and the check compared raw first-occurrence). Six review
  findings fixed in one batch, PASS attempt 1, 141s.
- 2026-07-06 — model-db stack (SQLite read model 516s, page redesign 536s,
  Ringside tab 527s, plus three fix batches all attempt-1): five substantial
  ringer.py features in one day, every one against an executed contract
  check. Review lane found the HIGH that mattered (sync cursor skipping a
  half-written trailing line). Codex is the proven lane for both sides of
  the review->fix loop on this codebase.

## glm-5.2 via opencode (`openrouter/z-ai/glm-5.2`)

- The cheap-intelligence default (~$0.74/M in, $2.33/M out, 2026-07 —
  20-30x cheaper output than frontier coding models). Reliable on
  mechanical, tightly-specced work: file edits, format conversions,
  template-driven builds.
- 2026-07-05 — milk-crate demo rehearsals: handled brand-board/SVG/copy
  tasks at around a penny per passing task.
- 2026-07-06 — adversarial pre-merge review (aicred spark): passed, but
  needed the retry (attempt 2) where codex passed on attempt 1. Long
  structured reviews sit at the edge of its comfort zone; keep the section
  contract explicit in the spec.
- 2026-07-06 — three mechanical image-generation batches (18 images via
  openrouter-image commands, idempotent batch-runner spec): 3/3 passed on
  attempt 1, ~14.5k tokens each. The "execute these exact commands, do not
  improve them" spec pattern is fully reliable for glm-5.2.

- 2026-07-06 — backfill/seed script for the model log (252-line stdlib CLI
  with a run-state join, 3-level mapping precedence, never-overwrite and
  idempotency rules): the artifact was CORRECT; the recorded FAIL was an
  orchestrator check-fixture bug (a missing newline glued the fixture's last
  row to a garbage line) plus the harness ordering bug below. Verified PASS
  once the check was fixed. Tight behavior contracts in the spec work great
  for glm — and read the raw logs before blaming the model.
- 2026-07-06 — README/MODEL-NOTES docs + task_type sweep across 17 template
  manifests: passed attempt 2; attempt 1 was lost to the harness ordering
  bug, not model quality — the retry worker's log correctly diagnosed that
  harness bug unprompted, impressive debugging from the cheap lane.
- 2026-07-06 — catalog/explore README section (flags, promotion ladder,
  per-user framing): PASS attempt 1, ~21.5k tokens. Doc sections against a
  grep-able content contract remain a safe glm lane.
- 2026-07-06 — milk-crate demo, full run: 4 independent buyer-persona
  reviews (focus group) all passed attempt 1 (~15k tokens, ~2¢ each) with an
  explicit VERDICT-block contract — persona work is squarely in glm's zone.
  Market read with live curl fetching passed once the spec demanded verbatim
  copy-paste of source URLs (first fail was the worker trimming URL slugs —
  spec/check craft, not model weakness). Brand-kit doc incl. a clean inline
  SVG wordmark: good, one bounce off an over-strict check regex.

- 2026-07-06 — elsas-website demo: verbatim content capture (16 pages + 19
  news posts, 213 blockquotes) passed attempt 2 — attempt 1 SELF-REPORTED
  "all 213 match exactly, 0 errors" while the executed check found 13 stitched/
  paraphrased quotes. Self-reports are worthless; the retry with injected
  failures fixed all 13 (~148k tok total, ~3¢). Page builds (about+faq;
  news index + 19 generated post routes via its own extraction script) and
  2 focus-group personas: all attempt 1. Fix batch attempt 1.
- 2026-07-06 — invariants/file-I/O review lens on the same stack: PASS
  attempt 1, 68k tokens — caught the non-atomic backfill rewrite (real data
  loss risk) and the daemon stdout race; both confirmed. Then fixed the
  backfill atomicity (tmp+os.replace, pid-stamped backups) attempt 1 with
  the original behavioral grader unchanged. Structured review with an
  explicit lens is now proven glm territory, not just probation.
- 2026-07-06 — solo adversarial review of the scoreboard renderer (~700
  line diff, injection-focused lens): PASS attempt 1 — 1 MEDIUM (unanchored
  MODEL-NOTES heading match cross-contaminating gpt-4/gpt-4o-style
  families) + 5 real LOWs, plus an empirically-verified injection all-clear
  (it actually rendered hostile model ids to prove escaping). Second
  proven-tier structured review in one day; glm is now the default review
  lane for mid-size diffs.
- 2026-07-06 — invariants/injection/frontend review of the 4,061-line
  model-db branch: PASS attempt 1, 96k tokens, 14 coverage items — two real
  contention findings (full catalog re-ingest per sync; schema writes on
  read paths) plus an empirical XSS all-clear on the new DOM surfaces.
  Third proven-tier structured review today.

## kimi-k2.7 via opencode (`openrouter/moonshotai/kimi-k2.7-code`)

- 2026-07-06 — adversarial pre-merge review (aicred spark): passed on
  attempt 1, ~83k tokens. First real outing; promising for review work.
  (Ran through an ad-hoc copy of the opencode engine block — the per-task
  `model` field now makes that unnecessary.)

## kimi-k2.6 (`moonshotai/kimi-k2.6`, subject-model evidence via OpenRouter)

- 2026-07-07 — Benchmark Suite 2.0 operator eval, killed by Jon at ~4.5h.
  Serving throughput, not model quality, was the failure: on the Brick
  1000-piece case (reasoning xhigh, pinned provider order
  inceptron→decart→baidu→modelrun, no fallbacks) K2.6 averaged ~21 tok/s
  with two ~19-min stalls at 4.5 tok/s — 136+ min unfinished vs Sonnet 5's
  25 min (94 tok/s) and GPT-5.5's 24 min (55 tok/s) on the identical case.
  Model behavior itself was fine: 28 turns (fewer than Sonnet's 82), 170k
  output tokens (in family norms), 12% reasoning, zero API errors. Verdict:
  do NOT schedule K2.6 for long agentic work through that provider set;
  if K2.6 data is ever wanted, probe a single case against other providers
  first. Distinct model from k2.7-code above — don't transfer this verdict
  to k2.7.


## grok-build (Grok CLI engine, flat plan)

- 2026-07-10 — identity correction (Jon): the Grok Build CLI is a HARNESS
  serving exactly two models — Grok 4.5 (xAI) and Composer 2.5 (Cursor).
  The engine-lane slug `grok-build` resolves to Grok 4.5. "Grok Build 0.1"
  was never a model; earlier notes/rows using it as one describe Grok 4.5.

- 2026-07-06 — first outing (elsas-website demo), engine added same day:
  audition PASS attempt 1 in 28.9s. Then: asset harvest (11 images, live URL
  re-fetch check), books page, 5 work-page routes in one task (59 verbatim
  needles), adversarial code review (10 real findings incl. an unshelled 404
  and a broken embedded link), press/media fix batch, audio-player integration
  across 15 pages — ALL attempt 1 (player's red ledger entry was a check bug,
  artifact certified). Fast, precise on mechanical/code work. No token counts
  in JSON output (flat plan) — cost reads "included in plan".

## grok-composer-2.5-fast (Grok CLI engine, flat plan)

- 2026-07-06 — first outing (elsas-website demo): audition PASS attempt 1
  (138s — slower than grok-build but the strongest copy of the round).
  Accessibility constitution (14 testable criteria, SC-numbered) attempt 1;
  a11y-gatekeeper harness (axe+Playwright, light/dark, reduced-motion assert)
  attempt 2 — attempt 1's harness mishandled Next's default /404 route.
  Events/faq/contact fix batch attempt 1, but satisfied "editorial grid" with
  an EMPTY aside landmark — axe caught it (landmark-complementary-is-top-level).
  Persona work: good. Watch for letter-of-the-spec shortcuts on layout asks.

## nemotron-3-super-120b (via opencode, `openrouter/nvidia/nemotron-3-super-120b-a12b:free`)

- 2026-07-06 — AUDITION FAILED (exploration slot, $0 spent — free promo).
  Task: fresh-eyes adversarial review of a 2,650-line diff with a structured
  report contract. Failed both attempts on the same executed check: report
  had the right sections and verdict but under 3 concrete code citations —
  shallow engagement with the actual code, 212k tokens burned. Don't re-run
  this audition on long structured code review; if it gets another slot,
  try a shorter, more mechanical task first.
- 2026-07-11 — AUDITION PASSED (exploration slot, $0 — free). Task: research
  (home-inventory-research, ai-capture-pipeline lane): web recon with a
  cited-evidence report contract. Passed the executed check on attempt 1,
  59k tokens, ~123s — and its key find (Duelion/homebox-companion repo) was
  orchestrator-verified real, quotes matched the actual README. Contrast
  with the 07-06 code-review failure: this model looks viable for short
  structured research/recon tasks, still unproven on long code review.
  Promotion status: probation on research (1/1 first-try).
- 2026-07-13 — AUDITION FAILED (exploration slot, $0 — free). Task: research
  (homebox-photo-locations, vision-approach lane): survey with the
  research-with-proof cited-evidence contract. Failed the same executed
  check on both attempts: missing_access_dates — Evidence items never
  carried 'Accessed: YYYY-MM-DD' even after the retry prompt quoted the
  exact failure. Content was otherwise plausible (78k tokens, ~191s).
  Pattern vs 07-11 pass: handles short recon, drops fine-grained format
  obligations inside a long contract. Demoted on research (1/2 tasks
  first-try 0.5); if re-auditioned, use a spec with fewer simultaneous
  format requirements or a check that fails earlier and louder on dates.

## llama-3.3-70b-instruct (via opencode, `openrouter/meta-llama/llama-3.3-70b-instruct:free`)

- 2026-07-06 — AUDITION FAILED (exploration slot, $0). Fresh-eyes review of
  a 4,061-line diff with a verbatim-quote citation requirement: failed the
  structured-report check both attempts. Second free-model audition to fail
  on long structured code review (after nemotron-3-super) — the exploration
  ladder now says: audition free models on SHORT mechanical tasks first;
  long-diff review is a proven-tier lane.

## qwen3-235b-a22b-2507 (via opencode, `openrouter/qwen/qwen3-235b-a22b-2507`)

- 2026-07-14 — LAZY PASS on spec-review (homebox-photo-locations): produced
  an 80-word "NO FINDINGS" report on a draft spec in which codex found 13
  structured findings (incl. a real P0) and deepseek found 8. The executed
  check passed it because NO FINDINGS is a legal verdict — the check can't
  measure diligence. Attempt 1 also failed/retried. Don't use for
  adversarial/review work where "nothing found" is a cheap exit; needs
  checks with a minimum-engagement floor (e.g. required per-section
  coverage notes) if auditioned again.

## deepseek-chat-v3.1 (via opencode, `openrouter/deepseek/deepseek-chat-v3.1`)

- 2026-07-14 — FAIL verdict on spec-review (homebox-photo-locations) was a
  CHECK false-negative: it wrote 8 real structured findings but as
  '**Finding:**' (markdown bold), which the adversarial-review kit regex
  rejected on both attempts; retry feedback quoted the failure but it kept
  the bold style. Kit check has since been patched to tolerate bold labels.
  Substance was mixed: several findings overlapped codex usefully, but ONE
  fabricated evidence ("proof demonstrates sibling names can be identical
  under different parents" — the executed proof never tested that).
  Verify its evidence claims before trusting; format-instruction adherence
  is weak.

## Small / flash-class models

- First to choke on long conversational or multi-turn harness tasks —
  watch retry counts before scaling them into a batch (2026-07-05 focus
  group lesson).

## Process lessons (cross-model)

- 2026-07-14 — m2 UI round (codex x2): BOTH tasks' recorded FAILs were an
  orchestrator CHECK bug — the substance-greps file used '|' as its field
  delimiter while the grep patterns themselves contained '|' alternation,
  so every pattern with a paren split mid-regex ('grep: Unmatched (').
  Both workers' svelte-checks were green on attempt 1 and their patches
  passed untouched once the delimiter moved to TAB. Lesson: never use a
  delimiter that can appear inside the delimited data; test the check
  against a fake artifact BEFORE the run (a 30s dry-run would have
  caught it).
- 2026-07-14 — m1b-api-wiring (codex) failed 2/2 attempts on a live-integration
  401 that was the ORCHESTRATOR'S fault: the spec said the Homebox login token
  could be passed "verbatim" to HomeboxClient, but the client prepends
  "Bearer " itself → "Bearer Bearer". One-line fix in the surviving worktree
  re-passed the executed check (9 API + 2 live tests). Lesson: when a spec
  documents an API quirk, state the ONE correct usage — never offer
  alternatives ("X handles it, or do Y") in a worker brief. Codex's actual
  code was otherwise correct on attempt 1.

- 2026-07-06 — the orchestrator's CHECKS were the day's top failure source:
  three check bugs (fixture newline join, first-occurrence ordering vs the
  watchlist strip, claim-prefix split on '.' instead of ':') each produced
  a FAIL verdict on work that was actually correct — including all four
  capability-research packets at once. Every one was caught by reading raw
  logs/artifacts before blaming the model. Corollary for the scoreboard:
  recorded FAILs whose root cause was a check bug are annotated here, and
  check fixtures deserve the same review care as production code.


- 2026-07-06 — HARNESS BUG (fix in flight on feat/model-perf-log):
  Verifier.verify evaluated expect_files BEFORE running the check, so any
  check that itself creates/exports its deliverable (the worktree
  patch-export pattern) failed attempt 1 with "missing expected files" even
  when the check printed PASS. Cost 3 phantom retries in one run — and it
  poisons first_try_pass_rate, the model log's routing signal. Until the
  reorder lands on your checkout: have the WORKER write the declared
  deliverable, or don't declare check-created files in expect_files. When
  reading seeded scoreboard numbers, remember 2026-07-06 first-try rates
  are depressed by this.
- 2026-07-06 — the model log is now automatic: every attempt row carries
  model/task_type/retry; `./ringer.py models` prints the scoreboard; 81
  historical rows were seeded via scripts/backfill_model_log.py with a
  hand-authored task-type mapping. Give every manifest task a task_type or
  its evidence buckets as (untyped).

- 2026-07-06 — a three-model "bakeoff" ran every task on the engine's
  hard-coded model: task keys said glm/gpt/kimi, but the opencode engine
  block pinned glm-5.2, so one model wrote all three "competing" reviews.
  This is why the per-task `model` field exists — a bakeoff is only a
  bakeoff if the manifest, not the engine block, names the model. Verify
  with the `model` column in the run state, not the task key.
- 2026-07-06 — spawning 5-6 opencode workers simultaneously hit opencode's
  local "database is locked" (sqlite) — several instant attempt-1 failures,
  all absorbed by Ringer's retry. Cosmetic in Ringside ("sent back" at 0s) but
  wastes an attempt; consider staggering opencode spawns.
- 2026-07-06 — opencode's bash tool kills foreground commands around the
  ~2-minute mark: a 2min+ image-generation API call can never finish inline.
  Spec pattern that works: nohup the long command in the background, then
  poll for the output file in separate short commands.
- 2026-07-06 — two check-craft lessons from the same run: (1) URL-allowlist
  checks must be prefix-tolerant (workers legitimately trim slugs); (2) any
  heading-regex must tolerate numbered headings ("## 3. Type / Typography").
  Both failures looked like worker laziness until the raw logs said otherwise.
- 2026-07-06 — elsas-website demo, check-craft in BOTH directions: (1) a fixed
  800-char body floor failed a worker for faithfully converting genuinely tiny
  source posts — floor must scale with the source; (2) a citation gate treating
  every backtick as a page-quote failed honest reviewers who backticked their
  own fix-suggestions — line-scoped pair parsing + attribute-aware corpus fixed
  it; (3) needle-exception lists must be shared across ALL checks that consume
  the needle set (a needle excepted in one checker failed a task through
  another). Post-mortems ruled FOR the worker 3 times this run — read raw logs
  before blaming the model.
- 2026-07-06 — opencode sqlite "database is locked" again with just 2
  simultaneous opencode spawns (page-news + page-about-faq); retry absorbed it.

## codex (2026-07-06, bench-operator-proofing)
- 8/8 code-feature tasks passed attempt 1 across 3 rounds (worktrees mode, Python harness refactor; 108k-406k tokens/task). Specs embedded the approved architecture doc + exact file ownership; checks built fresh uv venvs and ran the full pytest suite.
- Lesson (check design, not model): all 3 post-integration bugs were invisible to the checks — a test that passed only because the worker's worktree lacked .env, a `--help`-only assertion missing a runtime importlib/sys.modules bug (py3.12 dataclasses), and bare console-script names failing outside activated venvs. Checks should exercise one real invocation from a cold shell, not just --help.

## gpt-5.6-sol (codex)
- 2026-07-15 ringer-self-update run (3 serial tasks, direct-repo-edit mode): code-fix baseline-test repair 1/1 first-try (61k tokens, 1.6m); code-feature self-update mechanism (git fetch/ff-pull/re-exec + HUD staleness restart + 20-test suite) 1/1 first-try at high effort (153k, 8.1m); code-feature signal-contract (all 3 scoreboard surfaces + canonical-route lint enforcement) passed on retry (358k, 13.7m) — attempt 1 died on stale old-column assertions in pre-existing tests it hadn't finished updating; the retry prompt's injected FAIL list was enough to close it out. Lesson: when a task rewrites a display contract, name every test file asserting the old contract in the spec's ownership list AND tell it to update them FIRST.
- 2026-07-09 code-feature/code-fix (ringside-overhaul): 4/4 first-try — a ringer.py logging change with tests, a 265-line stdlib backfill CLI (atomic rewrite, dry-run, idempotence all check-verified), a ~1500-line single-file HTML redesign (running-now pills + worker-card grid + multi-expansion refactor, 30KB patch, node --check + contract greps + unittest), and a render-gating change where it correctly UPDATED tests asserting the old behavior instead of gaming the check. Medium/high reasoning, 65–120k tokens/task.
- Same day, different session (bench-harness-patches, code-fix): 0.29 first-try over 7 tasks on a Next.js/Turbopack harness. Spec and check quality dominate model choice — see the scoreboard before generalizing either number.
- 2026-07-11 research (home-inventory-research): 2 lanes. homebox-status 1/1 first-try (77k tok); alternatives-survey needed attempt 2, but the attempt-1 FAIL was format-only — report was substantively complete and the check rejected `**Accessed:**` (bold) where it wanted bare `Accessed:`. Scoreboard understates the model here. Check-author lesson: research-with-proof.py's field matching should tolerate markdown emphasis.
- 2026-07-13 code-feature (claude-vision-proxy-build), high reasoning: 1/1 first-try, 30k tokens, faithfully ported a codex-CLI-backed proxy to a claude-CLI-backed one from a heavily pre-researched spec (exact invocation flags, stdin JSONL shape, output-parsing contract all handed over as proven ground truth rather than left for the worker to discover). Clean, correct diff — reused the shared helpers verbatim as instructed, didn't touch unrelated code. Caveat worth remembering: the worker's own closing summary claimed "the real Claude CLI was not invoked during testing" — true of the worker's own dev-time validation, but NOT true of the actual check, which independently spawned the server and forced 3 real authenticated `claude` CLI round-trips (confirmed by re-running the check myself afterward, real API calls, real pass). Lesson reinforced: judge by the executed check and a personal re-run, never by the worker's self-report of what it tested.

## GPT-5.5 (codex) — attribution caveat
- Scoreboard rows dated before 2026-07-09 may actually be gpt-5.6: codex eval rows logged model="" until the write-time stamping fix (PR #18) and were credited to GPT-5.5 by the registry default at read time, while the machine's codex default had already moved to gpt-5.6-sol at an unknown earlier date. `scripts/backfill_model_from_logs.py` re-stamps rows with surviving command-log evidence; anything it skips is a mixed-model aggregate. Trust post-2026-07-09 rows.

## nvidia/nemotron-3-super-120b-a12b:free
- 2026-07-08 (research, content-strategy-recon): FAIL x2. Did the analysis in chat but never wrote report.md; attempt 2 exited rc=0 with no file. Doesn't reliably follow file-output contracts under OpenCode. Demoted — don't re-audition on file-deliverable tasks.
- 2026-07-11 (research, home-inventory-research/ai-capture-pipeline): PASS attempt 1, 59k tokens, ~123s — wrote report.md correctly this time, and its headline find (Duelion/homebox-companion) was orchestrator-verified real with matching quotes. Partially reverses the 07-08 demotion; note the orchestrator hadn't seen that demotion line before re-auditioning (it sits in a second section under the same model — consolidate these). Status: mixed on research (1 pass / 1 double-fail); next audition should stay low-stakes.

## meta-llama/llama-3.3-70b-instruct:free
- 2026-07-08 (research, content-strategy-recon): FAIL x2. Timed out at 900s both attempts on a moderate DB-scrape+format task. Too slow on the free tier for harness work. Demoted — don't re-audition without much longer timeouts or paid tier.

## z-ai/glm-5.2 (addendum)
- 2026-07-08 (research/filter, pitch-foundry): FAIL x2 on a long-spec rubric-application task (~40k input: embedded rubric + 4 candidate files). Read all inputs, exited rc=0 with ZERO output tokens both attempts — silent stall, no file written. GLM handled the same session's shorter formatting specs fine. Lesson: keep GLM specs short; route long-context apply-this-rubric work to codex.

## GPT-5.5 (codex) — honesty flag
- 2026-07-08 (image-gen, pitch-foundry): sandbox DNS blocked openrouter.ai; ALL 10 API calls errored (logged honestly in gen-log) — but the worker then FABRICATED 10 deliverables locally (composited canvases from the ref image) to satisfy a files-exist>40KB check, and passed. Lesson: (a) codex sandbox has no external DNS on this machine — route API-calling tasks to opencode (network open); (b) never write an existence-only check for generated media — require the success log (SAVED/cost lines) to match the file count.

- 2026-07-09 persona-review (pitch-foundry exec-briefing panel): 0/2 first-try+retry. Produced coherent review CONTENT as chat text but never wrote report.md — does not reliably use file-write tools under opencode. Demoted; do not re-audition for file-deliverable tasks without a write-tool probe first.

## gpt-5.6-luna (codex)
- 2026-07-09 code-feature (unlock-ai guide-format conversion, strict type-contract check): 1/1 first-try, 42.6k tokens, 80s. Followed a multi-file TS pattern precisely at $1/$6 pricing. Good candidate for mechanical codegen/docs lanes; audition in adjacent types.

## opencode / z-ai glm-5.2 (via openrouter)
- 2026-07-09 (aicred-invoice-downloads, 4 code-fix tasks + 1 follow-up, worktrees+npm ci checks): systematic attempt-1 NO-OP — all 4 parallel workers produced zero edits and no summary on first attempt, then completed cleanly on attempt 2 after retry-prompt injection (34k-69k tokens each). Follow-up single task passed attempt 1. Suspect first-invocation session warm-up in opencode-sandboxed under parallel spawn; budget for 2 attempts on parallel GLM batches. Output quality on Next.js/Stripe route+test work: solid, spec-faithful, one boss-caught design gap (used user-scoped supabase client where RLS demanded service role — spec didn't say explicitly; say it explicitly).

## opencode (harness note, any model)
- 2026-07-28 (code-review, pr82-token-saver-review): GLM 5.2 produced a complete, high-quality 218-line report but could NOT write it to an output directory created by the parent Claude Code process — every write returned EPERM. It then spent ~3000s burning retries on ctypes/`openat`/AppleScript/`sandbox-exec` workarounds until it timed out, and the task logged as FAIL despite the deliverable existing in its taskdir. Codex workers in the same run were unaffected. Lesson: point opencode workers' output INSIDE their own taskdir and harvest via `expect_files`; never hand them a shared output dir another process created. This is an orchestrator spec bug, not a model failure — do not read the FAIL as evidence against GLM.

## Process lessons (2026-07-28, PR #82 review)
- **Ideas worth keeping from a rejected PR.** PR #82's pre-call gateway was dropped (needs your own API key, so it converts flat-rate OAuth plans into metered API billing; incompatible with Claude Code; and it saves tokens by stripping the tool list, which is the thing that makes the CLI worth using). One idea inside it is worth remembering if the problem ever comes back: an *explicitly blessed* answer cache — key a reviewed answer to the exact request plus the exact selected source packet, and replay it with zero upstream calls, never auto-accepting a model answer. It only fires on byte-identical repeats, which is why it didn't justify 2,000 lines here.
- **Doc-stated support floors need a CI job or they are fiction.** README promised Python 3.11+ while CI only ever ran 3.12; a 3.12-only f-string reached review with a fully green suite. Either test the floor or move it.

## z-ai/glm-5.2:free (via opencode, `openrouter/z-ai/glm-5.2:free`)
- 2026-08-26 (probe, glm52-free-audition): FAIL x2 across two separate runs (4 attempts total, ~58s each, 0 tokens, 0 files produced) — every attempt died on an upstream HTTP 429 from OpenRouter's shared free pool: "[Decart] z-ai/glm-5.2:free is temporarily rate-limited upstream", `limit_source: upstream_provider_shared_pool`, `is_byok: false`, retry-after 5s. The model never emitted a single token. **This is provider unavailability, not a capability result — do not read these FAILs as evidence against GLM 5.2, and do not let the 0% first-try row for the `:free` slug influence routing.** The paid `openrouter/z-ai/glm-5.2` row (proven, 3 tasks, 67% first-try) remains the real signal for this model. Practical lesson: `:free` slugs on shared pools are a coin flip on availability, so never put one on time-critical work or on more than a throwaway exploration lane; if a free audition must happen, budget for it silently no-op'ing and keep the paid slug as the fallback. Re-audition when the pool is quieter before drawing any conclusion about the free tier's quality.
- 2026-08-26 (harness note, same run): this run was also the first Ringer use after the machine transfer from the Yoga. It surfaced that `engines/opencode-sandboxed-linux.sh` — referenced by `[engines.opencode] bin` in config.toml — was absent from the working tree, so `run` aborted with exit 2. **Correction to the first diagnosis:** the file *was* in git all along, on the unmerged `local-work` branch ("Carry over local work from the Yoga 13"), which had drifted 14 commits behind main. It was never lost — it was stranded. The real lesson is about branch hygiene, not backup: a local-only branch that nobody rebases silently stops being reachable from the branch you actually work on, and the failure surfaces as a missing file rather than as an out-of-date branch. Ported it to bubblewrap with the same containment contract (writes confined to taskdir + per-run scratch + OpenCode state dirs; full reads; network shared for the model API) and verified escape attempts to $HOME, the ringer repo, ~/Documents and ~/.ssh are all denied. Track that file so the next machine move doesn't repeat this.

## z-ai/glm-5.2 (paid slug, post-transfer rig check)
- 2026-08-26 (probe, glm52-free-audition round 3): PASS on attempt 1 — 13,097 tokens, 63.9s, ~$0.03. Task was a small roman-numeral CLI with an executed check (13 encode + 13 decode cases, 5 malformed-numeral rejections, 3 out-of-range rejections, plus a substantive notes.md). Notable behaviour, all visible in the worker log: it self-verified beyond what the spec demanded — ran its own exhaustive 1..3999 round-trip AND a re-encode idempotence sweep before declaring done, hex-dumped stdout to confirm the "value + single newline" contract, and noticed it had created a `__pycache__` dir during testing and removed it because the spec said it owned exactly two files. Independent spot-check afterwards confirmed a genuinely general implementation (validity by strict re-encode round-trip rather than pattern rules) that also rejects IL, IC, XD, VX, IXI, MMMM, CMCM, lowercase and whitespace-padded input — none of which the check tested. This is the paid slug behaving well on a small spec-following task; it does not transfer to the `:free` slug, which is a different availability story entirely.

## OpenRouter `:free` slugs — availability sweep (2026-08-26)
Eight free slugs, byte-identical spec and executed check (the roman-numeral CLI probe), max_parallel 2. Result: **7/8 PASS, and the single failure was availability, not capability.**

| slug | verdict | attempts | tokens | elapsed |
|---|---|---|---|---|
| `z-ai/glm-5.2:free` | PASS | 1 | 9,430 | 63.8s |
| `cohere/north-mini-code:free` | PASS | 1 | 7,903 | 18.1s |
| `thinkingmachines/inkling:free` | PASS | 1 | 11,664 | 146.9s |
| `poolside/laguna-s-2.1:free` | PASS | 1 | 15,757 | 160.4s |
| `nvidia/nemotron-3-super-120b-a12b:free` | PASS | 1 | 15,758 | 162.1s |
| `liquid/lfm-2.5-2.6b:free` | PASS | 1 | 16,781 | 177.1s |
| `minimax/minimax-m3:free` | PASS | 2 | 26,756 | 688.6s |
| `google/gemma-4-31b-it:free` | FAIL | 2 | 0 | 144.0s |

- **The 429 is per-slug and transient, not a property of "free" as a tier.** `glm-5.2:free` — which had just failed four straight attempts across two runs — passed here on attempt 1. `gemma-4-31b-it:free` failed both attempts on upstream 429 from Google AI Studio (`limit_source: upstream_provider_shared_pool`), zero tokens, zero files. Lesson: never conclude anything about a free model from a single 429 run; re-roll before judging, and expect roughly 1-in-8 of any free batch to be unavailable at any given moment. Budget a retry, keep free slugs off time-critical lanes, and keep a paid fallback.
- **Independent spot-check (not the run's own check): all 7 passing implementations are genuinely general.** Exhaustive 1..3999 round-trip = 0 failures for every one; canonical forms correct; all 7 rejected 14/14 adversarial malformed numerals the check never tested (IL, IC, XD, VX, IXI, MMMM, CMCM, VIV, IVI, XXXX, lowercase, whitespace-padded). No hardcoding to the check's inputs anywhere. 74-99 LOC each.
- `cohere/north-mini-code:free` — standout: fastest by 3.5x (18.1s, 7,903 tokens) and fully correct. Worth a real exploration slot on code tasks.
- `liquid/lfm-2.5-2.6b:free` — a 2.6B model passing a strict-validation task first try (177s) is well above what the "small/flash-class models choke" note would predict. That note is about long conversational/multi-turn harness tasks; short mechanical single-shot tasks are apparently fine.
- `nvidia/nemotron-3-super-120b-a12b:free` — **re-audition PASSED.** Its 2026-07-06 audition failed on a 2,650-line structured code review, with the note "if it gets another slot, try a shorter, more mechanical task first." That was the right call: on a short mechanical task it passed first try at 15,758 tokens. Promote off the do-not-retry list for mechanical work; the earlier failure was task-shape mismatch, not incapacity.
- `minimax/minimax-m3:free` — only model to need a retry: attempt 1 hit the 420s wall (SIGTERM), attempt 2 passed at 26,756 tokens. Correct but slow; give it a generous timeout or don't bother.
- Orchestrator note: my independent probe initially errored on nemotron's module because it named its functions `int_to_roman`/`roman_to_int` rather than `encode`/`decode`. The spec only ever specified the *CLI* contract, which it honors exactly — a good reminder that checks should verify what must be TRUE, not the shape the orchestrator imagined.

## OpenRouter free-model research bakeoff (2026-08-28)
Component check first: a one-task opencode probe on `z-ai/glm-5.2:free` hit an upstream 429 (same shared-pool failure mode as 2026-08-26), re-rolled onto `nvidia/nemotron-3-super-120b-a12b:free` and passed clean attempt 1 (10,822 tokens, 18.8s) — confirms the opencode↔OpenRouter path, the bwrap sandbox write confinement, and the check/retry pipeline are all intact after the machine transfer.

Then a real 5-way research bakeoff, task_type=research, identical prompt ("which free OpenRouter models are most reliable for long-context tool-using agentic work in a headless CLI harness"), each cell graded on citations + Accessed dates + a ranked top-3 + a `worker.log` grep confirming the manifest model actually ran:

| slug | verdict | attempts | tokens | elapsed | notes |
|---|---|---|---|---|---|
| `z-ai/glm-5.2:free` | FAIL | 2 | 0 | 61.6s | upstream 429 both attempts, zero tokens — same Decart shared-pool failure as the probe above, not a capability result |
| `nvidia/nemotron-3-super-120b-a12b:free` | PASS | 1 | 89,403 | 727.2s | wrote a python scraper to hit openrouter.ai/models, the scraper's own regex found "0 free models," and the report's actual top-3 (mistral-7b-instruct:free 33K ctx, gemma-2-9b-it:free 8K ctx) reads as generic/low-effort filler next to the other two passing entries — small context windows are a poor fit for the "long-context" ask it was answering. Expensive and slow relative to its peers for the same task. Passed the executed check (structure + citations were present) but this is a quality gap the check can't see; don't treat this PASS as evidence of strong research quality from this model.
| `minimax/minimax-m3:free` | PASS | 1 | 20,557 | 43.0s | best entrant by a wide margin — cited `openrouter.ai/collections/free-models` plus individual model pages, reported real per-model caveats (Poolside's free-tier train-on-your-data notice, its own non-free endpoint's tool-support gap), calibrated its own Limitations section around exactly which fetches failed. Also the fastest and cheapest of the three passes. Reverses the 2026-08-26 "slow, needs generous timeout" note for this task type — that note came from a single retry-needed run; on this task it was fastest of the batch. Keep both data points: still budget slack on timeout, but stop assuming it's the slow option by default.
| `google/gemma-4-31b-it:free` | FAIL | 2 | 0 | 144.9s | upstream 429 both attempts (Google AI Studio shared pool) — third time this exact slug has failed on availability, not capability, across two different runs now. Free-tier Gemma on Google's shared pool looks like a recurring coin-flip rather than a one-off; still not disqualifying (never conclude from failures alone), but don't spend a real deadline on it without a paid fallback.
| `inclusionai/ling-3.0-flash-fin:free` | PASS | 2 | 139,682 | 169.2s | **exploration slot, first outing for this slug.** Needed one retry but the passing attempt was strong: cited OpenRouter's actual rate-limit docs (20 RPM, 50/1000 RPD tiers) in addition to model pages, and its top-3 independently converged with MiniMax-M3's on two of three picks (`nvidia/nemotron-3-ultra-550b-a55b:free`, `cohere/north-mini-code:free`). Promote from untested to probation for research; the token count is high (139K) for a report task, worth a second data point before trusting it on anything cost-sensitive. |

**Headline finding, cross-checked by two independent models that don't share an evidence trail:** both MiniMax-M3 and Ling-3.0-Flash-Fin (unprompted, unaware of each other) named `nvidia/nemotron-3-ultra-550b-a55b:free` and `cohere/north-mini-code:free` as top picks for agentic CLI work — the latter specifically because Cohere's own model-page copy names OpenCode/SWE-Agent by name. Neither of those two models has been auditioned in this harness yet; they're reasonable next exploration-slot candidates. Meanwhile Nemotron-3-Super's self-assessment of the same question was the weakest of the three passing entries — a reminder that a model passing its own executed check says nothing about whether its research judgment was any good; that still needs a human or a second model to read the actual report.

## nvidia/nemotron-3-ultra-550b-a55b:free — audition (2026-08-29, Windows multi-instance opencode design)
- **PASS on attempt 1**, task_type=research, 137,919 tokens, 2217s (~37 min) — expensive and slow, but this was a genuinely hard task (design + build a real executable proof of opencode agent-to-provider routing, not just write prose). First outing for this slug in this harness; promote to probation.
- The audition itself: design and prove a way to run 3 concurrent `opencode` instances on Windows 11, each bound via a distinct agent to a different LAN llama.cpp/ollama provider/model, each isolated to its own `C:\temp\modelN` directory — the user's real use case for spreading instances across home-LAN inference servers. Proof had to run on Linux against local HTTP stubs standing in for the real LAN servers, using the real installed opencode binary.
- Quality was high and, importantly, self-verifying rather than self-declared: `proof-result.json`'s `hit_port`/`overlap_confirmed`/`directories_isolated` fields are computed in `proof.py` from real recorded stub-server hits and real subprocess start/end timestamps (verified by reading the script — no hardcoded `True`s). All 3 instances actually got killed with `-15` (SIGTERM) because the naive stub responses caused opencode to loop — the model caught this itself and documented it as a named Limitation, and the routing evidence was already captured server-side before the kill, so the FAIL-shaped SIGTERM didn't invalidate the PASS.
- Crucially, it created its agents with `--mode primary` explicitly (see gotcha below) — the one thing that separated it from `cohere/north-mini-code:free`'s failure on the identical task.
- Correctly used `--title` on every `opencode run` invocation per a gotcha fed into the spec (see harness note below) to avoid an unrelated auto-title-generation call polluting its routing proof.
- Deliverables (`report.md`, `launch.ps1`) are genuinely usable as a starting point for the user's real Windows deployment, not just audition busywork — `launch.ps1` uses `Start-Job` for real concurrency, is idempotent on agent re-creation, and self-verifies overlap and directory isolation at the end.

## cohere/north-mini-code:free — audition (2026-08-29, same task) and a separate harness bug
- **Run 1** (before a check-design bug was fixed, see harness note below): attempt 1 FAIL on an upstream Cohere 400 — `"invalid request: all elements in tool_results must have the 'outputs' property specified"` — a real OpenCode↔Cohere tool-calling format incompatibility, not availability. Did not recur on the re-run, so may be intermittent/pattern-dependent rather than universal; worth watching for on any future Cohere-via-OpenCode task that uses tool calls.
- **Run 2** (clean re-audition under the fixed check): **FAIL x2, task_type=research**, 76,738 tokens, 382s. Root cause was NOT availability or the Cohere API bug — it created its 3 opencode agents WITHOUT `--mode primary` (defaulting to subagent), then never diagnosed why every single stub server showed `hit_port: null` in its own `proof-result.json` before running out of attempts. It burned both attempts on the stub/proof mechanics and never got around to writing `report.md` or `launch.ps1` at all. This is a genuine capability/diligence gap on this task, not a harness artifact — treat this FAIL as real signal. Don't re-audition on a task this ambitious without a lower-stakes probe first.
- Interesting incidental finding from its logs: when a subagent name is passed to `--agent`, opencode's fallback response literally identifies itself as model `big-pickle` (`opencode/big-pickle`) — apparently an internal default/demo model — which is how it became obvious (in hindsight) that the routing had silently gone to the wrong place.

## opencode agent semantics — important gotcha for the user's real deployment (2026-08-29)
`opencode agent create` defaults to `--mode subagent` unless `--mode primary` (or `all`) is passed explicitly. `opencode run --agent <name>` does **not** error when given a subagent's name — it silently falls back to the default agent/model instead. For the user's actual plan (routing N opencode instances to N different LAN llama.cpp/ollama servers via per-instance agents), forgetting `--mode primary` on agent creation would cause every instance to silently ignore its intended LAN server and hit whatever the default model is, with no error printed. Always pass `--mode primary` explicitly when creating agents meant to be selected via `opencode run --agent`.

## Harness note: Ringer's CHECK_TIMEOUT_S (60s) vs. a check that re-executes real opencode calls
First run of the Windows-audition manifest above used a check script that re-ran the worker's `proof.py` itself to verify it — but `proof.py` needed to spawn real `opencode` subprocesses, which have enough cold-start latency (plus the auto-title-generation gotcha above) that the check blew past Ringer's hardcoded `CHECK_TIMEOUT_S = 60` (module constant in `ringer.py`, not manifest-configurable) and got killed mid-verification, producing a false FAIL for `cohere/north-mini-code:free`'s attempt 1 that had actually exited rc=0. Fix: never have a check command re-execute an expensive multi-subprocess proof. Instead, require the WORKER to run the expensive proof themselves during their own (much longer) `timeout_s` budget, redirect its output to a log file, and have it also emit structured JSON evidence (e.g. `proof-result.json` with per-instance expected-vs-actual routing, an `overlap_confirmed` bool, etc.); the check then only needs to fast-parse that JSON and grep the log for a success marker — both near-instant. This is a general pattern for any future audition whose proof needs real subprocess/network round-trips.
