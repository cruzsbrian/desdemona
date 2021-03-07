from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Color(Enum):
    WHITE = "white"
    BLACK = "black"

    def opp(self):
        return Color.WHITE if self == Color.BLACK else Color.BLACK


@dataclass
class Move:
    color: Color
    row: int
    col: int


@dataclass
class Board:
    last_move: Optional[Move] = None
    pass  # TODO
