import pygame
import numpy as np
from board.tile import Tile
from constants import castling_king_column, en_passant_direction
from utils import generate_piece_images, generate_board_image, generate_sounds, flip_pos, sign, debug_print
from board.piece import notation_to_piece, piece_to_notation, piece_to_num
from board.move import Move, MoveTree
from board.player import Player
from random import choice
from config import config

class Board:
    def __init__(self, player1: Player, player2: Player, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        """
        Initialize the chess board with a default or custom FEN string.

        Args:
            fen (str): The FEN string representing the initial board state.
        """
        # Initialize board attributes
        self.board = {}
        self.selected = None
        self.turn = 1
        self.winner = None
        self.ep = None
        self.promotion = None
        self.half_moves = 0
        self.full_moves = 1
        self.flipped = 1
        self.last_irreversible_move = 0
        self.game_over = False
        self.current_player = player1
        self.waiting_player = player2
        self.castling = {1: {1: False, -1: False}, -1: {1: False, -1: False}}

        # Anarchy chess
        if config.rules["+3_checks"] == True:
            self.checks = {1: 0, -1: 0}

        # Load resources
        self.image = generate_board_image()
        self.piece_images = generate_piece_images(self.flipped)
        self.sounds = generate_sounds()

        # Initialize the board from the FEN string
        self._create_board(fen)
        self.move_tree = MoveTree(self)

    def _create_board(self, fen: str) -> None:
        """
        Create the chess board from a FEN string.

        Args:
            fen (str): The FEN string representing the board state.

        Sets:
            - self.board: A dictionary representing the board state.
            - self.turn: 1 for white's turn, -1 for black's turn.
            - self.ep: The en passant target square.
            - self.half_moves: Number of half moves since the last pawn advance or capture.
            - self.full_moves: Number of full moves in the game.
        """
        self.board = {(r, c): Tile((r, c)) for r in range(config.rows) for c in range(config.columns)}
        try:
            # Chess960 row generation
            if config.rules["chess960"] == True:
                fen = self._transform_960_fen(fen)

            fen_parts = fen.split()
            if len(fen_parts) != 6:
                raise ValueError("Invalid FEN format: Must contain exactly 6 parts.")

            # Initialize board state
            self.turn = 1 if fen_parts[1] == "w" else -1
            self._initialize_pieces(fen_parts[0])
            self._initialize_castling(fen_parts[2])
            self.ep = self._parse_en_passant(fen_parts[3])
            self.half_moves = int(fen_parts[4])
            self.full_moves = int(fen_parts[5])
            self.play_sound("game-start")
        except (IndexError, ValueError) as e:
            raise ValueError(f"Failed to parse FEN string: {fen}. Error: {e}")

    def _initialize_pieces(self, board_part: str):
        """
        Initialize pieces on the board from the FEN's board description.

        Args:
            board_part (str): The first part of the FEN string, describing the board state.
        """
        for r, row in enumerate(board_part.split("/")):
            c = 0
            for char in row:
                if char.isdigit():
                    c += int(char)  # Skip empty squares
                else:
                    color = 1 if char.isupper() else -1
                    tile = Tile((r, c))
                    piece_type = notation_to_piece(char)
                    if not piece_type:
                        raise ValueError(f"Invalid piece notation: {char}")

                    piece_image_key = f"{(('w' if color == 1 else 'b') if config.piece_asset != "mono" else "")}{char.upper()}"
                    if piece_image_key not in self.piece_images:
                        raise ValueError(f"Missing piece image for: {piece_image_key}")
                    
                    piece = piece_type(color, self.piece_images[piece_image_key])
                    self.get_player(color).add_piece(piece)
                    tile.piece = piece
                    self.board[(r, c)] = tile

                    # Track the king's position
                    if char.upper() == "K":
                        self.get_player(color).king = (r, c)

                    c += 1

    def _initialize_castling(self, castling_part: str):
        """
        Initialize castling rights from the FEN castling part.

        Args:
            castling_part (str): The third part of the FEN string, describing castling rights.
        """
        if castling_part == "-":
            self.castling = {1: {1: False, -1: False}, -1: {1: False, -1: False}}
            return

        for color in [1, -1]:
            for direction, letter in zip([1, -1], ["K", "Q"]):
                letter = letter.lower() if color == -1 else letter
                if letter in castling_part:
                    rook_position = self._find_rook_for_castling(color, direction)
                    if rook_position:
                        self.castling[color][direction] = True

    def _find_rook_for_castling(self, color: int, direction: int) -> bool:
        """
        Find the rook required for castling and validate its position.

        Args:
            color (int): 1 for white, -1 for black.
            direction (int): 1 for kingside, -1 for queenside.

        Returns:
            bool: True if a valid rook is found for castling, otherwise False.
        """
        row, king_col = self.get_player(color).king
        for col in range(king_col, -1 if direction == -1 else config.columns, direction):
            piece = self.get_piece((row, col))
            if piece and piece.notation == "R" and piece.color == color:
                return True
        return False

    def _parse_en_passant(self, ep_part: str):
        """
        Parse the en passant target square from the FEN string.

        Args:
            ep_part (str): The fourth part of the FEN string, describing the en passant target.

        Returns:
            tuple or None: The en passant square as a (row, column) tuple, or None if not applicable.
        """
        if ep_part in ['-', '–']:
            return None
        if len(ep_part) != 2 or not ep_part[0].isalpha() or not ep_part[1].isdigit():
            raise ValueError(f"Invalid en passant notation: {ep_part}")

        row = flip_pos(int(ep_part[1]) - 1, flipped=-self.flipped)
        col = flip_pos(ord(ep_part[0]) - ord('a'), flipped=self.flipped)
        return row, col    

    def _transform_960_fen(self, fen: str):
        """
        Transform a fen into a Chess960 starting position for the last ranks.

        This function generates a randomized starting position for a Chess960 game
        following the rules:
        - Two bishops must be placed on opposite-colored squares.
        - The king must be placed between the rooks.
        - The remaining pieces (knights and queen) are placed in the empty squares.

        Args:
            fen (str): The FEN of the board configuration.

        Returns:
            list: Updated `fen` with the new Chess960 row included.
        """
        # Initialize the row
        last_row = [None] * config.columns

        # Place the bishops on opposite-colored squares
        light_square_indices = list(range(0, config.columns, 2))
        dark_square_indices = list(range(1, config.columns, 2))
        last_row[choice(light_square_indices)] = "B"
        last_row[choice(dark_square_indices)] = "B"

        # Place the remaining pieces: knights, queen, rooks, and king
        pieces = ["N", "N", "Q"]
        empty_indices = [i for i, val in enumerate(last_row) if val is None]
        for piece in pieces:
            selected_index = choice(empty_indices)
            last_row[selected_index] = piece
            empty_indices.remove(selected_index)
        for piece, index in zip(["R", "K", "R"], sorted(empty_indices)):
            last_row[index] = piece

        fen_parts = fen.split()

        # Update the FEN string for the board
        rows = fen_parts[0].split("/")
        for row in [0, 7]:
            rows[row] = "".join(last_row).lower() if row == 0 else "".join(last_row)
        fen_parts[0] = "/".join(rows)
        return " ".join(fen_parts)
    
    def check_game(self):
        """
        Determine if the game has ended and update the game state accordingly.
        """
        if config.rules["king_of_the_hill"] == True and self.waiting_player.king in self.get_center():
            self.winner = "Black" if self.turn == 1 else "White"
        elif config.rules["+3_checks"] == True and self.checks[-self.turn] >= 3:
            self.winner = "Black" if self.turn == 1 else "White"
        elif config.rules["giveaway"] == True and self.waiting_player.pieces == {}:
            self.winner = "Black" if self.turn == 1 else "White"
        elif self.is_stalemate():
            if self.current_player.is_king_check(self) or config.rules["giveaway"] == True:
                self.winner = "Black" if self.turn == 1 else "White"
            else:
                self.winner = "Stalemate"
        elif self.half_moves >= 100:
            self.winner = "Draw by the 50-move rule"
        elif self.is_insufficient_material():
            self.winner = "Draw by insufficient material"
        elif self.is_threefold_repetition():
            self.winner = "Draw by threefold repetition"
        if self.winner is not None:
            self.game_over = True
            self.play_sound("game-end")
            print(self.winner)

    def is_threefold_repetition(self):
        """
        Check if the current position has been repeated three times.

        Returns:
            bool: True if the position has been repeated three times, otherwise False.
        """
        positions = [move.fen.split(" ")[:4] for move in self.move_tree.get_root_to_leaf()[self.last_irreversible_move:]]
        return any(positions.count(pos) >= 3 for pos in positions)

    def is_stalemate(self):
        """
        Check if the game is in a stalemate state.

        Returns:
            bool: True if the game is a stalemate, otherwise False.
        """
        for tile in list(self.board.values()).copy():
            if not tile.piece or tile.piece.color != self.turn:
                continue
            for move in tile.calc_moves(self):
                if self.convert_to_move(tile.pos, move).is_legal():
                    return False
        return True
    
    def is_insufficient_material(self):
        """
        Check if there is insufficient material to continue the game.

        Returns:
            bool: True if neither player can checkmate, otherwise False.
        """
        piece_count = self.count_pieces()
        # Only kings remain
        if piece_count == 2:
            return True  
        if piece_count == 3:
            return any(
                len(self.get_player(color).pieces.get("B")) == 1 or
                len(self.get_player(color).pieces.get("K")) == 1
                for color in [-1, 1]
            )
        if piece_count == 4:
            if all(len(self.get_player(color).pieces.get("B")) == 1 for color in [-1, 1]):
                square_colors = [self.find_tile("B", color).get_square_color() for color in [-1, 1]]
                if square_colors[0] == square_colors[1]:
                    return True
        return False
    
    def count_pieces(self):
        """
        Count the number of pieces on the board.
        
        Returns:
            int: The number of pieces currently on the board.
        """
        return sum(1 for tile in self.board.values() if tile.piece is not None)
    
    def find_tile(self, notation, color):
        """
        Find the tile on the board that contains a piece matching the given notation and color.
        
        Args:
            notation (str): The notation of the piece (e.g., 'K', 'Q', 'R', etc.).
            color (int): The color of the piece (1 for white, -1 for black).
        
        Returns:
            Tile or None: The tile with the matching piece, or None if no such tile exists.
        """
        return next((tile for tile in self.board.values() if tile.piece and tile.piece.notation == notation and tile.piece.color == color), None)
    
    def convert_to_move(self, from_, to, promotion=None):
        """
        Convert the start and end positions to a Move object, optionally including a promotion.
        
        Args:
            from_ (tuple): The starting position (row, col).
            to (tuple): The target position (row, col).
            promotion (str or None): The piece to promote to, if applicable (e.g., 'Q' for queen).
        
        Returns:
            Move: A Move object representing the move.
        """
        return Move(self, from_, to, promotion)

    def get_tile(self, pos: tuple[int, int]):
        """
        Retrieve the tile at the given position on the board.
        
        Args:
            pos (tuple): The position of the tile as a tuple (row, column).
        
        Returns:
            Tile or None: The tile at the position, or None if the position is invalid.
        """
        return self.board.get(pos, None)
    
    def get_piece(self, pos: tuple[int, int]):
        """
        Retrieve the piece at the given position on the board.
        
        Args:
            pos (tuple): The position of the piece as a tuple (row, column).
        
        Returns:
            Piece or None: The piece at the position, or None if the position is empty.
        """
        try:
            return self.get_tile(pos).piece
        except AttributeError:
            raise ValueError(f"Invalid position: {pos}")
    
    def is_empty(self, pos):
        """
        Check if a position on the board is empty.
        
        Args:
            pos (tuple): The position to check as a tuple (row, column).
        
        Returns:
            bool: True if the position is empty, False otherwise.
        """
        return self.get_piece(pos) is None
    
    def get_empty_tiles(self):
        """
        Get a list of all empty tiles on the board.
        
        Returns:
            list: A list of positions (tuples) representing empty tiles.
        """
        return [pos for pos in self.board if self.is_empty(pos)]
    
    def play_sound(self, type: str):
        """
        Play a sound of the specified type.

        Args:
            type (str): The type of sound to play, e.g., 'illegal', 'notify', etc.
        
        Raises:
            ValueError: If the specified sound type is not found in the sounds dictionary.
        """
        # Check if the sound type exists in the sounds dictionary
        if type not in self.sounds:
            raise ValueError(f"Sound type '{type}' not found in the sound library.")
        self.sounds[type].play()

    def _update_castling(self, move: Move):
        """
        Update castling rights after a move.

        Args:
            move (Move): The move that was played.
        
        Updates the castling rights based on the piece involved in the move.
        """
        piece = move.from_piece
        if piece.notation == "K":
            # If the King moves, reset castling rights for that player
            self.castling[piece.color] = {1: False, -1: False}
        elif piece.notation == "R":
            # If the Rook moves, update the castling rights for that rook's side
            side = 1 if move.from_pos[1] > self.current_player.king[1] else -1
            self.castling[piece.color][side] = False

    def _update_last_irreversible_move(self, move: Move):
        """
        Update the last irreversible move index based on the current move.

        Args:
            move (Move): The move that was played.
        
        Updates the `last_irreversible_move` based on the conditions that make a move irreversible.
        """
        if move.capture or move.from_piece.notation == "P" or move.castling or self.move_tree.current.castling != self.castling:
            # If the move is a capture, pawn move, castling, or a change in castling rights, mark it as irreversible
            self.last_irreversible_move = len(self.move_tree.get_root_to_leaf())

    def _is_valid_en_passant(self, pos: tuple[int, int], ep: tuple[int, int]):
        d_ep = en_passant_direction[ep[0]]
        for d_col in [-1, 1]:
            new_pos = (pos[0], pos[1] + d_col)
            if not self.in_bounds(new_pos) or self.is_empty(new_pos):
                continue
            piece = self.get_piece(new_pos)
            if piece.notation != "P" or piece.color != d_ep*self.flipped:
                continue
            if self.convert_to_move(new_pos, ep).is_legal():
                return True
        return False

    def _update_en_passant(self, move):
        """Update the en passant square logic after a pawn move."""
        from_pos, to_pos = move.from_pos, move.to_pos
        self.ep = None
        if not self.is_empty(from_pos) and self.get_piece(from_pos).notation == "P" and abs(from_pos[0] - to_pos[0]) == 2:
            ep = ((from_pos[0] + to_pos[0]) // 2, from_pos[1])
            if self._is_valid_en_passant((to_pos[0], to_pos[1]), ep):
                self.ep = ep
        
    def select(self, pos: tuple[int, int]):
        """
        Select a piece on the board or execute a move based on the current selection.

        Args:
            pos (tuple[int, int]): The position of the clicked square.
        
        This function handles piece selection, move execution, promotion logic, and special moves like castling.
        """
        if self.selected is not None:
            debug_print("SELECTED", self.selected.pos)
            debug_print("POS", pos)
            debug_print("TRIGGER PROMOTION")
            if self._trigger_promotion(pos):
                return
            debug_print("ALLY PIECE")
            if self._ally_piece(pos):
                return
            debug_print("DESELECT PIECE")
            if self._deselect_piece(pos):
                return
            debug_print("HANDLE ILLEGAL MOVE")
            if self._handle_illegal_move(pos):
                return
            debug_print("SET PROMOTION")
            if self._set_promotion(pos):
                return
            debug_print("EXECUTE MOVE")
            self.convert_to_move(self.selected.pos, pos).execute()
        else:
            self._select_piece(pos)

    def _trigger_promotion(self, pos):
        """Trigger pawn promotion if the selected piece is a pawn."""
        if self.selected.piece.notation == "P" and self.promotion is not None:
            d = self.selected.piece.color * self.flipped
            if pos[0] in range(flip_pos(0, flipped=d), flip_pos(0, flipped=d) + d*len(self.selected.piece.promotion), d) and pos[1] == self.promotion[1]:
                self.convert_to_move(self.selected.pos, self.promotion, self.selected.piece.promotion[flip_pos(pos[0], flipped=d)]).execute()
                return True
            # Cancel promotion if the player doesn't click in the range of promotion
            self.promotion = None
            self.selected = None
            return True
        return False

    def _ally_piece(self, pos):
        """Handle the case when the player clicks on an ally piece."""
        if not self.is_empty(pos) and self.get_piece(pos).is_ally(self.selected.piece) and pos != self.selected.pos:
            # Castling move
            if self.selected.piece.notation == "K" and not self.is_empty(pos) and self.get_piece(pos).notation == "R" and pos in self.selected.calc_moves(self):
                self.convert_to_move(self.selected.pos, pos).execute()
                return True
            self.selected = None
            self.select(pos)
            return True
        return False

    def _deselect_piece(self, pos):
        """Deselect the piece if the player clicks on it again or on an invalid position."""
        if pos == self.selected.pos or not self.in_bounds(pos):
            self.selected = None
            return True
        return False

    def _handle_illegal_move(self, pos):
        """Handle illegal moves (either not in the possible moves or king is checked)."""
        if pos not in list(map(lambda move: move.to_pos, self.selected.piece.moves)):
            self.selected = None
            if self.current_player.is_king_check(self):
                self.play_sound("illegal")
            if not self.is_empty(pos) and self.get_piece(pos).color == self.turn:
                self.select(pos)
            return True
        return False
    
    def _set_promotion(self, pos):
        """Set the promotion square if the selected piece is a pawn and reaches the last rank."""
        if self.selected.piece.notation == "P" and pos[0] in [0, config.rows - 1]:
            self.promotion = pos
            return True
        return False

    def _select_piece(self, pos):
        """Select a new piece if it belongs to the current player."""
        if self.is_empty(pos) or self.get_piece(pos).color != self.turn:
            return
        self.selected = self.get_tile(pos)
        self.selected.piece.moves = self._filter_moves(self.selected)

    def _filter_moves(self, tile):
        """Filter the legal moves for the selected piece."""
        moves = list(map(lambda move: self.convert_to_move(tile.pos, move), tile.piece.moves))
        if config.rules["giveaway"] == True:
            if any(self.convert_to_move(tile.pos, move).capture for move in self.current_player.get_moves(self)):
                return list(filter(lambda move: move.capture, moves))
            else:
                return list(filter(lambda move: not move.castling, moves))
        else:
            return list(filter(lambda move: move.is_legal(), moves))

    def in_bounds(self, pos: tuple[int, int]) -> bool:
        """
        Check if a position is within the bounds of the board.

        Args:
            pos (tuple[int, int]): The position to check.
        
        Returns:
            bool: True if the position is within the board's bounds, False otherwise.
        """
        return self.get_tile(pos) is not None
    
    def flip_board(self) -> None:
        """
        Flip the board horizontally and update all necessary board elements.
        This function also updates the pieces, kings' positions, en passant square, and last move.
        """
        self._flip_board_tiles()
        self.flipped *= -1
        # Remove the highlight of the selected piece
        if self.selected is not None:
            self.selected.highlight_color = None
            self.selected = None
        self.promotion = None
        # Flipping the kings' positions
        for color in [1, -1]:
            player = self.get_player(color)
            player.king = flip_pos(player.king)
        # Flipping the en passant square
        if self.ep:
            self.ep = flip_pos(self.ep)
        # Flipping the move tree
        self.move_tree.flip_tree()
        # Regenerating the piece images depending on the flipped state
        if config.flipped_assets:
            self.piece_images = generate_piece_images(self.flipped)
            self.update_images()
        # Flipping the board image
        self.image = pygame.transform.flip(self.image, True, False)

    def _flip_board_tiles(self):
        """Flip all tiles and update their positions on the board."""
        flipped_board = {}
        for pos, tile in self.board.items():
            tile.flip()
            flipped_board[flip_pos(pos)] = tile
        self.board = flipped_board

    def update_images(self):
        """
        Update the images of all pieces on the board according to the current flipped state.
        """
        for tile in self.board.values():
            tile.piece.update_image(self.piece_images[("w" if tile.piece.color == 1 else "b") + tile.piece.notation])

    def get_player(self, color: int) -> Player:
        """
        Get the player object based on the color.

        Args:
            color (int): The color of the player (1 for white, -1 for black).

        Returns:
            Player: The player object corresponding to the color.
        """
        return self.current_player if color == self.turn else self.waiting_player

    def highlight_tile(self, highlight_color: int, *list_pos):
        """
        Highlight a tile on the board with a specific color.

        Args:
            list_pos (tuple[int, int] | list[tuple[int, int]]): The position of the tile to highlight.
            highlight_color (int): The color to highlight the tile with.
        """
        for pos in list_pos:
            tile = self.get_tile(pos)
            if tile.highlight_color != highlight_color:
                tile.highlight_color = highlight_color
            else:
                tile.highlight_color = None
                last_move = self.get_last_move()
                if last_move is not None:
                    to_pos = last_move.to_pos if not last_move.castling else (last_move.to_pos[0], flip_pos(castling_king_column[(1 if last_move.to_pos[1] > last_move.from_pos[1] else -1)*self.flipped], flipped=self.flipped))
                    if pos in [last_move.from_pos, to_pos]:
                        tile.highlight_color = 3
                if self.selected is not None and self.selected.piece is not None:
                    tile.highlight_color = 4

    def clear_highlights(self):
        """Clear all highlighted tiles on the board."""
        for tile in self.board.values():
            tile.highlight_color = None

    def get_last_move(self):
        """
        Get the last move that was played on the board.

        Returns:
            Move or None: The last move that was played, or None if no move has been played yet.
        """
        return self.move_tree.current.move
    
    def get_center(self) -> list[tuple[int, int]]:
        """
        Get the center position of the board.

        Returns:
            list[tuple[int, int]]: The center position(s) of the board.
        """
        mid_x, mid_y = (config.columns - 1) // 2, (config.rows - 1) // 2
        return [(mid_x + i, mid_y + j) for i in range(2 - config.columns % 2) for j in range(2 - config.rows % 2)]

    # FEN format
    def __str__(self):
        """Return the FEN string of the board state."""
        fen = []
        for row in range(config.rows):
            empty = 0
            row_fen = ""
            for col in range(config.columns):
                piece = self.get_piece((row, col))
                if piece is not None:
                    if empty > 0:
                        row_fen += str(empty)
                        empty = 0
                    row_fen += piece_to_notation(type(piece)) if piece.color == 1 else piece_to_notation(type(piece)).lower()
                else:
                    empty += 1
            if empty:
                row_fen += str(empty)
            fen.append(row_fen)
        fen = "/".join(fen)
        turn = "w" if self.turn == 1 else "b"
        castling = "".join(
            k for color in [1, -1] for k in ("KQ" if color == 1 else "kq") if self.castling[color][1 if k.upper() == "K" else -1]
        ) or "-"
        en_passant = "-"
        if self.ep is not None:
            d_ep = en_passant_direction[self.ep[0]]
            if self._is_valid_en_passant((self.ep[0] + d_ep, self.ep[1]), self.ep):
                en_passant = chr(97 + flip_pos(self.ep[1], flipped = self.flipped)) + str(flip_pos(self.ep[0], flipped = -self.flipped) + 1)
        return f"{fen} {turn} {castling} {en_passant} {self.half_moves} {self.full_moves}"

    def to_matrix(self):
        matrix = np.zeros((14, 8, 8))
        for pos, tile in self.board.items():
            piece = tile.piece
            if piece:
                channel = piece_to_num(type(piece))
                if piece.color == -1:
                    channel += 6
                matrix[channel, pos[0], pos[1]] = 1
                if piece.color == self.turn:
                    moves = piece.calc_moves(self, pos)
                    if moves:
                        legal_moves = 0
                        for move in moves:
                            if self.convert_to_move(pos, move).is_legal():
                                matrix[13, move[0], move[1]] = 1 
                                legal_moves += 1
                            if legal_moves:       
                                matrix[12, pos[0], pos[1]] = 1                 
        return matrix

    def convert_uci_to_move(self, uci_move):
        columns = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
        from_pos = (8-int(uci_move[1]), columns[uci_move[0]])
        to_pos = (8-int(uci_move[3]), columns[uci_move[2]])
        return self.convert_to_move(from_pos, to_pos)