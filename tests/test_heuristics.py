from strategy.heuristics import choose_direction, espacio_libre
from strategy.snake_adapter import parse_state
from tests.test_snake_adapter import make_turn_data


def test_espacio_libre_prefers_open_side():
    board_lines = [
        "      ",
        "      ",
        "      ",
        "bA    ",
        "      ",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))

    score_right = espacio_libre(state, "right")
    score_left = espacio_libre(state, "left")

    assert score_right > score_left


def test_choose_direction_never_picks_a_lethal_move_if_avoidable():
    board_lines = [
        "aA   ",
        "     ",
        "     ",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))

    direction = choose_direction(state)

    assert direction in ("down", "right")


def test_choose_direction_returns_valid_direction_even_when_trapped():
    board_lines = [
        "aaa",
        "aAa",
        "aaa",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))

    direction = choose_direction(state)

    assert direction in ("up", "down", "left", "right")