from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np


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


piece_idx = np.arange(64).reshape(8,8)

def extract_row(x: np.ndarray, row ,col):
    return x[row,:]

def extract_col(x: np.ndarray, row ,col):
    return x[:,col]

def extract_diag(x: np.ndarray, row ,col):
    return x.diagonal(col - row)

def extract_adiag(x: np.ndarray, row ,col):
    return np.fliplr(x).diagonal(7 - col - row)

def get_flips(pieces, piece_idx, move_idx, color):
    flips = []
    opp_after = []
    can_flip_before = False

    for i in range(len(pieces)):
        if piece_idx[i] < move_idx:
            if pieces[i] == color:
                flips_before = []
                can_flip_before = True
            if pieces[i] == color * -1 and can_flip_before:
                flips.append(piece_idx[i])

        if piece_idx[i] > move_idx:
            if pieces[i] == color:
                flips += opp_after
                break
            if pieces[i] == color * -1:
                opp_after.append(piece_idx[i])

    return flips


@dataclass
class Board:
    last_move: Optional[Move]
    pieces: np.ndarray

    def __init__(self):
        self.last_move = None
        self.pieces = np.zeros((8,8))
        self.pieces[3,3] = -1
        self.pieces[3,4] =  1
        self.pieces[4,3] =  1
        self.pieces[4,4] = -1

    def make_move(self, move: Move):
        if not move:
            return

        row       = extract_row(self.pieces, move.row, move.col)
        row_idx   = extract_row(piece_idx, move.row, move.col)
        col       = extract_col(self.pieces, move.row, move.col)
        col_idx   = extract_col(piece_idx, move.row, move.col)
        diag      = extract_diag(self.pieces, move.row, move.col)
        diag_idx  = extract_diag(piece_idx, move.row, move.col)
        adiag     = extract_adiag(self.pieces, move.row, move.col)
        adiag_idx = extract_adiag(piece_idx, move.row, move.col)

        move_idx = move.row * 8 + move.col
        color = 1 if move.color == Color.BLACK else -1

        flips = []
        flips += get_flips(row, row_idx, move_idx, color)
        flips += get_flips(col, col_idx, move_idx, color)
        flips += get_flips(diag, diag_idx, move_idx, color)
        flips += get_flips(adiag, adiag_idx, move_idx, color)

        if len(flips) == 0:
            return #TODO handle invalid moves

        for i in flips:
            row = int(i / 8)
            col = i % 8
            self.pieces[row,col] *= -1

        self.pieces[move.row,move.col] = color

    def piece_list(self):
        return self.pieces.tolist()
