#!/usr/bin/python3

# Launches the server on 0.0.0.0:80, for hosting over the internet

from desdemona.server import socketio, app

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=80)
