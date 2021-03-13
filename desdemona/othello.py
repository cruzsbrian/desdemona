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
    can_flip_after = True

    for i in range(len(pieces)):
        if piece_idx[i] < move_idx:
            if pieces[i] == color:
                flips = []
                can_flip_before = True
            if pieces[i] == 0:
                flips = []
                can_flip_before = False
            if pieces[i] == color * -1 and can_flip_before:
                flips.append(piece_idx[i])

        if piece_idx[i] > move_idx:
            if pieces[i] == color:
                flips += opp_after
                break
            if pieces[i] == color * -1 and can_flip_after:
                opp_after.append(piece_idx[i])
            if pieces[i] == 0:
                break

    return flips


@dataclass
class Board:
    pieces: np.ndarray

    def __init__(self):
        self.pieces = np.zeros((8,8))
        self.pieces[3,3] = -1
        self.pieces[3,4] =  1
        self.pieces[4,3] =  1
        self.pieces[4,4] = -1

    def get_flips(self, move: Move):
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

        return flips

    def make_move(self, color: Color, move: Move):
        if not move:
            if len(self.get_moves(color)) != 0:
                raise InvalidMove()
            return

        flips = self.get_flips(move)

        if len(flips) == 0:
            raise InvalidMove()

        for i in flips:
            row = int(i / 8)
            col = i % 8
            self.pieces[row,col] *= -1

        self.pieces[move.row,move.col] = 1 if move.color == Color.BLACK else -1

    def get_moves(self, color: Color):
        moves = []

        for row in range(8):
            for col in range(8):
                m = Move(color, row, col)

                if self.pieces[m.row,m.col] == 0 and len(self.get_flips(m)) != 0:
                    moves.append(m)

        return moves

    def count_pieces(self, color: Color):
        n = 0

        for p in self.pieces.flatten():
            if (p == 1 and color == Color.BLACK) or (p == -1 and color == Color.WHITE):
                n += 1

        return n

    def piece_list(self):
        return self.pieces.tolist()


class InvalidMove(ValueError):
    """
    Exception thrown by the board when an invalid move is played.
    """
    pass
