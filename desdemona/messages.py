from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from desdemona import othello


class Status(Enum):
    PLAYING = "playing"
    ERROR = "error"
    WHITE_WINS = "white_wins"
    BLACK_WINS = "black_wins"
    DRAW = "draw"


@dataclass
class GameMessage(DataClassJsonMixin):
    """
    A server -> client message indicating game status.
    """

    status: Status
    error: Optional[str]
    move: Optional[othello.Move]
    board: Optional[str]
    ms_remaining: Optional[int]
    ms_remaining_opponent: Optional[int]


@dataclass
class RegisterMessage(DataClassJsonMixin):
    match_code: str
    color: othello.Color


@dataclass
class MoveMessage(DataClassJsonMixin):
    """
    A client -> server message indicating a move.
    """

    move: Optional[othello.Move]
