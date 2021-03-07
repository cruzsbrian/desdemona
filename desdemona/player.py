import socketio
import argparse
from desdemona import messages, othello

sio = socketio.Client()


match_code = None
color = None


@sio.event
def connect():
    """
    Connection established with server; register this player in its game.
    """
    print(f"SID: {sio.get_sid()}")
    sio.emit(
        "register_player",
        messages.RegisterMessage(match_code, color).to_json(),
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

    print(f"Opponent played {msg.move}")

    move_str = input("Enter row, col: ")
    try:
        move = othello.Move(*move_str.split(','))
    except:
        print("Invalid move")
        move = None

    sio.emit("make_move", messages.MoveMessage(move).to_json())


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('match_code', metavar='match_code', type=str)
    parser.add_argument('color', metavar='color', type=othello.Color)
    args = parser.parse_args()

    global match_code, color
    match_code = args.match_code
    color = args.color

    print(f"Registering for match {match_code} as {color.value}")

    sio.connect("http://localhost:8765")
    sio.wait()
