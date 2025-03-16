from random import choice
from constants import piece_values

from board.player import Player


class Minimax(Player):
    def __init__(self, color: int, depth: int):
        super().__init__(color)
        self.depth = depth
        self.ia = True

    def evaluation(self, board):
        score = 0
        for tile in board.values():
            if tile.piece is None:
                continue
            score += piece_values.get(tile.piece.notation, 0)*tile.piece.color
        return score

    def minimax(self, board, depth, maximizing_player):
        if depth == 0:
            return self.evaluation(board), None
        
        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_moves(board):
                new_board = board.copy()  # Appliquer le mouvement
                eval_score, _ = self.minimax(new_board, depth - 1, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in self.get_moves(board):
                new_board = board.copy()
                eval_score, _ = self.minimax(new_board, depth - 1, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
            return min_eval, best_move

    def apply_heatmap(board, heatmap):
        """Applique une heatmap à l'évaluation pour influencer les choix."""
        adjusted_score = 0
        for position, piece in board.items():
            if piece and piece.lower() in heatmap:
                adjusted_score += heatmap[piece.lower()][position[1]][position[0]]
        return adjusted_score

    def get_best_move(board, depth, player):
        """Renvoie le meilleur coup pour le joueur donné en utilisant Minimax."""
        _, best_move = minimax(board, depth, player == 1)
        return best_move

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
        # TODO euhh ouais générer tous les moves de promotion selon le move.from_piece.promotion directement au lieu de faire ça
        if board.promotion is not None:
            row, column = board.promotion
            promotion_row = choice(range(row, row + len(move.from_piece.promotion)*board.flipped*self.color, board.flipped*self.color))
            board.select((promotion_row, column))
