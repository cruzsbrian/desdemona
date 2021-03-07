from typing import Optional

import json
import coolname
import eventlet
import socketio

from desdemona import messages, othello


class Game:
    match_code: str
    board: othello.Board = othello.Board()
    players: dict[othello.Color, str] = {
        othello.Color.BLACK : None,
        othello.Color.WHITE : None,
    }

    def __init__(self, match_code):
        self.match_code = match_code
        # TODO: initialize board


# Map from connection sids to games
client_games: dict[str, Game] = {}

# Map from match codes to games
all_games: dict[str, Game] = {}


# Server code
sio = socketio.Server()
app = socketio.WSGIApp(sio)


def update_game(game: Game, turn: othello.Color):
    """
    Send update of a game to all players and viewers.
    """
    print(f"Sending game update for {game.match_code}")

    sio.emit("game_update", messages.GameMessage(
        messages.Status.PLAYING,
        None,
        turn,
        game.board,
        None,
        None,
    ).to_json(), room=game.match_code)


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
def register(sid, msg_json):
    """
    Register a client as a player in game, updating client_games and the players
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

    client_games[sid] = game
    sio.enter_room(sid, game.match_code)

    if msg.color:
        print(f"Registering player {sid} as {msg.color.value} in match {msg.match_code}")

        if game.players[msg.color]:
            return #TODO handle duplicate registration

        game.players[msg.color] = sid

        if game.players[othello.Color.WHITE] and game.players[othello.Color.BLACK]:
            print(f"Starting match {game.match_code}")
            update_game(game, turn=othello.Color.BLACK)
    else:
        print(f"Registering viewer {sid} in match {msg.match_code}")
        update_game(game, turn=None)


@sio.event
def make_move(sid, msg_json):
    """
    Receive a move from a player, update the game, and update the other player.
    """
    game = client_games[sid]

    if sid == game.players[othello.Color.BLACK]:
        color = othello.Color.BLACK
    else:
        color = othello.Color.WHITE

    msg = messages.MoveMessage.from_json(msg_json)
    move = msg.move

    print(f"Match {game.match_code}: {color.value} plays {move}")

    #TODO update the board and figure out if game is over
    game.board.last_move = move

    update_game(game, turn=color.opp())


def run():
    eventlet.wsgi.server(eventlet.listen(("localhost", 8765)), app)
