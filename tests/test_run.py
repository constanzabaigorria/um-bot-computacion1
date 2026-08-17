"""
Tests de humo (Fase A): confirman que el cliente arranca sin romperse y
que, dado un turno válido, arma una acción de movimiento bien formada,
sin conectarse a ningún websocket real.
"""

import asyncio
import json

import run
from tests.test_snake_adapter import make_turn_data


class FakeWebSocket:
    def __init__(self):
        self.sent = []

    async def send(self, message):
        self.sent.append(message)


def test_process_move_sends_valid_direction():
    turn_data = make_turn_data(
        ["     ", " aA  ", "     ", "     "], side="A",
    )
    turn_data["game_id"] = "g_test"
    turn_data["turn_token"] = "t_test"

    request_data = {"event": "your_turn", "data": turn_data}
    ws = FakeWebSocket()

    asyncio.run(run.process_move(ws, request_data))

    assert len(ws.sent) == 1
    sent = json.loads(ws.sent[0])
    assert sent["action"] == "move"
    assert sent["data"]["game_id"] == "g_test"
    assert sent["data"]["turn_token"] == "t_test"
    assert sent["data"]["direction"] in ("up", "down", "left", "right")