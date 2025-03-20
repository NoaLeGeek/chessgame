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
        self.ia = True

    def get_best_move(self, board, valid_moves, return_queue):
        next_move = None
        shuffle(valid_moves)
        findMoveNegaMaxAlphaBeta(board, valid_moves, self.depth, -self.checkmate, self.checkmate, board.turn)
        return_queue.put(next_move)

    def findMoveNegaMaxAlphaBeta(self, board, valid_moves, depth, alpha, beta, turn_multiplier):
        if depth == 0:
            return turn_multiplier * self.evaluate_board(board)
        max_score = -self.checkmate
        for move in valid_moves:
            board.makeMove(move)
            next_moves = board.getValidMoves()
            score = -findMoveNegaMaxAlphaBeta(board, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
            if score > max_score:
                max_score = score
                if depth == self.depth:
                    next_move = move
            board.undoMove()
            if max_score > alpha:
                alpha = max_score
            if alpha >= beta:
                break
        return max_score

    def evaluate_board(self, board):
        """
        Score the board. A positive score is good for white, a negative score is good for black.
        """
        if board.is_stalemate():
            if board.current_player.is_king_check():
                return self.checkmate * -board.turn
            else:
                return self.stalemate
        score = 0
        for tile in board.board.values():
            if tile is None:
                raise ValueError("Tile is None")
            if board.is_empty(tile.pos):
                continue
            piece_score = [row[::tile.piece.color] for row in piece_heatmaps][::tile.piece.color][tile.piece.notation.upper()][row][col]
            score += (piece_values[tile.piece.notation.upper()] + piece_score) * tile.piece.color
        return score
        
    def play_move(self, board):
        self.get_best_move(board).execute(board)
        board.update_highlights()

class RandomAI(Player):
    def __init__(self, color: int):
        super().__init__(color)
        self.ia = True

    def get_best_move(self, board):
        moves = list(filter(lambda move: move.is_legal(board), self.get_moves(board)))
        return choice(moves)
    
    def play_move(self, board):
        self.get_best_move(board).execute(board)
        board.update_highlights()
