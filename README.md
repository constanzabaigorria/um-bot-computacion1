# um-bot-computacion1

Bot de **Constanza Baigorria** para [The Code Challenge](https://codechallenge.up.railway.app):
un bot que juega **Snake** (dos jugadores, por turnos) contra otros bots vía websocket.

Basado en el cliente de referencia del profesor
([`codechallenge-test-client`](https://github.com/thecodechallenge/codechallenge-test-client)),
que aporta la conexión websocket, el manejo de eventos y el logging de partidas.
La estrategia de juego (todo lo que decide *qué movimiento hacer*) es propia.

## Filosofía del bot

- **Balanceada**: nunca arriesgar la supervivencia por comida, pero
  buscarla activamente.
- Se asume que los rivales son sofisticados → el bot evoluciona hacia
  búsqueda adversarial (minimax) en vez de quedarse en heurísticas puras.
- Snake acá es *turn-based* (no tiempo real), así que se puede hacer
  minimax de verdad, como en tres-en-raya.

Ver `CHANGELOG.md` para el detalle de qué se agregó en cada fase.

## Instalación y ejecución

```bash
git clone https://github.com/constanzabaigorria/um-bot-computacion1.git
cd um-bot-computacion1
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py <TU_BOT_TOKEN>
```

`<TU_BOT_TOKEN>` sale de **My Bots** en https://codechallenge.up.railway.app.

También podés usar `./start.sh <TU_BOT_TOKEN>`, que arma el entorno virtual
por vos.

El bot se conecta, acepta desafíos automáticamente y juega usando la
estrategia de `strategy/`. Al terminar una partida escribe
`game_<game_id>.log` con todos los eventos/acciones, útil para revisar qué
pasó jugada por jugada.

## Arquitectura

```
um-bot-computacion1/
├── run.py                   # cliente websocket — sin lógica de juego
├── config.py                # pesos, presupuesto de tiempo, todo tuneable en un lugar
├── strategy/
│   ├── search.py            # minimax + alfa-beta + iterative deepening — game-agnostic (Fase D)
│   ├── heuristics.py        # funciones de evaluación puras, independientes
│   └── snake_adapter.py     # adapta Snake al motor de búsqueda genérico
├── simulator/
│   └── local_match.py       # dos bots jugando entre sí sin red, para testear rápido (Fase C)
├── tests/
└── requirements.txt / start.sh / .github/workflows/tests.yml / CHANGELOG.md
```

**Principio rector:** `search.py` no sabe qué es Snake. Si en un futuro
cambian de juego, se escribe un adapter nuevo y el motor de búsqueda se
reutiliza tal cual.

## Tests

```bash
pip install pytest
pytest
```

## Créditos

Cliente base websocket: [thecodechallenge/codechallenge-test-client](https://github.com/thecodechallenge/codechallenge-test-client).