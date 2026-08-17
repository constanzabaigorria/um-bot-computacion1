"""
Adapta el juego Snake (tal como lo manda el server: board como string,
side, etc.) a estructuras de datos simples que heuristics.py y, mas
adelante, search.py puedan consumir sin saber nada de strings ni de JSON.

search.py (Fase D) NO debe importar nada de acá salvo a traves de las
funciones generate_moves / apply_move / is_terminal que se agregan en esa
fase. Por ahora (Fase A/B) heuristics.py usa directamente parse_state y
generate_moves.
"""

from dataclasses import dataclass, field

DIRECTIONS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


@dataclass
class SnakeState:
    grid: list          # list[str], una fila del tablero por elemento (sin los '|')
    rows: int
    cols: int
    my_symbol: str       # 'A' o 'B' (mayuscula = cabeza)
    opp_symbol: str
    my_head: tuple
    opp_head: tuple
    my_body: set = field(default_factory=set)   # incluye la cabeza
    opp_body: set = field(default_factory=set)  # incluye la cabeza
    food: set = field(default_factory=set)


def _strip_pipes(line: str) -> str:
    """Saca el '|' inicial y final de una fila del board, si estan."""
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return line


def parse_board(board: str, rows: int = None, cols: int = None):
    """
    board viene como filas separadas por '\\n', cada una envuelta en '|...|'.
    Devuelve una lista de strings (una por fila), ya sin los '|'.
    """
    raw_lines = [ln for ln in board.split("\n") if ln.strip() != ""]
    grid = [_strip_pipes(ln) for ln in raw_lines]

    if cols is not None:
        # normalizamos ancho por si alguna fila quedo mas corta/larga
        grid = [ln.ljust(cols)[:cols] for ln in grid]
    return grid


def parse_state(turn_data: dict) -> SnakeState:
    side = turn_data["side"]  # 'A' o 'B'
    my_symbol = side
    opp_symbol = "B" if side == "A" else "A"

    rows_hint = turn_data.get("rows")
    cols_hint = turn_data.get("cols")
    grid = parse_board(turn_data["board"], rows_hint, cols_hint)

    rows = len(grid)
    cols = max((len(r) for r in grid), default=0)

    my_body, opp_body, food = set(), set(), set()
    my_head, opp_head = None, None

    for r, line in enumerate(grid):
        for c, ch in enumerate(line):
            if ch == "*":
                food.add((r, c))
            elif ch == my_symbol:
                my_head = (r, c)
                my_body.add((r, c))
            elif ch == my_symbol.lower():
                my_body.add((r, c))
            elif ch == opp_symbol:
                opp_head = (r, c)
                opp_body.add((r, c))
            elif ch == opp_symbol.lower():
                opp_body.add((r, c))

    return SnakeState(
        grid=grid, rows=rows, cols=cols,
        my_symbol=my_symbol, opp_symbol=opp_symbol,
        my_head=my_head, opp_head=opp_head,
        my_body=my_body, opp_body=opp_body, food=food,
    )


def in_bounds(state: SnakeState, cell: tuple) -> bool:
    r, c = cell
    return 0 <= r < state.rows and 0 <= c < state.cols


def is_occupied(state: SnakeState, cell: tuple) -> bool:
    """True si hay pared, cuerpo propio o del rival en esa celda."""
    if not in_bounds(state, cell):
        return True
    return cell in state.my_body or cell in state.opp_body


def next_cell(head: tuple, direction: str) -> tuple:
    dr, dc = DIRECTIONS[direction]
    return (head[0] + dr, head[1] + dc)


def generate_moves(state: SnakeState, head: tuple = None):
    """
    Todas las direcciones posibles desde `head` (default: nuestra cabeza)
    que no chocan de forma inmediata contra pared o cuerpo. Si ninguna es
    segura, devuelve las 4 igual (vamos a perder, pero hay que mandar algo).
    """
    if head is None:
        head = state.my_head

    safe = [
        d for d in DIRECTIONS
        if not is_occupied(state, next_cell(head, d))
    ]
    return safe if safe else list(DIRECTIONS.keys())