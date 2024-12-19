from utils import flip_coords, sign, get_value, play_sound

class Move:
    def __init__(self, board, from_pos, to_pos, castling=False, promotion=None):
        self.board = board
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.from_tile = board.get_tile(from_pos)
        self.to_tile = None
        self.promotion = None
        if board.ep is not None and not board.is_empty(board.ep) and board.get_piece(board.ep).is_enemy(self.from_tile.piece):
            self.to_tile = board.get_tile((to_pos[0] - self.piece.color*self.board.flipped, to_pos[1]))
        elif not board.is_empty(to_pos):
            self.to_tile = board.get_tile(to_pos)
        if self.to[0] in [0, board.config.rows - 1] and self.piece.notation == "P":
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
            self.to = (row, flip_coords(get_value(d, 2, 6), flipped=d*flipped))) """
        self.board.change_turn()
        self.board.selected = None
        # Reset halfMoves if it's a capture or a pawn move
        if self.is_capture() or self.piece.notation == "P":
            self.board.halfMoves = 0
        if self.board.config.rules["+3_checks"] == True and self.board.is_check():
            self.board.win_condition += 1
        self.notation = str(self)
        self.fen = str(self.board)
        self.board.check_game()

    def play_sound(self) -> None:
        if self.is_castling():
            play_sound("castle")
        elif self.board.config.rules["giveaway"] == False and self.board.is_check():
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
        return self.to_tile is not None
    
    def is_legal(self) -> bool:
        if not self.is_castling():
            return self.from_tile.can_move(self.to)
        # Castling
        is_legal = True
        if self.is_castling():
            d = sign(self.to_pos[1] - self.from_pos[1])
            flipped = self.board.flipped
            for next_column in range(min(flip_coords(self.to[1], flipped=d*flipped), flip_coords(get_value(d, 2, 6), flipped=d*flipped)), self.from_pos[1], d*flipped):
                is_legal = is_legal and self.from_tile.can_move((self.from_pos[0], next_column))
                if not is_legal:
                    break
        return is_legal
    
    def is_castling(self) -> bool:
        return self.from_tile.piece.notation == "K" and self.is_capture() and self.to_tile.piece.notation == "R" and self.from_tile.piece.is_ally(self.to_tile.piece) and self.from_tile.piece.first_move and self.to_tile.piece.first_move
    
    def is_en_passant(self) -> bool:
        return self.from_tile.piece.notation == "P" and self.is_capture() and self.board.ep is not None and self.to == self.board.ep
        
    def __str__(self) -> str:
        string = ""
        # The move is O-O or O-O-O
        if self.is_castling():
            string += "O" + "-O"*(get_value(sign(self.to_pos[1] - self.from_pos[1]) * self.board.flipped, 1, 2))
        else:
            if self.is_capture():
                # Add the symbol of the piece
                if self.from_tile.piece.notation != "P":
                    string += self.from_tile.piece.notation
                # Add the starting column if it's a pawn
                else:
                    string += chr(flip_coords(self.from_pos[1], flipped = self.board.flipped) + 97)
                # Add x if it's a capture
                string += "x"
            # Add the destination's column
            string += chr(flip_coords(self.to[1], flipped = self.board.flipped) + 97)
            # Add the destination's row
            string += str(flip_coords(self.to[0], flipped = -self.board.flipped) + 1)
            # Add promotion
            if self.promotion is not None:
                string += "=" + self.promotion.notation
        # Add # if it's checkmate or + if it's a check
        if self.board.is_check():
            if self.board.is_checkmate():
                string += "#"
            else:
                string += "+"
        return string