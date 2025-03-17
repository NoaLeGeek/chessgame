from random import choice
from constants import piece_values, piece_heatmaps

from board.player import Player


class MinimaxAI(Player):
    def __init__(self, color: int, depth: int):
        super().__init__(color)
        self.depth = depth
        self.ia = True

    def evaluation(self, board):
        score = 0
        for tile in board.board.values():
            if tile.piece is None:
                continue
            score += piece_values.get(tile.piece.notation, 0)*tile.piece.color
        score += self.apply_heatmap(board)
        return score

    def minimax(self, board, depth, maximizing_player):
        if depth == 0:
            return self.evaluation(board), None
        
        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_moves(board):
                move.move()
                eval_score, _ = self.minimax(board, depth - 1, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in self.get_moves(board):
                move.move()
                eval_score, _ = self.minimax(board, depth - 1, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
            return min_eval, best_move

    def apply_heatmap(self, board):
        adjusted_score = 0
        for tile in board.board.values():
            if tile.piece is None:
                continue
            if tile.piece.notation in piece_heatmaps:
                adjusted_score += piece_heatmaps[tile.piece.notation][tile.pos[1]][tile.pos[0]]
        return adjusted_score

    def get_best_move(self, board):
        _, best_move = self.minimax(board, self.depth, self.color)
        return best_move
    
    def play_move(self, board):
        move = board.current_player.get_best_move(board)
        board.select(move.from_pos)
        board.select(move.to_pos)
        # TODO euhh ouais générer tous les moves de promotion selon le move.from_piece.promotion directement au lieu de faire ça
        if board.promotion is not None:
            row, column = board.promotion
            promotion_row = choice(range(row, row + len(move.from_piece.promotion)*board.flipped*self.color, board.flipped*self.color))
            board.select((promotion_row, column))

class RandomAI(Player):
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
        # TODO euhh ouais générer tous les moves de promotion selon le move.from_piece.promotion directement au lieu de faire ça
        if board.promotion is not None:
            row, column = board.promotion
            promotion_row = choice(range(row, row + len(move.from_piece.promotion)*board.flipped*self.color, board.flipped*self.color))
            board.select((promotion_row, column))
