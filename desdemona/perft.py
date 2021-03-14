import copy

from desdemona import othello


def perft(b: othello.Board, c: othello.Color, depth: int, passed: bool):
    if (depth == 0): return 1;

    moves = b.get_moves(c)

    if len(moves) == 0:
        if passed: return 1
        return perft(b, c.opp(), depth - 1, True)

    nodes = 0
    for m in moves:
        b1 = copy.deepcopy(b)
        b1.make_move(c, m)
        nodes += perft(b1, c.opp(), depth - 1, True)

    return nodes


b = othello.Board()
print(perft(b, othello.Color.BLACK, 7, False))
