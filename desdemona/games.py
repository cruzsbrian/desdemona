from enum import Enum
from typing import Optional

from desdemona import othello


class Status(Enum):
    PLAYING = "playing"
    ERROR = "error"
    WHITE_WINS = "white_wins"
    BLACK_WINS = "black_wins"
    DRAW = "draw"


class Game:
    match_code: str

    status: Status
    error: Optional[str]

    board: othello.Board
    move_history: list[othello.Move]
    turn: othello.Color

    players: dict[othello.Color, str]

    def __init__(self, match_code):
        self.match_code = match_code

        self.status = Status.PLAYING
        self.error = None

        self.board = othello.Board()
        self.move_history = []
        self.turn = othello.Color.BLACK

        self.players = {
            othello.Color.BLACK : None,
            othello.Color.WHITE : None,
        }

    def update(self, move: othello.Move):
        try:
            self.board.make_move(move)
            self.move_history.append(move)
            self.turn = move.color.opp()

        except othello.InvalidMove:
            self.status = Status.ERROR
            self.error = f"Invalid move by {move.color.value}"
