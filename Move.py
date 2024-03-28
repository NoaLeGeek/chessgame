import Pieces

class Move:
    #TODO game.move() should be moved here too?
    def __init__(self, game, from_, to, piece, capture=False, promotion=False):
        self.game = game
        self.from_ = from_
        self.to = to
        self.piece = piece
        self.capture = capture
        self.promotion = promotion

    def make_move(self):
        row, column = self.to
        self.game.remove(row, column)
        self.game.move(self.piece, row, column)
        self.game.change_turn()
        self.game.valid_moves, self.game.selected = [], None
        self.game.check_game()

    def promote(self):
        #row, column = 7*(1 - (self.piece.color * -self.piece.flipped))//2, self.from_[1] + self.piece.promotion[1]
        row, column = self.to
        self.game.remove(row, column)
        self.game.move(self.piece, row, column)
        self.game.board.board[row][column] = self.promotion(self.piece.color, row, column)
        self.game.change_turn()
        self.game.valid_moves, self.game.selected = [], None
        self.game.check_game()

    def to_literal(self):
        # TODO DONT FORGET TO ADD THE LITERAL IN THE HISTORIC AFTER DOING THE MOVE
        string = ["", "N", "B", "R", "Q", "K"][Pieces.Piece.piece_to_index(self.piece)] + ("x" if self.capture else "") + chr((self.to[1] if self.piece.flipped == -1 else 7 - self.to[1]) + 97) + str((7 - self.to[0] if self.piece.flipped == -1 else self.to[0]) + 1) + ("=" + ["N", "B", "R", "Q"][Pieces.Piece.piece_to_index(self.piece) - 1] if self.promotion else "") + ("#" if self.game.is_checkmate() else ("+" if self.game.is_king_checked() else ""))
        return string