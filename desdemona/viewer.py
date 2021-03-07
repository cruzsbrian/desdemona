import socketio
import argparse
from desdemona import messages, othello

sio = socketio.Client()


match_code = None


@sio.event
def connect():
    """
    Connection established with server; register this player in its game.
    """
    print(f"SID: {sio.get_sid()}")
    sio.emit(
        "register",
        messages.RegisterMessage(match_code, None).to_json(),
    )


@sio.event
def game_update(msg_json):
    """
    Read the game update from the server, get the next move through stdin, then
    send it to the server.
    """
    try:
        msg = messages.GameMessage.from_json(msg_json)
    except:
        return

    print(msg.board.last_move)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('match_code', metavar='match_code', type=str)
    args = parser.parse_args()

    global match_code
    match_code = args.match_code

    print(f"Registering for match {match_code}")

    sio.connect("http://localhost:8765")
    sio.wait()
