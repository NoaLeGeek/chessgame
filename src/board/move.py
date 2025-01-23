from utils import flip_pos, sign, get_value
from config import config
from constants import castling_king_column
from board.piece import piece_to_notation

class Move:
    def __init__(self, board, from_pos, to_pos, promotion=None):
        self.board = board
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.from_tile = board.get_tile(from_pos)
        self.to_tile = board.get_tile(to_pos)
        self.capture = self._is_capture()
        self.castling = self._is_castling()
        self.en_passant = self._is_en_passant()
        self.promotion = self._get_promotion(promotion)
        self.notation = None
        self.fen = None

    def _get_promotion(self, promotion) -> None:
        """Validates if the promotion is possible based on the piece's position."""
        if promotion is not None and (self.to_pos[0] not in [0, config.rows - 1] or self.from_tile.piece.notation != "P"):
            raise ValueError("Promotion is only possible for pawns at the last row")
        return promotion

    def execute(self) -> None:
        """Executes the move on the board and updates the game state."""
        # Reset half_moves if it's a capture or a pawn move
        if self.capture or self.from_tile.piece.notation == "P":
            self.board.half_moves = 0
        if self.promotion is not None:
            self.board.promote_piece(self.promotion)
        else:
            self.board.move_piece(self)
        # TODO attention à ça quand draw_highlight
        # Modify the final column of the king if it's a castling move
        """ if self.castling:
            self.to = (row, flip_pos(get_value(d, 2, 6), flipped=d*flipped))) """
        if self.board.turn == -1:
            self.board.full_moves += 1
        self.board.half_moves += 1
        self.board.turn *= -1
        self.board.selected = None
        self._play_sound_move()
        self.notation = str(self)
        # This is the board state after the move
        self.fen = str(self.board)
        self.board.check_game()

    def _play_sound_move(self) -> None:
        """Plays the appropriate sound based on the move type."""
        if self.castling:
            self.board.play_sound("castle")
        elif self.board.is_king_checked():
            self.board.play_sound("move-check")
        elif self.promotion is not None:
            self.board.play_sound("promote")
        elif self.capture:
            self.board.play_sound("capture")
        else:
            self.board.play_sound("move-self" if self.board.turn * self.board.flipped == 1 else "move-opponent")

    def _is_capture(self) -> bool:
        """Checks if the move results in a capture."""
        return self.to_tile.piece is not None or (self.board.ep is not None and not self.board.is_empty((self.from_pos[0], self.to_pos[1])) and self.board.get_piece((self.from_pos[0], self.to_pos[1])).is_enemy(self.from_tile.piece))
    
    def is_legal(self) -> bool:
        """Validates if the move is legal according to the game rules."""
        if not self.castling:
            return self.from_tile.can_move(self.board, self.to_pos)
        
        # Castling
        is_legal = True
        d = sign(self.to_pos[1] - self.from_pos[1])
        for next_column in list(range(self.from_pos[1] + d, flip_pos(castling_king_column[d*self.board.flipped], flipped=self.board.flipped) + d, d)):
            condition = self.from_tile.can_move(self.board, (self.from_pos[0], next_column))
            is_legal = is_legal and condition
            if not is_legal:
                break
        return is_legal
    
    def _is_castling(self) -> bool:
        """
        Checks if the move is a castling move.
        """
        if self.from_tile.piece.notation != "K":
            return False
        d = 1 if self.to_tile.pos[1] > self.from_tile.pos[1] else -1
        if (config.rules["chess960"] == False and abs(self.from_pos[1] - self.to_pos[1]) != 2) or (config.rules["chess960"] == True and (not self.capture or self.board.is_empty(self.to_pos) or self.to_tile.piece.notation != "R" or self.from_tile.piece.is_enemy(self.to_tile.piece))):
            return False
        # O-O-O castling's right
        if d == -1 and not self.board.castling[self.from_tile.piece.color][d]:
            return False
        # O-O castling's right
        elif d == 1 and not self.board.castling[self.from_tile.piece.color][d]:
            return False
        return True
    
    def _is_en_passant(self) -> bool:
        """
        Checks if the move is an en passant capture.
        """
        return (
            self.from_tile.piece.notation == "P" and
            self.capture and
            self.board.ep is not None and
            self.to_pos == self.board.ep
            )
        
    def __str__(self) -> str:
        """
        Converts the move into its chess notation.
        """
        string = ""
        # The move is O-O or O-O-O
        if self.castling:
            string += "O" + "-O"*(get_value(sign(self.to_pos[1] - self.from_pos[1]) * self.board.flipped, 1, 2))
        else:
            if self.capture:
                # Add the symbol of the piece
                if self.to_tile.piece.notation != "P":
                    string += self.to_tile.piece.notation
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
                string += "=" + piece_to_notation(self.promotion)
        # Add # if it's checkmate or + if it's a check
        if self.board.is_king_checked():
            if self.board.is_stalemate():
                string += "#"
            else:
                string += "+"
        return string
