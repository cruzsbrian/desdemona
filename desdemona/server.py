from typing import Optional, Dict
import time

import json
import coolname
from flask import Flask, request, render_template, redirect
from flask_socketio import SocketIO, emit, join_room

from desdemona import messages, othello, games


HOST = "localhost"
PORT = 5000


# Map from connection sids to games
player_games: Dict[str, games.Game] = {}

# Map from match codes to games
all_games: Dict[str, games.Game] = {}


# Server code
app = Flask(__name__)
socketio = SocketIO(app)


def create_game(time_black, time_white):
    """
    Create a new game, and return the corresponding match code to the requester.
    """
    # NOTE: this may yield a name collision after ~300K games without server restart
    game_code = ''.join(x.capitalize() for x in coolname.generate(2))

    game = games.Game(game_code, time_black, time_white)
    all_games[game_code] = game

    return game_code


def send_update(game: games.Game, to=None):
    """
    Send update of a game to all viewers, and an optionally specified player.
    Sending a player an update implies they should move.
    """
    print(f"Sending game update for {game.match_code}")

    if len(game.move_history) > 0:
        last_move = game.move_history[-1]
    else:
        last_move = None

    msg_json = messages.GameMessage(
        game.status,
        game.error,
        game.score,
        game.turn,
        last_move,
        game.board.piece_list(),
        {key.value:value for (key, value) in game.time_left.items()},
        game.players[othello.Color.BLACK],
        game.players[othello.Color.WHITE],
    ).to_json()

    emit("game_update", msg_json, to=game.match_code)

    if to:
        print(f"Sending game update for {game.match_code} to {to}")
        emit("game_update", msg_json, to=to)


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

    if msg.color:
        if game.players[msg.color]:
            pass #TODO handle duplicate registration

        print(f"Registering player {request.sid} as {msg.color.value} in match {msg.match_code}")
        player_games[request.sid] = game
        game.players[msg.color] = request.sid

        if game.players[othello.Color.WHITE] and game.players[othello.Color.BLACK]:
            game.status = games.Status.PLAYING
            print(f"Starting match {game.match_code}")
            send_update(game, to=game.players[othello.Color.BLACK])
            game.start_time[othello.Color.BLACK] = time.time()
    else:
        print(f"Registering viewer {request.sid} in match {msg.match_code}")
        join_room(game.match_code) # add viewer to the room for the game

    send_update(game) # send game to viewers


@socketio.on("make_move")
def make_move(msg_json):
    """
    Receive a move from a player, update the game, and update the other player.
    """
    game = player_games[request.sid]

    if request.sid == game.players[othello.Color.BLACK]:
        color = othello.Color.BLACK
    elif request.sid == game.players[othello.Color.WHITE]:
        color = othello.Color.WHITE
    else:
        pass #TODO we got a move from someone not playing

    if game.time_left[color]:
        move_time = time.time() - game.start_time[color]
        game.time_left[color] -= move_time

    msg = messages.MoveMessage.from_json(msg_json)
    move = msg.move

    print(f"Match {game.match_code}: {color.value} plays {move}")

    game.update(color, move)

    if game.status == games.Status.PLAYING or game.status == games.Status.ERROR:
        send_update(game, to=game.players[game.turn])
        game.start_time[game.turn] = time.time()
    else:
        # game is over, send message to all clients
        print(f"Ending game {game.match_code} with status {game.status.value}")
        join_room(game.match_code, sid=game.players[othello.Color.BLACK])
        join_room(game.match_code, sid=game.players[othello.Color.WHITE])
        send_update(game)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template('home.html')
    if request.method == "POST":
        try:
            time_black = int(request.form["time_black"])
        except:
            time_black = None

        try:
            time_white = int(request.form["time_white"])
        except:
            time_white = None

        match_code = create_game(time_black, time_white)
        return redirect(f"/view/{match_code}")

@app.route("/view/<match_code>")
def view(match_code):
    return render_template('view.html', match_code=match_code)


def run():
    print(f"Hosting on http://{HOST}:{PORT}")
    socketio.run(app, host=HOST, port=PORT)
