from strategy.snake_adapter import generate_moves, parse_state


def make_turn_data(board_lines, side="A"):
    board = "\n".join(f"|{line}|" for line in board_lines)
    return {
        "board": board,
        "side": side,
        "rows": len(board_lines),
        "cols": len(board_lines[0]),
    }


def test_parse_state_finds_heads_bodies_and_food():
    board_lines = [
        "     ",
        " aA  ",
        "  *  ",
        "  Bb ",
        "     ",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))

    assert state.rows == 5
    assert state.cols == 5
    assert state.my_symbol == "A"
    assert state.opp_symbol == "B"
    assert state.my_head == (1, 2)
    assert (1, 1) in state.my_body
    assert state.opp_head == (3, 2)
    assert (3, 3) in state.opp_body
    assert (2, 2) in state.food


def test_generate_moves_avoids_wall_and_body():
    board_lines = [
        "a    ",
        "A    ",
        "     ",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))
    moves = set(generate_moves(state))

    assert "up" not in moves
    assert "left" not in moves
    assert "down" in moves
    assert "right" in moves


def test_generate_moves_returns_something_even_if_trapped():
    board_lines = [
        "aaa",
        "aAa",
        "aaa",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))
    moves = generate_moves(state)

    assert len(moves) == 4
    assert set(moves) == {"up", "down", "left", "right"}
    