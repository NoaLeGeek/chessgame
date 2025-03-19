from random import choice
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

    def findBestMove(game_state, valid_moves, return_queue):
        next_move = None
        random.shuffle(valid_moves)
        findMoveNegaMaxAlphaBeta(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE,
                                1 if game_state.white_to_move else -1)
        return_queue.put(next_move)


    def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
        if depth == 0:
            return turn_multiplier * scoreBoard(game_state)
        # move ordering - implement later //TODO
        max_score = -CHECKMATE
        for move in valid_moves:
            game_state.makeMove(move)
            next_moves = game_state.getValidMoves()
            score = -findMoveNegaMaxAlphaBeta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            game_state.undoMove()
            if max_score > alpha:
                alpha = max_score
            if alpha >= beta:
                break
        return max_score


    def evaluate_board(board):
        """
        Score the board. A positive score is good for white, a negative score is good for black.
        """
        if board.is_stalemate():
            if board.current_player.
                return -CHECKMATE  # black wins
            else:
                return CHECKMATE  # white wins
        elif game_state.stalemate:
            return STALEMATE
        score = 0
        for row in range(len(game_state.board)):
            for col in range(len(game_state.board[row])):
                piece = game_state.board[row][col]
                if piece != "--":
                    piece_position_score = 0
                    if piece[1] != "K":
                        piece_position_score = piece_position_scores[piece][row][col]
                    if piece[0] == "w":
                        score += piece_score[piece[1]] + piece_position_score
                    if piece[0] == "b":
                        score -= piece_score[piece[1]] + piece_position_score

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
