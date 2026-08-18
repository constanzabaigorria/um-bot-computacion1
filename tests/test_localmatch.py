import shutil

from strategy.heuristics import choose_direction
from strategy.snake_adapter import generate_moves
from simulator.local_match import LocalMatch, play_local_match, random_safe_bot


def test_local_match_runs_to_completion_without_crashing():
    result = play_local_match(rows=10, cols=10, max_moves=50)

    assert result["winner"] in ("A", "B")
    assert isinstance(result["score_a"], int)
    assert isinstance(result["score_b"], int)
    assert result["moves_played"] <= 50


def test_local_match_against_random_bot_runs_to_completion():
    result = play_local_match(
        bot_a=choose_direction,
        bot_b=random_safe_bot,
        rows=10,
        cols=10,
        max_moves=50,
    )

    assert result["winner"] in ("A", "B")


def test_local_match_writes_a_log_file(tmp_path, monkeypatch):
    import simulator.local_match as lm

    monkeypatch.setattr(lm, "LOG_DIR", tmp_path)

    result = play_local_match(rows=8, cols=8, max_moves=20)

    log_path = tmp_path / f"game_{result['game_id']}.log"
    assert log_path.exists()

    content = log_path.read_text()
    assert '"event": "your_turn"' in content
    assert '"action": "move"' in content
    assert '"event": "game_over"' in content


def test_random_safe_bot_only_picks_generated_moves():
    match = LocalMatch(rows=10, cols=10, max_moves=10)
    state_turn_data = match._turn_data("A")
    from strategy.snake_adapter import parse_state

    state = parse_state(state_turn_data)
    direction = random_safe_bot(state)

    assert direction in generate_moves(state)


def test_local_match_food_never_spawns_on_top_of_a_snake():
    match = LocalMatch(rows=10, cols=10, max_moves=10, food_count=3)

    occupied = {cell for body in match.snakes.values() for cell in body}
    assert match.food.isdisjoint(occupied)