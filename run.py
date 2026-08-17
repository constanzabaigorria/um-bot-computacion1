import asyncio
import json
from random import randint
import sys
import websockets
import time


# A running text log of events received / actions sent per game, written to
# game_<game_id>.log when the match ends.
HISTORY = {}


def log_event(game_id, message):
    HISTORY.setdefault(game_id, []).append('< ' + json.dumps(message))


def log_action(game_id, message):
    HISTORY.setdefault(game_id, []).append('> ' + json.dumps(message))


def write_game_log(game_id):
    try:
        with open(f"game_{game_id}.log", "w") as f:
            f.write("\n".join(HISTORY.get(game_id, [])) + "\n")
        print(f"saved game_{game_id}.log")
    except OSError as e:
        print(f"could not write game log: {e}")


async def send(websocket, action, data):
    message = json.dumps(
        {
            'action': action,
            'data': data,
        }
    )
    print(message)
    await websocket.send(message)


async def start(auth_token):
    uri = "wss://server.codechallenge.net.ar/ws?token={}".format(auth_token)
    # uri = "ws://localhost:5000/ws?token={}".format(auth_token)
    while True:
        try:
            print('connection to {}'.format(uri))
            async with websockets.connect(uri) as websocket:
                print('connection READY!')
                await play(websocket)
        except KeyboardInterrupt:
            print('Exiting...')
            break
        except Exception:
            print('connection error!')
            time.sleep(3)


async def on_game_over(websocket, request_data):
    game_id = request_data['data'].get('game_id')
    if game_id:
        log_event(game_id, request_data)
        write_game_log(game_id)


async def on_challenge(websocket, request_data):
    # if request_data['data']['opponent'] == 'favoriteopponent':
    await send(
        websocket,
        'accept_challenge',
        {
            'challenge_id': request_data['data']['challenge_id'],
        },
    )


async def on_your_turn(websocket, request_data):
    log_event(request_data['data']['game_id'], request_data)
    await process_your_turn(websocket, request_data)


# Un evento sin entrada acá se ignora, que es lo que queremos para los
# informativos ('update_user_list'). Para reaccionar a uno nuevo, escribí su
# handler y agregalo al dict — no toques play().
HANDLERS = {
    'game_over': on_game_over,
    'challenge': on_challenge,
    'your_turn': on_your_turn,
}


async def play(websocket):
    while True:
        try:
            request = await websocket.recv()
            print(f"< {request}")
            request_data = json.loads(request)
            handler = HANDLERS.get(request_data['event'])
            if handler:
                await handler(websocket, request_data)
        except KeyboardInterrupt:
            print('Exiting...')
            break
        except Exception as e:
            print('error {}'.format(str(e)))
            break  # force login again


async def process_your_turn(websocket, request_data):
    # if randint(0, 4) >= 1:
    await process_move(websocket, request_data)


async def process_move(websocket, request_data):
    # `data` también trae 'side', que este bot no mira porque juega al azar.
    board = request_data['data']['board']
    colums = board.find('|', 1) - 1
    print(board)
    move = {
        'game_id': request_data['data']['game_id'],
        'turn_token': request_data['data']['turn_token'],
        'col': randint(0, colums),
    }
    log_action(move['game_id'], {'action': 'move', 'data': move})
    await send(websocket, 'move', move)


async def process_wall(websocket, request_data):
    await send(
        websocket,
        'wall',
        {
            'game_id': request_data['data']['game_id'],
            'turn_token': request_data['data']['turn_token'],
            'row': randint(0, 8),
            'col': randint(0, 8),
            'orientation': 'h' if randint(0, 1) == 0 else 'v'
        },
    )


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        auth_token = sys.argv[1]
        asyncio.get_event_loop().run_until_complete(start(auth_token))
    else:
        print('please provide your auth_token')
