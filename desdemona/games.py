from enum import Enum
from typing import Optional, Tuple, List, Dict

from desdemona import othello


class Status(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    ERROR = "error"
    WHITE_WINS = "white wins"
    BLACK_WINS = "black wins"
    DRAW = "draw"


class Game:
    match_code: str

    status: Status
    error: Optional[str]
    score: Optional[Tuple[int]]

    board: othello.Board
    move_history: List[othello.Move]
    turn: othello.Color

    players: Dict[othello.Color, str]
    time_left: Dict[othello.Color, float]
    start_time: Dict[othello.Color, float]


    def __init__(self, match_code, time_black=None, time_white=None):
        self.match_code = match_code

        self.status = Status.WAITING
        self.error = None
        self.score = None

        self.board = othello.Board()
        self.move_history = []
        self.turn = othello.Color.BLACK

        self.players = {
            othello.Color.BLACK : None,
            othello.Color.WHITE : None,
        }

        self.time_left = {
            othello.Color.BLACK : time_black,
            othello.Color.WHITE : time_white,
        }

        self.start_time = {
            othello.Color.BLACK : 0,
            othello.Color.WHITE : 0,
        }


    def update(self, color: othello.Color, move: othello.Move):
        self.status = Status.PLAYING # needed if coming from an error state

        try:
            self.board.make_move(color, move)
            self.move_history.append(move)
            self.turn = color.opp()

            # Handle game over
            if (len(self.board.get_moves(othello.Color.BLACK)) == 0 and
                len(self.board.get_moves(othello.Color.WHITE)) == 0):
                black_score = self.board.count_pieces(othello.Color.BLACK)
                white_score = self.board.count_pieces(othello.Color.WHITE)

                self.score = (black_score, white_score)

                if black_score > white_score:
                    self.status = Status.BLACK_WINS
                elif black_score < white_score:
                    self.status = Status.WHITE_WINS
                else:
                    self.status = Status.DRAW

        except othello.InvalidMove:
            self.status = Status.ERROR
            self.error = f"Invalid move by {color.value}"
