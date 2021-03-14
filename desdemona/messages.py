from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict

from dataclasses_json import DataClassJsonMixin

from desdemona import othello, games


@dataclass
class GameMessage(DataClassJsonMixin):
    """
    A server -> client message indicating game status.
    """

    status: games.Status
    error: Optional[str]
    score: Optional[Tuple[int]]
    turn: Optional[othello.Color]
    last_move: Optional[othello.Move]
    board: Optional[List[List[int]]]
    ms_remaining: Optional[Dict[str, int]]
    black_sid: Optional[str]
    white_sid: Optional[str]


@dataclass
class RegisterMessage(DataClassJsonMixin):
    """
    A client -> server message sent after connect to register with a game.
    If color is provided, the client is playing for that color. Otherwise the
    client is a viewer.
    """
    match_code: str
    color: Optional[othello.Color]


@dataclass
class MoveMessage(DataClassJsonMixin):
    """
    A client -> server message indicating a move.
    """

    move: Optional[othello.Move]
