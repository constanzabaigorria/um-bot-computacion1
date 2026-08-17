from strategy.heuristics import choose_direction, distancia_comida, espacio_libre, territorio
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


def test_distancia_comida_prefers_the_closer_direction():
    board_lines = [
        "      ",
        "  A  *",
        "      ",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))

    assert distancia_comida(state, "right") > distancia_comida(state, "left")


def test_distancia_comida_is_zero_when_no_food_on_board():
    board_lines = [
        "     ",
        "  A  ",
        "     ",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))

    assert distancia_comida(state, "right") == 0.0


def test_choose_direction_goes_toward_food_when_safe():
    board_lines = [
        "        ",
        "        ",
        "  A    *",
        "        ",
        "        ",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))

    direction = choose_direction(state)

    assert direction == "right"


def test_territorio_is_zero_when_move_is_immediately_blocked():
    # "up" choca contra la pared: no hay celdas alcanzables, territorio
    # tiene que ser 0, no explotar ni devolver algo raro.
    board_lines = [
        "A    ",
        "     ",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))

    assert territorio(state, "up") == 0.0


def test_territorio_is_positive_with_rival_present_and_open_board():
    # Con el rival lejos y tablero abierto, cualquier movimiento válido
    # debería asegurar al menos una porción de territorio propio.
    board_lines = [
        "          ",
        "  A      B",
        "          ",
    ]
    state = parse_state(make_turn_data(board_lines, side="A"))

    assert territorio(state, "right") > 0.0
    assert territorio(state, "down") > 0.0