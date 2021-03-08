import socketio
import argparse
from desdemona import messages, othello, games

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
        "register",
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

    # Only care about updates when it's our turn
    if (msg.status == games.Status.PLAYING):
        print(f"Opponent played {msg.last_move}")

        move_str = input("Enter row, col: ")
        row, col = [int(x) for x in move_str.split(',')]
        try:
            move = othello.Move(color, row, col)
        except:
            print("Invalid move")
            move = None

        sio.emit("make_move", messages.MoveMessage(move).to_json())

    else:
        print(f"Game over: {msg.status.value}")
        if msg.status == games.Status.ERROR:
            print(msg.error)

        sio.disconnect()


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('match_code', metavar='match_code', type=str)
    parser.add_argument('color', metavar='color', type=othello.Color)
    args = parser.parse_args()

    global match_code, color
    match_code = args.match_code
    color = args.color

    print(f"Registering for match {match_code} as {color.value}")

    sio.connect("http://localhost:5000")
    sio.wait()
