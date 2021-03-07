from typing import Optional

import json
import coolname
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit, join_room

from desdemona import messages, othello


HOST = "localhost"
PORT = 5000


class Game:
    match_code: str
    board: othello.Board
    players: dict[othello.Color, str]

    def __init__(self, match_code):
        self.match_code = match_code
        self.board = othello.Board()
        self.players = {
            othello.Color.BLACK : None,
            othello.Color.WHITE : None,
        }


# Map from connection sids to games
player_games: dict[str, Game] = {}

# Map from match codes to games
all_games: dict[str, Game] = {}


# Server code
app = Flask(__name__)
socketio = SocketIO(app)


def create_game():
    """
    Create a new game, and return the corresponding match code to the requester.
    """
    # NOTE: this may yield a name collision after ~300K games without server restart
    game_code = coolname.generate_slug(2)

    game = Game(game_code)
    all_games[game_code] = game

    return game_code

def update_game(game: Game, turn: othello.Color):
    """
    Send update of a game to all players and viewers.
    """
    print(f"Sending game update for {game.match_code}")

    emit("game_update", messages.GameMessage(
        messages.Status.PLAYING,
        None,
        turn,
        game.board.last_move,
        game.board.piece_list(),
        None,
        None,
    ).to_json(), room=game.match_code)


@socketio.on("connect")
def connect():
    print("SERVER: connected to", request.sid)


@socketio.on("disconnect")
def disconnect():
    print("SERVER: disconnected from", request.sid)


@socketio.on("register")
def register(msg_json):
    """
    Register a client as a player in game, updating player_games and the players
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

    join_room(game.match_code)

    if msg.color:
        if game.players[msg.color]:
            return #TODO handle duplicate registration

        print(f"Registering player {request.sid} as {msg.color.value} in match {msg.match_code}")
        player_games[request.sid] = game
        game.players[msg.color] = request.sid

        if game.players[othello.Color.WHITE] and game.players[othello.Color.BLACK]:
            print(f"Starting match {game.match_code}")
            update_game(game, turn=othello.Color.BLACK)
    else:
        print(f"Registering viewer {request.sid} in match {msg.match_code}")
        update_game(game, turn=None)


@socketio.on("make_move")
def make_move(msg_json):
    """
    Receive a move from a player, update the game, and update the other player.
    """
    game = player_games[request.sid]

    if request.sid == game.players[othello.Color.BLACK]:
        color = othello.Color.BLACK
    else:
        color = othello.Color.WHITE

    msg = messages.MoveMessage.from_json(msg_json)
    move = msg.move

    print(f"Match {game.match_code}: {color.value} plays {move}")

    game.board.last_move = move
    game.board.make_move(move)

    update_game(game, turn=color.opp())


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template('home.html')
    if request.method == "POST":
        return render_template('newgame.html', match_code=create_game())

@app.route("/view/<match_code>")
def view(match_code):
    return render_template('view.html', match_code=match_code)


def run():
    print(f"Hosting on http://{HOST}:{PORT}")
    socketio.run(app, host=HOST, port=PORT)
