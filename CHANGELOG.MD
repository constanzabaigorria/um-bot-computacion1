# Changelog

## [v0.2.0-heuristics] — Fase B: heurísticas fuertes

- Se activa `distancia_comida` (`config.FEATURES["comida_enabled"] = True`):
  el bot ahora busca comida activamente en vez de deambular sin rumbo.
- Se implementa `territorio` (Voronoi vs. rival): BFS simultáneo desde
  nuestra cabeza y la del rival, cuenta cuántas celdas alcanzamos
  estrictamente antes que el rival. Activado
  (`config.FEATURES["territorio_enabled"] = True`) con peso 0.3.
  Nota de diseño: acercarse al rival puede *aumentar* el territorio propio
  (el punto medio del Voronoi se corre hacia el rival) — el heurístico no
  es simplemente "mantené distancia", hay que tenerlo presente al tunear
  pesos en Fase E.
- Se refactoriza `distancia_comida` para reusar el nuevo `bfs_distances`
  (mismo BFS que usa `territorio`), sacando código duplicado.
- 5 tests nuevos en `tests/test_heuristics.py` cubriendo `distancia_comida`
  y `territorio`, incluyendo casos límite (sin comida, movimiento
  bloqueado, sin rival en el tablero).
- 12/12 tests pasan.

## [v0.1.0-refactor] — Fase A: arquitectura base

- Se reemplaza la lógica de ejemplo del cliente base (Connect 4, movimiento
  random) por la arquitectura escalable definida en el plan:
  `config.py`, `strategy/heuristics.py`, `strategy/snake_adapter.py`.
- `run.py` mantiene toda la infraestructura del cliente base (conexión,
  reconexión, manejo de eventos, logging a `game_<id>.log`) y delega la
  decisión de movimiento en `strategy.heuristics.choose_direction`.
- Estrategia activa en esta fase: **solo `espacio_libre`** (flood-fill) —
  el bot elige, entre las direcciones que no chocan contra pared/cuerpo
  propio/rival, la que le deja más espacio libre alcanzable.
- `distancia_comida` y `territorio` quedan escritas en `heuristics.py`
  desde el principio pero detrás de feature flags apagados en
  `config.py`, listas para prenderse en Fase B sin tocar `search.py` ni
  `run.py`.
- Tests de humo: `tests/test_snake_adapter.py`, `tests/test_heuristics.py`,
  `tests/test_run.py` — cubren parseo del tablero, generación de
  movimientos seguros y que `process_move` arma una acción válida.
- Se agrega workflow de CI (`.github/workflows/tests.yml`) que corre
  `pytest` en cada push/PR a `main`.
- El token del bot vive en un archivo `.env` (`BOT_TOKEN=...`, ver
  `.env.example`) en vez de tipearse siempre por línea de comando.
  `.env` está en `.gitignore` para no exponerlo en el repo público.
- **Confirmado por prueba real**: el dominio del websocket vigente es
  `wss://server.codechallenge.net.ar` (coincide con la documentación
  oficial). El dominio hardcodeado en el repo base del profesor,
  `codechallenge-server.up.railway.app`, devuelve HTTP 404 — ya no está
  activo.
- Primera partida real jugada (self-play / desafío en la web): el bot no
  crasheó, terminó con puntaje positivo, y no comió (esperado — `comida`
  seguía apagada en esta fase).

## [unreleased]

- Fase C: `simulator/local_match.py` — correr partidas bot vs. bot sin
  red, para iterar rápido sin gastar rate limit del server.
- Fase D: `strategy/search.py` — minimax + poda alfa-beta + iterative
  deepening, modelando al rival con la misma `evaluate()`.
- Fase E: tuning de pesos (`config.WEIGHTS`) contra distintos oponentes
  simulados.
- Fase F: hardening pre-torneo (reconexión, manejo defensivo de eventos
  inesperados, logging para post-mortem).