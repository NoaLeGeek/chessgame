from random import random

from board.player import Player


class Minimax(Player):
    def __init__(self, color: int, depth: int):
        super().__init__(color)
        self.depth = depth
        self.ia = True

    def get_best_move(self, board):
        pass

class RandomIA(Player):
    def __init__(self, color: int):
        super().__init__(color)
        self.ia = True

    def get_best_move(self, board):
        moves = list(filter(lambda move: move.is_legal(), self.get_moves(board)))
        return random.choice(moves)
