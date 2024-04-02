import Pieces
from constants import *

class Move:
    def __init__(self, game, from_, to, piece, capture=False, promotion=False):
        self.game = game
        self.from_ = from_
        self.to = to
        self.piece = piece
        self.capture = capture
        self.promotion = promotion

    def make_move(self):
        row, column = self.to
        print(row, column)
        self.game.remove(row, column)
        self.game.move(self.piece, row, column)
        self.game.change_turn()
        self.game.valid_moves, self.game.selected = [], None
        if self.capture or isinstance(self.piece, Pieces.Pawn):
            self.game.halfMoves = 0
        self.game.history.append((self, self.to_literal()))
        self.game.check_game()

    def promote(self):
        row, column = self.to
        self.game.remove(row, column)
        self.game.move(self.piece, row, column)
        self.game.board.board[row][column] = self.promotion(self.piece.color, row, column)
        self.game.change_turn()
        self.game.valid_moves, self.game.selected = [], None
        if self.capture or isinstance(self.piece, Pieces.Pawn):
            self.game.halfMoves = 0
        self.game.history.append((self, self.to_literal()))
        self.game.check_game()

    def to_literal(self):
        # TODO DONT FORGET TO ADD THE LITERAL IN THE HISTORIC AFTER DOING THE MOVE
        string = ""
        # The move is O-O or O-O-O
        if isinstance(self.piece, Pieces.King) and abs(self.from_[1] - self.to[1]) == 2:
            string += "O" + "-O"*((-self.to[1] + 10) // 4)
        else:
            # Add the symbol of the piece or the starting column if it's a pawn
            string += [(chr(flip_coords(self.game.flipped, self.from_[1]) + 97) if self.capture else ""), "N", "B", "R", "Q", "K"][Pieces.Piece.piece_to_index(self.piece)]
            # Add x if it's a capture
            string += ("x" if self.capture else "")
            # Add the destination's column
            string += chr(flip_coords(self.game.flipped, self.to[1]) + 97)
            # Add the destination's row
            string += str(flip_coords(-self.game.flipped, self.to[0]) + 1)
            # Add promotion
            string += ("=" + ["N", "B", "R", "Q"][Pieces.Piece.piece_to_index(self.piece) - 1] if self.promotion else "")
        # Add # if it's checkmate or + if it's a check
        string += ("#" if self.game.is_checkmate() else ("+" if self.game.is_king_checked() else ""))
        return string