from random import choice, shuffle
from constants import piece_values, piece_heatmaps

from board.player import Player
from board.board import Board


class NegamaxAI(Player):
    def __init__(self, color: int, depth: int):
        super().__init__(color)
        self.depth = depth
        self.stalemate = 0
        self.checkmate = 1000
        self.ia = 1

    def get_best_move(self, board):
        best_move, _ = self.negamax(board, self.depth, -self.checkmate, self.checkmate)
        return best_move

    def negamax(self, board, depth, alpha, beta):
        if depth == 0:
            return None, board.turn * self.evaluate_board(board)
        
        max_score = -self.checkmate
        best_move = None

        for move in board.current_player.get_legal_moves(board):
            move.move(board)
            _, score = self.negamax(board, depth - 1, -beta, -alpha)
            score = -score
            move.undo(board)

            if score > max_score:
                max_score = score
                best_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return best_move, max_score

    def evaluate_board(self, board):
        """
        Score the board. A positive score is good for white, a negative score is good for black.
        """
        if board.is_stalemate():
            if board.current_player.is_king_check(board):
                return self.checkmate * -board.turn
            else:
                return self.stalemate
        score = 0
        for tile in board.board.values():
            if tile is None:
                raise ValueError("Tile is None")
            if board.is_empty(tile.pos):
                continue
            piece_score = [row[::tile.piece.color] for row in piece_heatmaps[tile.piece.notation.upper()][::tile.piece.color]][tile.pos[0]][tile.pos[1]]
            score += (piece_values[tile.piece.notation.upper()] + piece_score) * tile.piece.color
        return score

    def play_move(self, board):
        self.get_best_move(board).execute(board)
        board.update_highlights()

class RandomAI(Player):
    def __init__(self, color: int):
        super().__init__(color)
        self.ia = 1

    def get_best_move(self, board):
        moves = [move for move in self.get_moves(board) if move.is_legal(board)]
        return choice(moves)
    
    def play_move(self, board):
        self.get_best_move(board).execute(board)
        board.update_highlights()
