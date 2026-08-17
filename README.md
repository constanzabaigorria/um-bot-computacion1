# codechallenge-test-client

[![tests](https://github.com/thecodechallenge/codechallenge-test-client/actions/workflows/tests.yml/badge.svg)](https://github.com/thecodechallenge/codechallenge-test-client/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/thecodechallenge/codechallenge-test-client/badge.svg?branch=main)](https://coveralls.io/github/thecodechallenge/codechallenge-test-client?branch=main)

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

## Coverage

The course requires **at least 90% coverage**, measured with
[coverage.py](https://coverage.readthedocs.io/):

```bash
coverage run -m unittest discover
coverage report -m
```

The threshold lives in `.coveragerc` as `fail_under = 90`, so `coverage report`
exits non-zero on its own when coverage drops below it — you don't need to pass
`--fail-under` by hand. That file also keeps the test files out of the
measurement (`omit`) and skips the `if __name__ == '__main__':` block
(`exclude_lines`), which the tests can't reach.

This repo currently sits at **100%**.

### Coveralls

CI also publishes the report to
[Coveralls](https://coveralls.io/github/thecodechallenge/codechallenge-test-client),
which is where the badge at the top comes from and what gives you the
line-by-line diff on a pull request. `coverage` writes its own `.coverage`
binary file, so the workflow converts it first:

```bash
coverage lcov -o coverage.lcov
```

Only the Python 3.12 leg of the matrix uploads — otherwise Coveralls gets two
reports for the same commit and the numbers flap. The repo is public, so
`coverallsapp/github-action@v2` authenticates with the `GITHUB_TOKEN` it
already receives; there is no secret to configure.

Coveralls is reporting only. The build-failing threshold is still
`fail_under = 90` in `.coveragerc`.

## Complexity

Cyclomatic complexity is checked with [xenon](https://github.com/rubik/xenon),
which wraps [radon](https://radon.readthedocs.io/) and exits non-zero when a
threshold is crossed:

```bash
xenon --max-absolute B --max-modules B --max-average A run.py test_run.py
```

Three separate limits: `--max-absolute` is the worst any single function may
rank, `--max-modules` the worst any whole file may average, `--max-average` the
worst the project as a whole may average. Ranks go A (1–5) → B (6–10) → C
(11–20) → …

Today the only block above A is `play()` at **B (9)** — one `try` wrapping a
chain of `if request_data['event'] == ...` branches. The thresholds are set at
that current state, so they hold the line without demanding a refactor now. To
see the breakdown instead of a pass/fail:

```bash
radon cc run.py -s -a
```

## Continuous integration

`.github/workflows/tests.yml` runs on every push and pull request, on Python
3.9 and 3.12. It installs both requirement files, runs the suite under
`coverage run`, then `coverage report -m`, then `xenon` — so a change that drops
coverage below 90% *or* pushes a function past rank B fails the build.

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
