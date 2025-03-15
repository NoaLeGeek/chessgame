from random import choice

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
        return choice(moves)
    
    def play_move(self, board):
        move = board.current_player.get_best_move(board)
        board.select(move.from_pos)
        board.select(move.to_pos)
        if board.promotion is not None:
            row, column = board.promotion
            promotion_column = choice(range(column, column + 4*board.flipped, board.flipped))
            board.select((row, promotion_column))
