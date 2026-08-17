"""
Funciones de evaluación puras e independientes entre sí. Cada una recibe un
SnakeState (ver strategy/snake_adapter.py) y una dirección candidata, y
devuelve un número: más alto = mejor para nosotros.

Fase A: solo `espacio_libre` está activa (es la lógica de seguridad que ya
teníamos funcionando con el cliente base, migrada a esta arquitectura).
Fase B: se suma `distancia_comida` (ya implementada acá, lista para
conectarse) y `territorio`. `agresion` queda apagada por la filosofía
"balanceada" del plan, disponible como flag en config.py.
"""

import random
from collections import deque

import config
from strategy import snake_adapter as sa


def flood_fill(state: sa.SnakeState, start: tuple, blocked: set) -> int:
    """
    Cuenta cuántas celdas libres son alcanzables desde `start` sin cruzar
    `blocked` (paredes son implícitas via sa.in_bounds). Usado para medir
    si un movimiento nos deja con espacio para maniobrar o nos autoencierra.
    """
    if not sa.in_bounds(state, start) or start in blocked:
        return 0

    seen = {start}
    q = deque([start])
    count = 0
    while q:
        cell = q.popleft()
        count += 1
        for d in sa.DIRECTIONS:
            nxt = sa.next_cell(cell, d)
            if nxt in seen:
                continue
            if not sa.in_bounds(state, nxt):
                continue
            if nxt in blocked:
                continue
            seen.add(nxt)
            q.append(nxt)
    return count


def espacio_libre(state: sa.SnakeState, direction: str) -> float:
    """
    Flood-fill desde la celda a la que iríamos. Cuantas más celdas libres
    alcanzables, mejor: evita que el bot se autoencierre.
    Tratamos todo el cuerpo (propio + rival, cabezas incluidas) como
    bloqueado; es una aproximación conservadora (no descuenta que la cola
    se va a mover), suficiente para Fase A.
    """
    new_head = sa.next_cell(state.my_head, direction)
    blocked = (state.my_body | state.opp_body) - {state.my_head}
    reachable = flood_fill(state, new_head, blocked)
    # normalizado 0..1 contra el tablero completo, para que sea comparable
    # con otras heurísticas cuando se sumen en Fase B.
    total_cells = max(state.rows * state.cols, 1)
    return reachable / total_cells


def distancia_comida(state: sa.SnakeState, direction: str) -> float:
    """
    (Fase B) BFS desde la celda a la que iríamos hasta la comida más
    cercana. Devuelve un score en (0, 1], más alto cuanto más cerca.
    Si no hay comida visible o no hay camino, devuelve 0.
    """
    if not state.food:
        return 0.0

    new_head = sa.next_cell(state.my_head, direction)
    blocked = (state.my_body | state.opp_body) - {state.my_head}
    if not sa.in_bounds(state, new_head) or new_head in blocked:
        return 0.0

    seen = {new_head}
    q = deque([(new_head, 0)])
    while q:
        cell, dist = q.popleft()
        if cell in state.food:
            return 1.0 / (1.0 + dist)
        for d in sa.DIRECTIONS:
            nxt = sa.next_cell(cell, d)
            if nxt in seen or not sa.in_bounds(state, nxt) or nxt in blocked:
                continue
            seen.add(nxt)
            q.append((nxt, dist + 1))
    return 0.0


def territorio(state: sa.SnakeState, direction: str) -> float:
    """(Fase B) Voronoi vs. rival. Placeholder: no implementado todavía."""
    return 0.0


def agresion(state: sa.SnakeState, direction: str) -> float:
    """(Fase B, flag off por defecto) Reduce el espacio del rival."""
    return 0.0


def evaluate(state: sa.SnakeState, direction: str) -> float:
    w = config.WEIGHTS
    score = w["espacio"] * espacio_libre(state, direction)
    if config.FEATURES["comida_enabled"]:
        score += w["comida"] * distancia_comida(state, direction)
    if config.FEATURES["territorio_enabled"]:
        score += w["territorio"] * territorio(state, direction)
    if config.FEATURES["agresion_enabled"]:
        score += w["agresion"] * agresion(state, direction)
    return score


def choose_direction(state: sa.SnakeState) -> str:
    """
    Punto de entrada que usa run.py. Filtra movimientos inmediatamente
    letales (pared/cuerpo) y elige el de mejor evaluate(), con desempate
    aleatorio para no ser 100% determinista.
    """
    candidates = sa.generate_moves(state)
    scored = [(evaluate(state, d), d) for d in candidates]
    best_score = max(s for s, _ in scored)
    best = [d for s, d in scored if s == best_score]
    return random.choice(best)