# Rose-All-G6

Monorepo for the ROSE racing game: `rose-game-engine` (game/scoring logic),
`rose-game-ai-group-6` (self-driving car module + reference drivers), and
`rose-game-web-ui` (browser client and proxy server).

## Planned features

1 - added visual effects: when passing through obstacles
2 - a map builder
3 - different music
4 - skins
5 - manual driving

## Code review

Reviewed the full history of this repository (`e9043ab` "created a repository
containing the AI, UI and engine of the game" through `9d0bc37` "removed
unnessessary objects", 21 commits) plus the current state of all three
projects. Grouped by severity.

### Correctness

- **The engine's test suite has been red since `4d8dd43`.** That commit
  ("modified the score system to not expect special action for special
  objects...") changed `rose/engine/score.py` so that hitting a
  burger/hotdog/pizza obstacle always clears it and always awards the bonus
  points, regardless of the action returned by the driver. `test_score.py`'s
  `MagicActionTest` (backing `TestHotdog`/`TestPizza`) and `TestBurger` were
  never updated to match — they still assert the old two-branch behavior
  (correct action ⇒ obstacle kept; any other action ⇒ player moves back and
  the obstacle is removed). The result is 11 failing tests in
  `rose-game-engine` as of this review (`pytest rose/ -q`), stable across
  every commit since. Nobody appears to have re-run the suite after that
  change landed — there's no CI to catch it (see below). Either the tests or
  the behavior need to be brought back in line with each other; right now
  the suite doesn't tell you anything true about `score.py`.

- **`rose-game-ai-group-6/rose/ai/server.py::do_POST` turns driver bugs into
  opaque 500s.** If `MyHTTPRequestHandler.drive(game_world)` raises, the
  exception is caught and logged, but `action` is never assigned — the
  following `response_data = {...action}` then raises `UnboundLocalError`,
  which is caught by the *outer* handler and returned as a generic HTTP 500
  with a Python exception message as the body. A driver bug (e.g. an
  unhandled obstacle type in a lookup dict) can't be distinguished from a
  transport failure by anything reading the response, and the car gets no
  action for that tick instead of a safe default. This is exactly the
  failure mode `g6-GAY-mobil.py`'s `REWARDS` dict was exposed to: it does a
  direct `REWARDS[obj]` lookup with no default, so any obstacle type added
  to `rose.common.obstacles.ALL` without a matching `REWARDS` entry crashes
  the driver via this path. Confirmed in practice during this session: an
  older, unrebuilt driver process without a `SAUCE` reward entry hit this
  exact chain (`KeyError` → `UnboundLocalError` → 500) as soon as a sauce
  obstacle entered its lookahead window.

- **Dead counters and dead code.** `Player.misses` and `Player.breaks`
  (`rose-game-engine/rose/engine/player.py`) are declared, reset, and
  serialized in `state()`, but nothing in `score.py` ever increments them —
  they're permanently `0` and the web UI dutifully displays that. Similarly,
  `SPECIAL_ACTIONS` in `g6-GAY-mobil.py` is defined but never read anywhere;
  the actual action-selection logic in `DriveEngine.__scan_tree` doesn't
  consult it. Both read as leftovers from an earlier design where the
  special action actually mattered (see the point above).

- **`rose-game-web-ui/public/game.js`'s info panel mislabels its own field.**
  The "Pinguins:" line (`Information.update`) displays `player.pickups`,
  which now counts burger/hotdog/pizza pickups collectively — the label
  predates (and misspells) the obstacle rename and no longer corresponds to
  anything in the game.

### Architecture / duplication

- `rose/common/obstacles.py` and its test file are maintained as two
  hand-synchronized copies, one under `rose-game-engine` and one under
  `rose-game-ai-group-6`, with no shared package or build step tying them
  together. Every obstacle-set change (there have been several: the
  vegetable rename in `12eafe7`/`674bd1b`/`cfdf54b`, the sauce feature) has
  to be applied twice by hand. So far the copies have stayed in sync, but
  nothing enforces it, and a future edit to only one side would fail purely
  by omission rather than by any error.
- Score-related constants are similarly duplicated by convention rather than
  by reference: `rose-game-engine/rose/engine/config.py` is the source of
  truth for point values, and `g6-GAY-mobil.py`'s `REWARDS` dict (plus, now,
  `SAUCE_MULTIPLIER`/`SAUCE_EFFECT_HITS`) mirrors it by hand because the AI
  package has no dependency on the engine package. Reasonable given the
  three projects ship independently, but worth a comment or shared constants
  file if the scoring model keeps growing.

### Process / repository hygiene

- **No CI.** There's no `.github/workflows` (or equivalent) anywhere in the
  repo, despite `pytest` suites in both Python projects and an `eslint`
  config in the web UI. All quality gates are manual, which is how the
  11-test regression above went unnoticed.
- **The repository is nearly half junk files.** `git ls-files | wc -l`
  currently reports 220 tracked files, of which **102** are Windows
  `*:Zone.Identifier` sidecar files (NTFS "mark of the web" metadata created
  when files are downloaded in a browser on Windows/WSL) — introduced in
  bulk by `6df3958` and `b04b342`. They carry no project value and roughly
  double the size of every diff that touches an asset. `9d0bc37` cleaned up
  four stray `.png~` editor-backup files, but more remain untouched (e.g.
  `rose-game-ai-group-6/mydriver - Copy.py:Zone.Identifier` — the sidecar
  for a copy-pasted driver file whose actual `.py` was never committed, only
  its metadata). `rose-game-web-ui/.vs/slnx.sqlite`, a Visual Studio IDE
  database file, is also currently tracked.
- **No top-level `.gitignore`.** Each subproject has its own (Python
  caches/coverage for the two Python projects, `node_modules`/build output
  for the web UI), but none of the three exclude `*:Zone.Identifier`, `*~`,
  or `.vs/`, which is how the above got committed in the first place and how
  more of the same will keep getting committed.
- Commit messages are mostly good-faith descriptions of intent ("modified
  the score system to...", "improved the soundtrack detection...") rather
  than "fix bug" placeholders, which is a genuine strength — the history is
  readable. A few merge commits (`95ddeb0`, `f3b3eef`, `8bb265a`) exist purely
  to reconcile parallel work from two contributors (`eyasu-k`/`Eyasu Kassa`
  and `gelkin`) touching the same asset files; not a problem, just a sign
  the asset-swap work wasn't coordinated ahead of time.

### Strengths worth keeping

- The engine/AI/web-ui split has a clean, obstacle-name-agnostic contract:
  adding a new obstacle type only ever requires touching `obstacles.py`,
  `score.py`, and the web UI's asset map — `track.py`, `net.py`'s track
  payload, and `game.js`'s draw loop never needed to change across any of
  the several obstacle-set overhauls in this history.
- `rose-game-engine/rose/engine/test_score.py`'s per-obstacle test-class
  pattern (`SinglePlayerTest`/`MagicActionTest`/`TurnTest` base classes,
  one thin subclass per obstacle) makes adding a new obstacle's tests a
  copy-paste-and-rename exercise rather than a redesign — this held up well
  even for a mechanic as different as the sauce buff.
- Each of the three subprojects carries its own `README.md` with concrete
  run instructions (local, containerized, and Kubernetes for the engine),
  which is more operational documentation than this top-level file had until
  now.

### Suggested next steps

1. Reconcile `score.py` and `test_score.py`'s `MagicActionTest` — decide
   whether the special-action requirement is actually gone for good, and
   either delete the "wrong action" branches from the tests or restore the
   old behavior.
2. Add a top-level `.gitignore` covering `*:Zone.Identifier`, `*~`, and
   `.vs/`, then remove the 102+ already-tracked junk files in one pass
   (`git rm --cached`).
3. Add a minimal CI workflow that runs both `pytest` suites and `eslint` on
   every push/PR — even just enough to have caught the current 11 failures.
4. Give `ai/server.py::do_POST` a safe fallback action (e.g. `actions.NONE`)
   when `.drive()` raises, instead of letting the failure surface as an
   unrelated `UnboundLocalError`.
