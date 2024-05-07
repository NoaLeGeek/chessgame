import Pieces

from constants import flip_coords, config, piece_assets, sign, get_value
from Config import play_sound

class Move:
    def __init__(self, game, from_, to, piece, capture: bool | Pieces.Piece = False, promotion: bool | tuple[Pieces.Piece, int] = False):
        self.game = game
        self.from_ = from_
        self.to = to
        self.piece = piece
        self.capture = capture
        self.promotion = promotion
        self.board = game.board
        self.fen = None
        self.notation = None

    def make_move(self):
        row, column = self.to
        castling = self.game.is_castling(self.piece, *self.to)
        # Modify the final column of the king if it's a castling move
        self.game.move(self)
        if castling:
            self.to = (row, (7 + self.game.flipped + get_value(sign(column - self.from_[1]), 4, -4)) // 2)
        # Add the promoted piece to the board if there is one
        if self.promotion and config["selected_piece_asset"] != "blindfold":
            self.promotion.image = piece_assets[config["selected_piece_asset"]][Pieces.Piece.piece_to_index(self.promotion) + get_value(self.promotion.color, 0, 6)]
            self.game.board[row][column] = self.promotion
        self.game.change_turn()
        self.game.legal_moves, self.game.selected = [], None
        # Reset halfMoves if it's a capture or a pawn move
        if self.capture or isinstance(self.piece, Pieces.Pawn):
            self.game.halfMoves = 0
        if self.game.gamemode == "+3 Checks" and self.game.is_king_checked():
            self.game.win_condition += 1
        self.notation = self.to_literal()
        self.fen = self.game.generate_fen()
        self.game.history.append(self)
        print(self.game.history[-1])
        self.game.check_game()
        if castling:
            play_sound("castle")
        elif self.game.is_king_checked():
            play_sound("move-check")
        elif self.promotion:
            play_sound("promote")
        elif self.capture:
            play_sound("capture")
        else:
            if self.game.turn * self.game.flipped == 1:
                play_sound("move-self")
            else:
                play_sound("move-opponent")

    def to_literal(self):
        row, column = self.to
        string = ""
        # The move is O-O or O-O-O
        if isinstance(self.piece, Pieces.King) and isinstance(self.game.board[row][column], Pieces.Rook) and self.game.board[row][column].color == self.piece.color:
            string += "O" + "-O"*(get_value(sign(column - self.from_[1]) * self.game.flipped, 1, 2))
        else:
            # Add the symbol of the piece or the starting column if it's a pawn
            string += [(chr(flip_coords(self.from_[1], flipped = self.game.flipped) + 97) if self.capture else ""), "N", "B", "R", "Q", "K"][Pieces.Piece.piece_to_index(self.piece)]
            # Add x if it's a capture
            string += ("x" if self.capture else "")
            # Add the destination's column
            string += chr(flip_coords(column, flipped = self.game.flipped) + 97)
            # Add the destination's row
            string += str(flip_coords(row, flipped = -self.game.flipped) + 1)
            # Add promotion
            string += ("=" + ["N", "B", "R", "Q"][Pieces.Piece.piece_to_index(self.promotion) - 1] if self.promotion else "")
        # Add # if it's checkmate or + if it's a check
        string += ("#" if self.game.is_checkmate() else ("+" if self.game.is_king_checked() else ""))
        return string