from utils import flip_pos, sign, get_value
from config import config
from constants import castling_king_column

class Move:
    def __init__(self, board, from_pos, to_pos, castling=False, promotion=None):
        self.board = board
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.piece_tile = board.get_tile(from_pos)
        self.capture_tile = None
        self.promotion = None
        if board.ep is not None and not board.is_empty((from_pos[0], to_pos[1])) and board.get_piece((from_pos[0], to_pos[1])).is_enemy(self.piece_tile.piece):
            self.capture_tile = board.get_tile((from_pos[0], to_pos[1]))
        elif not board.is_empty(to_pos):
            self.capture_tile = board.get_tile(to_pos)
        if self.to_pos[0] in [0, config.rows - 1] and self.piece_tile.piece.notation == "P":
            self.promotion = promotion
        self.castling = castling
        self.notation = None

    def execute(self) -> None:
        if self.promotion is not None:
            self.board.promote_piece(self, self.promotion)
        else:
            self.board.move_piece(self)
        # TODO attention à ça quand draw_highlight
        # Modify the final column of the king if it's a castling move
        """ if self.is_castling():
            self.to = (row, flip_pos(get_value(d, 2, 6), flipped=d*flipped))) """
        self.board.change_turn()
        self.board.selected = None
        # Reset halfMoves if it's a capture or a pawn move
        if self.is_capture() or self.piece_tile.piece.notation == "P":
            self.board.halfMoves = 0
        if config.rules["+3_checks"] == True and self.board.is_king_checked():
            self.board.win_condition += 1
        self.notation = str(self)
        # This is the board state after the move
        self.fen = str(self.board)
        self.board.check_game()

    def play_sound_move(self) -> None:
        if self.is_castling():
            self.board.play_sound("castle")
        elif config.rules["giveaway"] == False and self.board.is_king_checked():
            self.board.play_sound("move-check")
        elif self.promotion is not None:
            self.board.play_sound("promote")
        elif self.is_capture():
            self.board.play_sound("capture")
        else:
            if self.board.turn * self.board.flipped == 1:
                self.board.play_sound("move-self")
            else:
                self.board.play_sound("move-opponent")

    def is_capture(self) -> bool:
        return self.capture_tile is not None
    
    def is_legal(self) -> bool:
        if not self.is_castling():
            return self.piece_tile.can_move(self.board, self.to_pos)
        # Castling
        is_legal = True
        d = sign(self.to_pos[1] - self.from_pos[1])
        for next_column in list(range(self.from_pos[1] + d, flip_pos(castling_king_column[d*self.board.flipped], flipped=self.board.flipped) + d, d)):
            condition = self.piece_tile.can_move(self.board, (self.from_pos[0], next_column))
            is_legal = is_legal and condition
            if not is_legal:
                break
        return is_legal
    
    def is_castling(self) -> bool:
        if not self.is_capture() or self.capture_tile.piece.notation != "R" or self.piece_tile.piece.notation != "K" or self.piece_tile.piece.is_enemy(self.capture_tile.piece):
            return False
        # O-O-O castling's right
        if self.capture_tile.pos[1] < self.piece_tile.pos[1] and not self.board.castling[self.piece_tile.piece.color][-1]:
            return False
        # O-O castling's right
        elif self.capture_tile.pos[1] > self.piece_tile.pos[1] and not self.board.castling[self.piece_tile.piece.color][1]:
            return False
        return True
    
    def is_en_passant(self) -> bool:
        return self.piece_tile.piece.notation == "P" and self.is_capture() and self.capture_tile.pos != self.to_pos and self.board.ep is not None and self.to_pos == self.board.ep
        
    def __str__(self) -> str:
        string = ""
        # The move is O-O or O-O-O
        if self.is_castling():
            string += "O" + "-O"*(get_value(sign(self.to_pos[1] - self.from_pos[1]) * self.board.flipped, 1, 2))
        else:
            if self.is_capture():
                # Add the symbol of the piece
                if self.piece_tile.piece.notation != "P":
                    string += self.piece_tile.piece.notation
                # Add the starting column if it's a pawn
                else:
                    string += chr(flip_pos(self.from_pos[1], flipped = self.board.flipped) + 97)
                # Add x if it's a capture
                string += "x"
            # Add the destination's column
            string += chr(flip_pos(self.to_pos[1], flipped = self.board.flipped) + 97)
            # Add the destination's row
            string += str(flip_pos(self.to_pos[0], flipped = -self.board.flipped) + 1)
            # Add promotion
            if self.promotion is not None:
                string += "=" + self.promotion.notation
        # Add # if it's checkmate or + if it's a check
        if self.board.is_king_checked():
            if self.board.is_stalemate():
                string += "#"
            else:
                string += "+"
        return string