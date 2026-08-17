# codechallenge-test-client

[![tests](https://github.com/thecodechallenge/codechallenge-test-client/actions/workflows/tests.yml/badge.svg)](https://github.com/thecodechallenge/codechallenge-test-client/actions/workflows/tests.yml)
[![flake8](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/thecodechallenge/codechallenge-test-client/badge-data/lint.json&cacheSeconds=300)](https://github.com/thecodechallenge/codechallenge-test-client/actions/workflows/tests.yml)
[![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/thecodechallenge/codechallenge-test-client/badge-data/coverage.json&cacheSeconds=300)](https://htmlpreview.github.io/?https://github.com/thecodechallenge/codechallenge-test-client/blob/python-coverage-comment-action-data/htmlcov/index.html)
[![complexity](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/thecodechallenge/codechallenge-test-client/badge-data/complexity.json&cacheSeconds=300)](https://github.com/thecodechallenge/codechallenge-test-client/actions/workflows/tests.yml)

A minimal **bot client** for [The Code Challenge](https://codechallenge.net.ar).
It connects to the match server over a websocket using your bot's token,
auto-accepts challenges, and plays. Use it as a starting point (and a smoke
test) for writing your own bot.

## How it works

Your bot authenticates with its **token** (from **My Bots** on the web) and
opens a websocket to the server:

```
wss://server.codechallenge.net.ar/ws?token=<YOUR_BOT_TOKEN>   # production
ws://localhost:5000/ws?token=<YOUR_BOT_TOKEN>                          # local
```

The server then sends events and the bot replies with actions (JSON):

| Event          | The bot does…                                                        |
| -------------- | -------------------------------------------------------------------- |
| `list_users`   | nothing (just who's online)                                          |
| `challenge`    | replies `accept_challenge` with the `challenge_id`                   |
| `your_turn`    | plays a move — replies `move` with the move data + the `turn_token`  |
| `game_over`    | nothing (the match ended)                                            |

> The example move logic in `run.py` plays **Connect 4** (it picks a random
> column). That `process_your_turn` / `process_move` part is exactly where you
> put your own strategy — and where you adapt it to another game's action shape.

## Requirements

- Python 3.9+
- `websockets` (see `requirements.txt`)

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py <YOUR_BOT_TOKEN>
```

Get `<YOUR_BOT_TOKEN>` from **My Bots** in the web app. By default `run.py`
connects to the production server; switch the `uri` in `run.py` to the
`localhost` line to play against a local server.

> `start.sh` / `start_dev.sh` are convenience runners kept out of git because
> they may embed your personal token.

## Tests

`test_run.py` covers the event handling, the move replies and the game log,
using a fake websocket — nothing connects to the network.

```bash
pip install -r requirements-dev.txt
python -m unittest discover -v
```

## Lint

[flake8](https://flake8.pycqa.org/) — style plus the obvious errors (unused
imports and variables, undefined names):

```bash
flake8 .
```

**Where it's configured**

| Setting | File | Key |
| --- | --- | --- |
| Line length, ignored codes, excludes | [`setup.cfg`](setup.cfg) | `[flake8]` |
| Tool version | [`requirements-dev.txt`](requirements-dev.txt) | `flake8>=7,<8` |
| Enforced on every push | [`.github/workflows/tests.yml`](.github/workflows/tests.yml) | step `Lint` |

The values in `setup.cfg` — `max-line-length = 119`, `ignore = W503,W504` — are
copied from `codechallenge-connect4`, `-game-template` and `-grpc` on purpose,
so every repo in the course lints the same way. Because the config lives in
that file, the CI step is a bare `flake8 .` with no flags.

> Why flake8 and not [ruff](https://docs.astral.sh/ruff/), which is far faster
> and would fold in the complexity check too: consistency with the other course
> repos wins here. On a two-file repo flake8 takes well under a second, so the
> speed argument buys nothing.

## Coverage

The course requires **at least 90% coverage**, measured with
[coverage.py](https://coverage.readthedocs.io/):

```bash
coverage run -m unittest discover
coverage report -m
```

**Where it's configured**

| Setting | File | Key |
| --- | --- | --- |
| The 90% threshold | [`.coveragerc`](.coveragerc) | `[report] fail_under = 90` |
| What gets measured | [`.coveragerc`](.coveragerc) | `[run] source`, `omit` |
| Lines the tests can't reach | [`.coveragerc`](.coveragerc) | `[report] exclude_lines` |
| Tool version | [`requirements-dev.txt`](requirements-dev.txt) | `coverage>=7.10,<8` |
| Enforced on every push | [`.github/workflows/tests.yml`](.github/workflows/tests.yml) | steps `Run tests with coverage` → `Check coverage` |

The threshold lives in `.coveragerc` as `fail_under = 90`, so `coverage report`
exits non-zero on its own when coverage drops below it — you don't need to pass
`--fail-under` by hand, in CI or locally. That file also keeps the test files
out of the measurement (`omit`) and skips the `if __name__ == '__main__':`
block (`exclude_lines`), which the tests can't reach.

This repo currently sits at **100%**.

### PR comments and the HTML report

[python-coverage-comment-action](https://github.com/py-cov-action/python-coverage-comment-action)
posts (and updates) a comment on every pull request with the coverage diff,
line by line, and publishes the full browsable HTML report — the one the
coverage badge links to. It needs **no third-party account**: no Coveralls, no
Codecov, no signup, no secret.

It keeps both in an orphan `python-coverage-comment-action-data` branch. That
branch holds only generated files; never check it out to work on. This is why
the job asks for `contents: write` and `pull-requests: write`, and why
`.coveragerc` sets `relative_files = true` — the action reads the coverage data
from a different checkout, so absolute runner paths would not resolve. Only the
Python 3.12 leg of the matrix runs it, so the two legs don't overwrite each
other.

The badge itself does **not** come from this action — see [Badges](#badges).

Each run also drops the coverage table into its **GitHub Actions summary** page
via `coverage report --format=markdown`, so you can read it without opening the
logs.

All of this is reporting only. The build-failing threshold is still
`fail_under = 90` in `.coveragerc`.

## Complexity

Cyclomatic complexity is checked with [xenon](https://github.com/rubik/xenon),
which wraps [radon](https://radon.readthedocs.io/) and exits non-zero when a
threshold is crossed:

```bash
xenon --max-absolute A --max-modules A --max-average A run.py test_run.py
```

**Where it's configured**

| Setting | File | Key |
| --- | --- | --- |
| The rank thresholds | [`.github/workflows/tests.yml`](.github/workflows/tests.yml) | step `Check complexity` — the `--max-*` flags |
| Tool version | [`requirements-dev.txt`](requirements-dev.txt) | `xenon>=0.9,<1` |
| Badge generation | [`.github/workflows/tests.yml`](.github/workflows/tests.yml) | job `badges` |

Note there is **no config file** for this one: xenon takes its thresholds only
as command-line flags, so the workflow step *is* the configuration. Change the
numbers there and nowhere else.

Three separate limits: `--max-absolute` is the worst any single function may
rank, `--max-modules` the worst any whole file may average, `--max-average` the
worst the project as a whole may average. Ranks go A (1–5) → B (6–10) → C
(11–20) → …

**The whole repo is rank A**, so all three limits are set to A — nothing is
allowed to slip to B. The worst block is `play()` at A (5), which leaves room
up to 5 before anything breaks the build.

`play()` used to be B (9): one `try` wrapping a chain of
`if request_data['event'] == ...` branches. It now looks the event up in a
`HANDLERS` dict and awaits whatever it finds, which is also how you extend it —
write a handler, add it to the dict, leave `play()` alone. An event with no
entry is ignored, which is what we want for the informational ones.

To see the breakdown instead of a pass/fail:

```bash
radon cc run.py -s -a
```

The complexity badge reports the **single worst block** in the repo, not an
average — an average hides exactly the function you'd want to know about. See
[Badges](#badges).

## Badges

All three badges — flake8, coverage, complexity — are generated by the `badges`
job and served from one `badge-data` branch. Nothing is hosted by a third
party.

The job re-measures the commit, then writes one
[shields.io endpoint](https://shields.io/endpoint) file per gate:

| File | Looks like | Colour |
| --- | --- | --- |
| `lint.json` | `passing`, or `3 issues` | green / red |
| `coverage.json` | `100%` | green ≥ 95, green ≥ 90, yellow ≥ 75, red below |
| `complexity.json` | `A (5)` — the worst block | follows the rank: A green → F red |

```json
{"schemaVersion": 1, "label": "complexity", "message": "A (5)", "color": "brightgreen"}
```

The three files are force-pushed as a single orphan commit to `badge-data`, on
pushes to `main` only. Like the coverage action's branch, it holds nothing but
generated output and is rewritten every run; never check it out to work on.

Two things worth knowing if you touch this:

- **Don't point a badge at a `.svg` on `raw.githubusercontent.com`.** GitHub
  proxies README images through camo, and raw serves `.svg` as plain text, so
  it renders as a broken image. That's why every badge here goes through the
  shields endpoint, which returns a real `image/svg+xml`.
- **It has to be its own job.** `python-coverage-comment-action` runs in Docker
  as root and leaves the workspace's `.git` owned by root, so a `git commit`
  later in that same job dies with
  `could not open '.git/COMMIT_EDITMSG': Permission denied`. A separate job
  gets a clean checkout.

Badges are informational. What blocks a merge are the `Lint`, `Check coverage`
and `Check complexity` steps.

## Continuous integration

`.github/workflows/tests.yml` runs on every push and pull request, on Python
3.9 and 3.12. Three things can fail the build, and each is documented in its own
section above with the exact file and key:

| Gate | Fails when | Configured in |
| --- | --- | --- |
| [Lint](#lint) | flake8 reports anything | [`setup.cfg`](setup.cfg) |
| [Coverage](#coverage) | coverage drops below 90% | [`.coveragerc`](.coveragerc) |
| [Complexity](#complexity) | any block slips out of rank A | the `Check complexity` step itself |

On a push to `main` it then refreshes the two badge data branches.

> `requirements-dev.txt` asks for `coverage>=7.10,<8` instead of a hard pin:
> 7.15.x needs Python ≥ 3.10 and this repo still tests on 3.9.

## Game logs

When a match ends, the client writes a **`game_<game_id>.log`** in the working
directory with everything that happened: each event received (`<`) and action
sent (`>`), as JSON, ending with the `game_over` event. Useful for replaying or
debugging a match. These files are git-ignored.

```
< {"event": "your_turn", "data": {"board": "...", "game_id": "g_9f", "turn_token": "t_01", ...}}
> {"action": "move", "data": {"game_id": "g_9f", "turn_token": "t_01", "col": 3}}
...
< {"event": "game_over", "data": {"board": "...", "game_id": "g_9f", ...}}
```

## Write your own bot

You don't need this client — any websocket client works. The contract is:

1. Connect to `ws(s)://<server>/ws?token=<your bot token>`.
2. On `challenge`, send `{"action": "accept_challenge", "data": {"challenge_id": "..."}}`.
3. On `your_turn`, read `data` (board / game state, `game_id`, `turn_token`) and
   send your move: `{"action": "move", "data": { ... , "turn_token": "..." }}`.
