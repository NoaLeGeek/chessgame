from utils import flip_coords, sign, get_value, play_sound
from Board.piece import Piece

class Move:
    def __init__(self, board, from_, to, castling=False):
        self.board = board
        self.from_ = from_
        self.to = to
        self.piece = board.get_object(*from_)
        if board.ep_square is not None and board.is_enemy(*board.ep_square, ):
            self.capture = board.get_object(to[0] - self.piece.color*self.board.flipped, to[1])
        elif board.is_piece(*to):
            self.capture = board.get_object(*to)
        self.promotion = 
        self.castling = castling
        self.notation = None

    def execute(self, promotion: Piece = None) -> None:
        if promotion is not None:
            self.promotion = promotion
            self.board.promote_piece(self, promotion)
        # Modify the final column of the king if it's a castling move
        self.board.move_piece(self)
        # TODO attention à ça quand draw_highlight
        """ if self.is_castling():
            self.to = (row, flip_coords(get_value(d, 2, 6), flipped=d*flipped))) """
        self.board.change_turn()
        self.board.selected = [], None
        # Reset halfMoves if it's a capture or a pawn move
        if self.is_capture() or self.get_piece().notation == "P":
            self.board.halfMoves = 0
        if self.board.config.rules["+3_checks"] == True and self.board.is_king_checked():
            self.board.win_condition += 1
        self.notation = self.to_literal()
        self.fen = self.board.generate_fen()
        self.board.moveLogs.append(self)
        self.board.check_game()

    def play_sound(self) -> None:
        if self.is_castling():
            play_sound("castle")
        elif self.board.config.rules["giveaway"] == False and self.board.is_in_check():
            play_sound("move-check")
        elif self.promotion is not None:
            play_sound("promote")
        elif self.is_capture():
            play_sound("capture")
        else:
            if self.board.turn * self.board.flipped == 1:
                play_sound("move-self")
            else:
                play_sound("move-opponent")

    def is_capture(self) -> bool:
        return self.capture is not None
    
    def is_legal(self) -> bool:
        if not self.is_castling():
            return self.piece.can_move(self.board, *self.to)
        # Castling
        is_legal = True
        if self.is_castling():
            d = sign(self.to[1] - self.from_[1])
            flipped = self.board.flipped
            for next_column in range(min(flip_coords(self.to[1], flipped=d*flipped), flip_coords(get_value(d, 2, 6), flipped=d*flipped)), self.from_[1], d*flipped):
                is_legal = is_legal and self.get_piece().can_move(self.from_[0], next_column)
                if not is_legal:
                    break
        return is_legal
    
    def is_castling(self) -> bool:
        return self.piece.notation == "K" and self.capture.notation == "R" and self.get_piece().color == self.get_capture().color and self.get_piece().first_move and self.get_capture().first_move
        
    def __str__(self) -> str:
        row, column = self.to
        string = ""
        # The move is O-O or O-O-O
        if self.is_castling():
            string += "O" + "-O"*(get_value(sign(column - self.from_[1]) * self.board.flipped, 1, 2))
        else:
            if self.is_capture():
                # Add the symbol of the piece
                if self.get_piece().notation != "P":
                    string += self.get_piece().notation
                # Add the starting column if it's a pawn
                else:
                    string += chr(flip_coords(self.from_[1], flipped = self.board.flipped) + 97)
                # Add x if it's a capture
                string += "x"
            # Add the destination's column
            string += chr(flip_coords(column, flipped = self.game.flipped) + 97)
            # Add the destination's row
            string += str(flip_coords(row, flipped = -self.game.flipped) + 1)
            # Add promotion
            if self.promotion is not None:
                string += "=" + self.promotion.notation
        # Add # if it's checkmate or + if it's a check
        if self.board.is_in_check():
            if self.board.is_checkmate():
                string += "#"
            else:
                string += "+"
        return string