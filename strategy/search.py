"""
Motor de búsqueda adversarial (minimax + poda alfa-beta + iterative
deepening). Se implementa en la Fase D del plan.

Principio rector: este módulo NO debe saber nada de Snake. Trabaja
contra una interfaz genérica (generate_moves, apply_move, is_terminal,
evaluate) que en Fase D va a exponer strategy/snake_adapter.py.

TODO(Fase D):
- minimax(state, depth, maximizing_player) con poda alfa-beta.
- iterative_deepening(state, time_budget_ms).
- Modelar al rival con la misma evaluate() que usamos nosotros.
"""