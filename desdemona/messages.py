from dataclasses import dataclass
from typing import Optional, List

from dataclasses_json import DataClassJsonMixin

from desdemona import othello, games


@dataclass
class GameMessage(DataClassJsonMixin):
    """
    A server -> client message indicating game status.
    """

    status: games.Status
    error: Optional[str]
    turn: Optional[othello.Color]
    last_move: Optional[othello.Move]
    board: Optional[List[List[int]]]
    ms_remaining: Optional[int]
    ms_remaining_opponent: Optional[int]


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
