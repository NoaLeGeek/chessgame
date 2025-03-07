from utils import flip_pos, sign, get_value, debug_print
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
    
    def flip_move(self) -> None:
        """Flips the move's positions."""
        self.from_pos = flip_pos(self.from_pos)
        self.to_pos = flip_pos(self.to_pos)
        self.from_tile = self.board.get_tile(self.from_pos)
        self.to_tile = self.board.get_tile(self.to_pos)

    def execute(self) -> None:
        """Executes the move on the board and updates the game state."""
        self.move()
        # Reset half_moves if it's a capture, castling or a pawn move
        if self.capture or self.castling or (not self.board.is_empty(self.to_pos) and self.to_tile.piece.notation == "P"):
            self.board.half_moves = 0
        # This is the board state after the move
        self.notation = str(self)
        self.fen = str(self.board)
        self.board.check_game()

    def move(self):
        """Moves the piece on the board and updates the game state."""
        # Update the board state
        if self.promotion is not None:
            self.board.promote_piece(self.promotion)
        else:
            self.board._update_castling(self)
            self.board._update_en_passant(self)
            self.board._update_last_irreversible_move(self)
            self.move_piece()
        if self.board.turn == -1:
            self.board.full_moves += 1
        self.board.half_moves += 1
        self.board.turn *= -1
        self.board.selected = None
        self.board.current_player, self.board.waiting_player = self.board.waiting_player, self.board.current_player
        if config.rules["+3_checks"] == True and self.board.current_player.is_king_check(self.board):
            self.board.checks[self.board.waiting_player.color] += 1
        self._play_sound_move()

    def move_piece(self):
        """
        Move a piece on the board and handle special moves like en passant and castling.

        Args:
            move (Move): The move to perform.
        
        This function handles all move types including normal moves, en passant, and castling,
        and updates the board, castling rights, and en passant square accordingly.
        """
        if self.board.is_empty(self.from_pos):
            raise ValueError(f"There is no piece at {self.from_pos}")
        
        # Remember the move for undo
        self.board.move_tree.add(MoveNode(self, self.board.move_tree.current.move, self.board))

        # Update kings' positions
        if self.from_tile.piece.notation == "K":
            self.board.current_player.king = self.to_pos

        # Update player's pieces
        if self.capture and not self.castling and not self.en_passant:
            self.board.waiting_player.remove_piece(self.to_tile.piece)

        # Capture en passant
        if self.en_passant:
            ep_pos = (self.from_pos[0], self.to_pos[1])
            self.board.waiting_player.remove_piece(self.board.board[ep_pos].piece)
            self.board.board[ep_pos].piece = None

        # Handle castling logic
        if self.castling:
            debug_print("Castling move")
            self._handle_castling(self.from_pos, self.to_pos)
        # Handle normal move
        else:
            self._handle_normal_move(self.from_pos, self.to_pos)
        
        # Anarchy chess
        if config.rules["+3_checks"] == True and self.board.current_player.is_king_check(self):
            self.checks[self.board.waiting_player.color] += 1

    def _handle_castling(self, from_pos, to_pos):
        """Handle the logic for castling move."""
        d = sign(to_pos[1] - from_pos[1])
        # Save the pieces
        king = self.board.get_tile(from_pos).piece
        rook_pos = to_pos if config.rules["chess960"] == True else (to_pos[0], (7 if d == 1 else 0))
        rook = self.board.get_tile(rook_pos).piece

        # Destinations columns
        dest_king_column = flip_pos(castling_king_column[d*self.board.flipped], flipped=self.board.flipped)
        dest_rook_column = dest_king_column - d
        
        # Castling move
        self.board.board[from_pos].piece = None
        self.board.board[rook_pos].piece = None
        self.board.board[(from_pos[0], dest_king_column)].piece = king
        self.board.board[(from_pos[0], dest_rook_column)].piece = rook
        
    def _handle_normal_move(self, from_pos, to_pos):
        """Handle a normal move of a piece."""
        save_tile = self.board.get_tile(from_pos)
        self.board.board[to_pos].piece = save_tile.piece
        self.board.board[from_pos].piece = None

    def promote_piece(self, type_piece):
        """
        Promote a pawn to a new piece type.

        Args:
            type_piece: The type of piece to promote to (e.g., Queen, Rook).
        """
        new_piece = type_piece(self.selected.piece.color)
        if config.piece_asset != "blindfold":
            new_piece.image = self.piece_images[("w" if new_piece.color == 1 else "b") + new_piece.notation]
        self.current_player.add_piece(new_piece)
        self.board.board[self.promotion].piece = new_piece
        self.board.board[self.selected.pos].piece = None
        self.promotion = None

    def undo(self) -> None:
        """Undoes the move on the board and updates the game state."""
        self.board.turn *= -1
        self.board.selected = None
        self.board.current_player, self.board.waiting_player = self.board.waiting_player, self.board.current_player
        if config.rules["+3_checks"] == True and self.board.current_player.is_king_check(self.board):
            self.board.checks[self.board.waiting_player.color] -= 1
        if self.promotion is not None:
            self.undo_promote_piece()
        else:
            self.undo_move_piece()
        self.board.half_moves -= 1
        if self.board.turn == -1:
            self.board.full_moves -= 1

    def undo_promote_piece(self):
        """
        Undo the last promotion on the board and restore the pawn to its previous state.
        
        This function reverses the effects of the last promotion, restoring the pawn to its previous state.
        """
        self.board.board[self.from_pos].piece = self.from_tile.piece
        self.board.board[self.to_pos].piece = None
        self.board.waiting_player.remove_piece(self.to_tile.piece)

    def undo_move_piece(self):
        """
        Undo the last move on the board and restore the previous state.
        
        This function reverses the effects of the last move, restoring the board state, castling rights,
        en passant square, and player's pieces to their previous state.
        """
        # Restore the board state
        self.board.board[self.from_pos].piece = self.from_tile.piece
        self.board.board[self.to_pos].piece = self.to_tile.piece

        # Restore king position
        if self.from_tile.piece.notation == "K":
            self.board.current_player.king = self.from_pos

        # Restore player's pieces
        if self.capture and not self.castling and not self.en_passant:
            self.board.waiting_player.add_piece(self.to_tile.piece)

        # Restore en passant capture
        if self.en_passant:
            ep_pos = (self.from_pos[0], self.to_pos[1])
            self.board.board[ep_pos].piece = self.to_tile.piece

    def _play_sound_move(self) -> None:
        """Plays the appropriate sound based on the move type."""
        if self.castling:
            self.board.play_sound("castle")
        elif self.board.current_player.is_king_check(self.board):
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
        if config.rules["giveaway"] == True or self.board.current_player.is_king_check(self.board):
            return False
        is_legal = True
        d = sign(self.to_pos[1] - self.from_pos[1])
        # -1 for O-O-O, 1 for O-O
        castling_direction = d*self.board.flipped
        rook_pos = self.to_pos if config.rules["chess960"] == True else (self.to_pos[0], (7 if d == 1 else 0))
        dest_rook_column = flip_pos(castling_king_column[castling_direction] - castling_direction, flipped=self.board.flipped) * d
        dest_king_column = flip_pos(castling_king_column[castling_direction], flipped=self.board.flipped) * d
        start = d * min(self.from_pos[1] * d, dest_rook_column)
        end = d * max(rook_pos[1] * d, dest_king_column)
        for next_column in range(start + castling_direction, end + castling_direction, castling_direction):
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
        if self.board.current_player.is_king_check(self.board):
            if self.board.is_stalemate():
                string += "#"
            else:
                string += "+"
        return string
    
class MoveNode:
    def __init__(self, move, parent, board):
        self.move = move
        self.parent = parent
        self.children = []
        self.ep = board.ep
        self.castling = board.castling
        self.half_moves = board.half_moves
        self.full_moves = board.full_moves
        self.last_irreversible_move = board.last_irreversible_move

class MoveTree:
    def __init__(self, board):
        self.root = MoveNode(None, None, board)
        self.current = self.root

    def add(self, move_node: MoveNode):
        move_node.parent = self.current
        self.current.children.append(move_node)
        self.go_forward()

    def go_forward(self):
        if self.current.children:
            self.current = self.current.children[0]

    def go_backward(self):
        if self.current.parent:
            self.current.move.undo()
            self.current = self.current.parent

    def go_previous(self):
        if self.current.parent:
            siblings = self.current.parent.children
            index = siblings.index(self.current)
            self.current = siblings[index - 1] if index > 0 else siblings[-1]

    def go_next(self):
        if self.current.parent:
            siblings = self.current.parent.children
            index = siblings.index(self.current)
            self.current = siblings[index + 1] if index < len(siblings) - 1 else siblings[0]

    def go_root(self):
        while self.current.parent:
            self.go_backward()

    def go_leaf(self):
        while self.current.children:
            self.go_forward()

    def get_root_to_leaf(self):
        moves = []
        current = self.current
        while current.parent:
            moves.append(current.move)
            current = current.parent
        return moves[::-1]
    
    def flip_tree(self):
        current = self.current
        while current.parent:
            current.move.flip_move()
            current = current.parent