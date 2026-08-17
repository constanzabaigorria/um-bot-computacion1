"""
Toda constante tuneable del bot vive acá. Nada de numeros magicos sueltos
en heuristics.py / search.py / snake_adapter.py.
"""

# --- Pesos de evaluate() (Fase B en adelante) ---------------------------
# evaluate(state) = w1*espacio + w2*comida + w3*territorio + w4*agresion
WEIGHTS = {
    "espacio": 1.0,      # flood-fill: no autoencerrarse (prioridad alta)
    "comida": 0.5,       # BFS a la comida mas cercana (prioridad media-alta)
    "territorio": 0.0,   # Voronoi vs. rival (Fase B, arranca en 0 -> desactivado)
    "agresion": 0.0,     # reduce el espacio del rival (Fase B, flag off por filosofia balanceada)
}

# --- Feature flags --------------------------------------------------------
FEATURES = {
    "comida_enabled": False,       # se prende en Fase B (Fase A = solo espacio_libre, "lo que ya teniamos")
    "territorio_enabled": False,   # se prende en Fase B
    "agresion_enabled": False,     # queda para probar mas adelante, no forma parte del plan base
    "minimax_enabled": False,      # se prende en Fase D
}

# --- Búsqueda adversarial (Fase D) ----------------------------------------
# Presupuesto de tiempo por movimiento para iterative deepening.
# TODO(Fase D / seccion "3. Cosas a confirmar"): medir empiricamente el
# limite real del server y ajustar con margen de seguridad.
TIME_BUDGET_MS = 300
MAX_SEARCH_DEPTH = 6

# --- Tablero ----------------------------------------------------------
# TODO: confirmar si el tablero siempre es 15x15 o varia por partida.
DEFAULT_BOARD_SIZE = 15