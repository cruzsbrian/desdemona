from typing import Dict, Optional

import json
import coolname
import eventlet
import socketio

from desdemona import messages, othello


class Game:
    match_code: str
    board: othello.Board
    player: Dict[othello.Color, str] = {
        othello.Color.BLACK : None,
        othello.Color.WHITE : None,
    }

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


def update_player(game: Game, color: othello.Color, move: othello.Move):
    """
    Send update of a game to a player.
    """
    print(f"Sending game update for {game.match_code} to {game.player[color]} ({color.value})")

    sio.emit("game_update", messages.GameMessage(
        messages.Status.PLAYING,
        None,
        move,
        None,
        None,
        None,
    ).to_json(), to=game.player[color])


@sio.event
def connect(sid, environ):
    print("SERVER: connected to", sid)


@sio.event
def disconnect(sid):
    print("SERVER: disconnected from", sid)


@sio.event
def create_game(sid):
    """
    Create a new game, and return the corresponding match code to the requester.
    """
    # NOTE: this may yield a name collision after ~300K games without server restart
    game_code = coolname.generate_slug(2)

    game = Game(game_code)
    all_games[game_code] = game

    sio.emit("get_game_code", game_code, to=sid)


@sio.event
def register_player(sid, msg_json):
    """
    Register a client as a player in game, updating player_games and the player
    dict in the game object.
    """
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

    if game.player[msg.color]:
        return #TODO handle duplicate registration

    game.player[msg.color] = sid

    if game.player[othello.Color.WHITE] and game.player[othello.Color.BLACK]:
        print("Starting game")
        update_player(game, othello.Color.BLACK, None)


@sio.event
def make_move(sid, msg_json):
    """
    Receive a move from a player, update the game, and update the other player.
    """
    game = player_games[sid]

    if sid == game.player[othello.Color.BLACK]:
        color = othello.Color.BLACK
    else:
        color = othello.Color.WHITE

    msg = messages.MoveMessage.from_json(msg_json)
    move = msg.move

    print(f"Match {game.match_code}: {color.value} plays {move}")

    #TODO update the board and figure out if game is over

    update_player(game, color.opp(), move)


def run():
    eventlet.wsgi.server(eventlet.listen(("localhost", 8765)), app)
