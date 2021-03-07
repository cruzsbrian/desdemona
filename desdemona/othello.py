from dataclasses import dataclass
from enum import Enum


@dataclass
class Move:
    row: int
    col: int


class Color(Enum):
    WHITE = "white"
    BLACK = "black"


class Board:
    pass  # TODO
