from dataclasses import dataclass
from enum import Enum


@dataclass
class Move:
    row: int
    col: int


class Color(Enum):
    WHITE = "white"
    BLACK = "black"

    def opp(self):
        return Color.WHITE if self == Color.BLACK else Color.BLACK


class Board:
    pass  # TODO
