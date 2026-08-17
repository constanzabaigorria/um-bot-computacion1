"""
Funciones de evaluación puras e independientes entre sí. Cada una recibe un
SnakeState (ver strategy/snake_adapter.py) y una dirección candidata, y
devuelve un número: más alto = mejor para nosotros.

Fase A: solo `espacio_libre` estaba activa.
Fase B: se suman `distancia_comida` y `territorio` (Voronoi vs. rival).
`agresion` queda apagada por la filosofía "balanceada" del plan,
disponible como flag en config.py para probar más adelante.
"""

import random
from collections import deque

import config
from strategy import snake_adapter as sa


def flood_fill(state: sa.SnakeState, start: tuple, blocked: set) -> int:
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


def bfs_distances(state: sa.SnakeState, start: tuple, blocked: set) -> dict:
    """
    BFS desde `start`, devuelve {celda: distancia_en_pasos} para todas las
    celdas alcanzables sin cruzar `blocked`. Usado tanto por
    distancia_comida como por territorio (Voronoi).
    """
    if not sa.in_bounds(state, start) or start in blocked:
        return {}

    dist = {start: 0}
    q = deque([start])
    while q:
        cell = q.popleft()
        for d in sa.DIRECTIONS:
            nxt = sa.next_cell(cell, d)
            if nxt in dist:
                continue
            if not sa.in_bounds(state, nxt) or nxt in blocked:
                continue
            dist[nxt] = dist[cell] + 1
            q.append(nxt)
    return dist


def espacio_libre(state: sa.SnakeState, direction: str) -> float:
    new_head = sa.next_cell(state.my_head, direction)
    blocked = (state.my_body | state.opp_body) - {state.my_head}
    reachable = flood_fill(state, new_head, blocked)
    total_cells = max(state.rows * state.cols, 1)
    return reachable / total_cells


def distancia_comida(state: sa.SnakeState, direction: str) -> float:
    if not state.food:
        return 0.0

    new_head = sa.next_cell(state.my_head, direction)
    blocked = (state.my_body | state.opp_body) - {state.my_head}
    dist = bfs_distances(state, new_head, blocked)

    reachable_food_dist = [d for cell, d in dist.items() if cell in state.food]
    if not reachable_food_dist:
        return 0.0

    return 1.0 / (1.0 + min(reachable_food_dist))


def territorio(state: sa.SnakeState, direction: str) -> float:
    """
    Voronoi vs. rival: de las celdas del tablero, cuántas alcanzo yo
    estrictamente antes que el rival, partiendo de la celda a la que
    iríamos con `direction`. Si no hay rival en el tablero (o el
    movimiento choca), maneja esos casos límite sin explotar.
    """
    new_head = sa.next_cell(state.my_head, direction)

    my_blocked = (state.my_body | state.opp_body) - {state.my_head}
    my_dist = bfs_distances(state, new_head, my_blocked)
    if not my_dist:
        return 0.0

    total_cells = max(state.rows * state.cols, 1)

    if state.opp_head is None:
        return len(my_dist) / total_cells

    opp_blocked = (state.my_body | state.opp_body) - {state.opp_head}
    opp_dist = bfs_distances(state, state.opp_head, opp_blocked)

    mine = 0
    for cell, d in my_dist.items():
        opp_d = opp_dist.get(cell)
        if opp_d is None or d < opp_d:
            mine += 1

    return mine / total_cells


def agresion(state: sa.SnakeState, direction: str) -> float:
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
    candidates = sa.generate_moves(state)
    scored = [(evaluate(state, d), d) for d in candidates]
    best_score = max(s for s, _ in scored)
    best = [d for s, d in scored if s == best_score]
    return random.choice(best)