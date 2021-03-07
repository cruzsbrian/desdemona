from typing import Dict, Optional

import json
import coolname
import eventlet
import socketio

from desdemona import messages, othello


class Game:
    match_code: str
    board: othello.Board
    black_sid: Optional[str] = None
    white_sid: Optional[str] = None

    def __init__(self, match_code):
        self.match_code = match_code
        # TODO: initialize board


# Map from connection sids to games
player_games: Dict[str, Game] = {}

# Map from match codes to games
all_games: Dict[str, Game] = {}


# Server code
sio = socketio.Server()
app = socketio.WSGIApp(sio)


def update_player(sid: str, game: Game, move: othello.Move):
    print(f"Sending game update for {game.match_code} to {sid}")

    sio.emit("game_update", messages.GameMessage(
        messages.Status.PLAYING,
        None,
        move,
        None,
        None,
        None,
    ).to_json(), to=sid)


@sio.event
def connect(sid, environ):
    print("SERVER: connected to", sid)


@sio.event
def disconnect(sid):
    print("SERVER: disconnected from", sid)


@sio.event
def create_game(sid):
    # NOTE: this may yield a name collision after ~300K games without server restart
    game_code = coolname.generate_slug(2)

    game = Game(game_code)
    all_games[game_code] = game

    sio.emit("get_game_code", game_code, to=sid)


@sio.event
def register_player(sid, msg_json):
    try:
        msg = messages.RegisterMessage.from_json(msg_json)
    except json.decoder.JSONDecodeError:
        return  # TODO: handle

    try:
        game = all_games[msg.match_code]
    except KeyError:
        return  # TODO: handle

    print(f"Registering player {sid} as {msg.color.value} in match {msg.match_code}")

    player_games[sid] = game

    if msg.color == othello.Color.WHITE:
        game.white_sid = sid
    else:
        game.black_sid = sid

    if game.white_sid and game.black_sid:
        print("Starting game")
        update_player(game.black_sid, game, None)


@sio.event
def make_move(sid, msg_json):
    game = player_games[sid]

    color = othello.Color.BLACK if sid == game.black_sid else othello.Color.WHITE

    msg = messages.MoveMessage.from_json(msg_json)
    move = msg.move

    print(f"Match {game.match_code}: {color.value} plays {move}")

    #TODO update the board and figure out if game is over

    next_player = game.white_sid if color == othello.Color.BLACK else game.black_sid
    update_player(next_player, game, move)


def run():
    eventlet.wsgi.server(eventlet.listen(("localhost", 8765)), app)
