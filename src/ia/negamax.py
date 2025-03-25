from random import choice, shuffle
from constants import piece_values, piece_heatmaps

from board.player import Player


class NegamaxAI(Player):
    def __init__(self, color: int, depth: int):
        """
        Initializes the Negamax AI player with the specified color and search depth.

        Parameters:
            color (int): The color of the player. Typically, 1 for white and -1 for black.
            depth (int): The maximum depth of the search tree for the Negamax algorithm.

        Attributes:
            depth (int): The maximum depth of the search tree for the Negamax algorithm.
            stalemate (int): The score assigned to a stalemate situation (default is 0).
            checkmate (int): The score assigned to a checkmate situation (default is 1000).
            ia (int): A flag indicating that this is an AI player.
        """
        super().__init__(color)
        self.depth = depth
        self.stalemate = 0
        self.checkmate = 1000
        self.ia = 1

    def get_best_move(self, board):
        """
        Determines the best move for the current player using the Negamax algorithm.

        This method evaluates all possible moves on the given board and selects the 
        optimal move based on the Negamax algorithm with alpha-beta pruning.

        Parameters:
            board (object): The current state of the chessboard. It should be an 
                            object that represents the game state and provides 
                            necessary methods for move generation and evaluation.

        Returns:
            object: The best move determined by the Negamax algorithm. The exact 
                    type of the return value depends on the implementation of the 
                    board object and its move representation.
        """
        best_move, _ = self.negamax(board, self.depth, -self.checkmate, self.checkmate)
        return best_move

    def negamax(self, board, depth, alpha, beta):
        """
        Implements the Negamax algorithm for evaluating and selecting the best move in a chess game.
        The Negamax algorithm is a variant of the Minimax algorithm, optimized for two-player zero-sum games like chess.
        It recursively evaluates possible moves to a specified depth and returns the best move along with its score.
        Parameters:
            board (Board): The current state of the chessboard. It provides information about the game state, 
                           including the current player's legal moves.
            depth (int): The maximum depth to search in the game tree. A depth of 0 indicates the base case, 
                         where the evaluation function is used to score the board.
            alpha (float): The alpha value for alpha-beta pruning. It represents the best score that the maximizing 
                           player is assured of.
            beta (float): The beta value for alpha-beta pruning. It represents the best score that the minimizing 
                          player is assured of.
        Returns:
            tuple: A tuple containing:
                - best_move (Move or None): The best move found by the algorithm. If depth is 0, this will be None.
                - max_score (float): The score of the best move, as evaluated by the algorithm. A higher score 
                                     indicates a better move for the current player.
        """
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
        Evaluates the current state of the chess board and returns a score representing the board's favorability
        for the current player.

        This method calculates the score based on the positions and values of the pieces on the board, as well as
        the game's current state (e.g., stalemate or checkmate). Positive scores favor the current player, while
        negative scores favor the opponent.

        Parameters:
            board (Board): The chess board object representing the current state of the game. It contains
                           information about the pieces, their positions, and the current player's turn.

        Returns:
            int: A numerical score representing the evaluation of the board. Higher scores indicate a more
                 favorable position for the current player, while lower scores indicate a less favorable position.
                 Special values are returned for stalemates and checkmates.
        """
        if board.is_stalemate():
            if board.current_player.is_king_check(board):
                return self.checkmate * -board.turn
            else:
                return self.stalemate
        score = 0
        for tile in board.board.values():
            if board.is_empty(tile.pos):
                continue
            piece_score = piece_heatmaps[tile.piece.color*board.flipped][tile.piece.notation][tile.pos[0]][tile.pos[1]]
            score += (piece_values[tile.piece.notation.upper()] + piece_score) * tile.piece.color
        return score

    def play_move(self, board):
        """
        Executes the best move for the current player on the given chess board.

        This method determines the best possible move for the current player
        using the `get_best_move` method, executes that move on the board, 
        and updates the board's highlights to reflect the new state.

        Parameters:
            board (Board): The current state of the chess board. This object 
                           is modified in place to reflect the executed move 
                           and updated highlights.
        """
        self.get_best_move(board).execute(board)
        board.update_highlights()

class RandomAI(Player):
    def __init__(self, color: int):
        """
        Initializes an instance of the class with the specified color.

        Parameters:
            color (int): The color assigned to the instance. Typically, this 
                         represents the player's color in the chess game 
                         (e.g., 1 for white, -1 for black).

        Attributes:
            ia (int): A flag indicating that this instance represents an AI 
                      player. It is set to 1 by default.
        """
        super().__init__(color)
        self.ia = 1

    def get_best_move(self, board):
        """
        Determines the best legal move for the current board state.

        This method generates all possible moves for the given board, filters out
        the illegal ones, and selects one legal move at random.

        Parameters:
            board (object): The current state of the chessboard. It is expected to
                            be an object that provides the necessary methods for
                            generating and validating moves.

        Returns:
            object: A randomly selected legal move from the list of possible moves.
        """
        moves = [move for move in self.get_moves(board) if move.is_legal(board)]
        return choice(moves)
    
    def play_move(self, board):
        """
        Executes the best move for the current player on the given board.

        This method determines the best possible move for the current player
        using the `get_best_move` method, executes that move on the board, 
        and updates the board's highlights to reflect the new state.

        Parameters:
            board (Board): The current state of the chessboard. This object
                           is modified in-place to reflect the executed move
                           and updated highlights.
        """
        self.get_best_move(board).execute(board)
        board.update_highlights()
