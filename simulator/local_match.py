"""
Simulador local: corre una partida completa de Snake entre dos "bots" en
memoria, sin websocket, turno a turno, hasta game over o hasta agotar
remaining_moves. Guarda el log con el mismo formato de eventos/acciones
que game_<id>.log, para poder revisar jugada por jugada qué salió mal sin
gastar partidas reales ni rate limit del server.

Principio de diseño: reusa exactamente el mismo camino que run.py usa en
producción -- arma un turn_data igual al que manda el server, lo pasa por
strategy.snake_adapter.parse_state y strategy.heuristics.choose_direction.
Así lo que se prueba acá es literalmente lo mismo que corre en una
partida real, no una reimplementación paralela que podría divergir.
"""

import json
import random
from pathlib import Path

from strategy.heuristics import choose_direction
from strategy.snake_adapter import (
    generate_moves,
    in_bounds,
    next_cell,
    parse_state,
)

# --- Reglas de scoring (ver Snake - How to play) --------------------------
FOOD_SCORE = 100
SURVIVE_SCORE = 1
CRASH_PENALTY = -500
OPPONENT_WIN_BONUS = 1000

LOG_DIR = Path("logs")


def random_safe_bot(state):
    """
    Bot "tonto" de referencia para probar contra algo que no sea uno
    mismo: entre los movimientos que no chocan de forma inmediata, elige
    uno al azar (sin buscar comida ni territorio). Vive acá porque el
    simulador es lo que hace posible probarlo sin gastar partidas reales
    (el tuning real contra este oponente es Fase E).
    """
    return random.choice(generate_moves(state))


class LocalMatch:
    """
    Estado mutable de una partida local. rows/cols siguen el mismo
    sistema de coordenadas que snake_adapter (fila, columna), fila 0
    arriba.
    """

    def __init__(self, rows=None, cols=None, max_moves=300, food_count=1):
        import config

        self.rows = rows or config.DEFAULT_BOARD_SIZE
        self.cols = cols or config.DEFAULT_BOARD_SIZE
        self.max_moves = max_moves
        self.food_count = food_count

        # TODO: confirmar contra el server real la longitud/posicion
        # inicial exacta de las serpientes. Aca arrancamos con largo 1
        # (solo cabeza), separadas en extremos opuestos del tablero, como
        # aproximacion razonable mientras no este confirmado.
        mid_row = self.rows // 2
        self.snakes = {
            "A": [(mid_row, 1)],
            "B": [(mid_row, self.cols - 2)],
        }
        self.alive = {"A": True, "B": True}
        self.score = {"A": 0, "B": 0}
        self.food = set()
        self._spawn_food()

        self.moves_played = 0
        self.game_id = f"local_{random.randint(0, 999999)}"
        self.history = []  # lineas de log, formato "< {...}" / "> {...}"

    # --- Rendering del tablero, igual al formato del server -------------

    def render_board(self) -> str:
        grid = [[" "] * self.cols for _ in range(self.rows)]

        for side, body in self.snakes.items():
            if not self.alive[side]:
                continue
            head_char = side           # 'A' / 'B'
            body_char = side.lower()   # 'a' / 'b'
            for i, (r, c) in enumerate(body):
                grid[r][c] = head_char if i == 0 else body_char

        for r, c in self.food:
            if grid[r][c] == " ":
                grid[r][c] = "*"

        return "\n".join("|" + "".join(row) + "|" for row in grid)

    def _spawn_food(self):
        occupied = {cell for body in self.snakes.values() for cell in body}
        occupied |= self.food
        empty_cells = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in occupied
        ]
        needed = self.food_count - len(self.food)
        if needed > 0 and empty_cells:
            self.food.update(random.sample(empty_cells, min(needed, len(empty_cells))))

    # --- Un turno de un jugador ------------------------------------------

    def _turn_data(self, side: str) -> dict:
        return {
            "board": self.render_board(),
            "rows": self.rows,
            "cols": self.cols,
            "side": side,
            "player_1": "A",
            "player_2": "B",
            "score_1": self.score["A"],
            "score_2": self.score["B"],
            "remaining_moves": self.max_moves - self.moves_played,
            "game_id": self.game_id,
            "turn_token": f"t_{self.moves_played}",
        }

    def _log(self, prefix: str, payload: dict):
        self.history.append(prefix + json.dumps(payload))

    def play_turn(self, side: str, bot) -> bool:
        """
        Juega un turno del jugador `side` usando `bot` (una funcion
        state -> direction, tipicamente strategy.heuristics.choose_direction
        o random_safe_bot). Devuelve True si el jugador sigue vivo despues
        del turno.
        """
        if not self.alive[side]:
            return False

        opponent = "B" if side == "A" else "A"
        turn_data = self._turn_data(side)
        self._log("< ", {"event": "your_turn", "data": turn_data})

        state = parse_state(turn_data)
        direction = bot(state)

        self._log(
            "> ",
            {
                "action": "move",
                "data": {
                    "game_id": self.game_id,
                    "turn_token": turn_data["turn_token"],
                    "direction": direction,
                },
            },
        )

        head = self.snakes[side][0]
        new_head = next_cell(head, direction)

        crashed = (
            not in_bounds(state, new_head)
            or new_head in self.snakes[side]
            or new_head in self.snakes[opponent]
        )

        if crashed:
            self.alive[side] = False
            self.score[side] += CRASH_PENALTY
            if self.alive[opponent]:
                self.score[opponent] += OPPONENT_WIN_BONUS
            return False

        ate_food = new_head in self.food
        self.snakes[side].insert(0, new_head)
        if ate_food:
            self.food.discard(new_head)
            self.score[side] += FOOD_SCORE
            self._spawn_food()
        else:
            self.snakes[side].pop()

        self.score[side] += SURVIVE_SCORE
        return True

    # --- Loop completo -----------------------------------------------------

    def run(self, bot_a=choose_direction, bot_b=choose_direction) -> dict:
        bots = {"A": bot_a, "B": bot_b}

        while (
            self.moves_played < self.max_moves
            and self.alive["A"]
            and self.alive["B"]
        ):
            for side in ("A", "B"):
                if not self.alive[side]:
                    break
                self.play_turn(side, bots[side])
                if not (self.alive["A"] and self.alive["B"]):
                    break
            self.moves_played += 1

        if self.alive["A"] and self.alive["B"]:
            # se acabaron los movimientos sin que nadie choque: gana el
            # de mayor puntaje (ver "Snake - How to play")
            winner = "A" if self.score["A"] >= self.score["B"] else "B"
        elif self.alive["A"]:
            winner = "A"
        elif self.alive["B"]:
            winner = "B"
        else:
            # colision mutua en el mismo turno: desempata por puntaje
            winner = "A" if self.score["A"] >= self.score["B"] else "B"

        result = {
            "winner": winner,
            "score_a": self.score["A"],
            "score_b": self.score["B"],
            "moves_played": self.moves_played,
            "game_id": self.game_id,
        }

        self._log("< ", {"event": "game_over", "data": result})
        self._write_log()
        return result

    def _write_log(self):
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            path = LOG_DIR / f"game_{self.game_id}.log"
            path.write_text("\n".join(self.history) + "\n")
        except OSError as e:
            print(f"could not write local match log: {e}")


def play_local_match(bot_a=choose_direction, bot_b=choose_direction, **kwargs) -> dict:
    """Punto de entrada simple: una partida, devuelve el resultado."""
    match = LocalMatch(**kwargs)
    return match.run(bot_a=bot_a, bot_b=bot_b)


if __name__ == "__main__":
    # Uso rápido: correr N partidas de nuestro bot contra sí mismo (o
    # contra random_safe_bot) e imprimir el % de victorias.
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    opponent = random_safe_bot if "--vs-random" in sys.argv else choose_direction
    wins_a = 0

    for i in range(n):
        result = play_local_match(bot_a=choose_direction, bot_b=opponent)
        if result["winner"] == "A":
            wins_a += 1
        print(
            f"match {i + 1}/{n}: winner={result['winner']} "
            f"score_a={result['score_a']} score_b={result['score_b']} "
            f"moves={result['moves_played']}"
        )

    print(f"\nA ganó {wins_a}/{n} partidas ({100 * wins_a / n:.1f}%)")