import socketio

from desdemona import messages

sio = socketio.Client()

@sio.event
def connect():
    print("connected")
    sio.emit("create_game")

@sio.event
def get_game_code(match_code_msg):
    print("Match code:", match_code_msg)
    sio.disconnect()

def run():
    sio.connect("http://localhost:8765")
    sio.wait()
