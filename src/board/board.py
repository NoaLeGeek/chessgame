from random import choice
from math import ceil

import pygame
import numpy as np

from gui import Label
from config import config
from board.tile import Tile
from board.player import Player
from ia.negamax import NegamaxAI
from board.move import Move, MoveTree
from constants import castling_king_column, en_passant_direction, Fonts, Colors
from board.piece import notation_to_piece, piece_to_notation, piece_to_num
from utils import generate_piece_images, generate_board_image, generate_sounds, flip_pos, play_sound

class Board:
    def __init__(self, current_player: Player, waiting_player: Player, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        """
        Initializes the Board object, setting up the chessboard, players, and game state.
        Parameters:
            current_player (Player): The player whose turn it is to play.
            waiting_player (Player): The player waiting for their turn.
            fen (str): The FEN (Forsyth-Edwards Notation) string representing the initial state of the board.
                       Defaults to the standard starting position.
        Attributes:
            board (dict): A dictionary representing the chessboard and its tiles.
            selected (Tile | None): The currently selected tile on the board, if any.
            turn (int): The current turn number.
            winner (None | str): The winner of the game, if the game is over.
            ep (None | tuple[int, int]): The en passant square's pos, if applicable.
            promotion (None | tuple[int, int]): The pos to which a pawn will be promoted, if applicable.
            half_moves (int): The number of half-moves since the last capture or pawn move.
            full_moves (int): The number of full moves in the game.
            flipped (int): Indicates whether the board is flipped (1 for normal, -1 for flipped).
            last_irreversible_move (int): The turn number of the last irreversible move.
            game_over (bool): Indicates whether the game is over.
            current_player (Player): The player whose turn it is to play.
            waiting_player (Player): The player waiting for their turn.
            castling (dict): A dictionary tracking castling rights for both players.
            score (int): The current evaluation score of the board.
            negamax (NegamaxAI): The AI engine used to evaluate the board.
            checks (dict): Tracks the number of checks for each player (used in "+3_checks" rule).
                           Only initialized if the "+3_checks" rule is enabled in the configuration.
            image: The visual representation of the chessboard.
            piece_images: The images of the chess pieces, adjusted for board orientation.
            sounds: The sound effects used during the game.
            move_tree (MoveTree): The tree structure used to manage possible moves.
            history_change (bool): Indicates whether the game history has changed.
            history (list): A list of moves made during the game.
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
        self.current_player = current_player
        self.waiting_player = waiting_player
        self.castling = {1: {1: False, -1: False}, -1: {1: False, -1: False}}
        self.score = 0
        self.negamax = NegamaxAI(0, 0)

        # Anarchy chess
        if config.rules["+3_checks"] == True:
            self.checks = {1: 0, -1: 0}

        # Load resources
        self.image = generate_board_image()
        self.piece_images = generate_piece_images(self.flipped)
        self.sounds = generate_sounds()

        # Initialize the board from the FEN string
        self.move_tree = MoveTree(self)

        self.history_change = False
        self.history = []
        self._create_board(fen)

        # IA plays first if the white player is an IA
        if self.current_player.ia == True:
            self.current_player.play_move(self)

    def _create_board(self, fen: str) -> None:
        """
        Initializes the chess board state based on the provided FEN (Forsyth-Edwards Notation) string.
        This method sets up the board tiles, pieces, turn, castling rights, en passant target square, 
        half-move clock, and full-move number. It also supports Chess960 (Fischer Random Chess) 
        if enabled in the configuration. If the FEN string is invalid, an exception is raised.
        Parameters:
            fen (str): A string in FEN format that describes the initial state of the chess board.
        Raises:
            ValueError: If the FEN string is invalid or cannot be parsed.
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
            play_sound(self.sounds, "game-start")
        except (IndexError, ValueError) as e:
            raise ValueError(f"Failed to parse FEN string: {fen}. Error: {e}")

    def _initialize_pieces(self, board_part: str):
        """
        Initializes the chess pieces on the board based on the given board notation.
        This function parses a board representation string in Forsyth-Edwards Notation (FEN) format 
        for the piece placement section and sets up the board with the appropriate pieces. It also 
        assigns images to the pieces if the configuration specifies a visual representation and 
        tracks the position of the kings for each player.
        Args:
            board_part (str): A string representing the piece placement on the board in FEN format. 
                              Each row is separated by a forward slash ('/'), and empty squares are 
                              denoted by numbers.
        Raises:
            ValueError: If an invalid piece notation is encountered or if a required piece image 
                        is missing from the configuration.
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
                    piece = piece_type(color)
                    if config.piece_asset != "blindfold":
                        piece_image_key = f"{(('w' if color == 1 else 'b') if config.piece_asset != "mono" else "")}{char.upper()}"
                        if piece_image_key not in self.piece_images:
                            raise ValueError(f"Missing piece image for: {piece_image_key}")
                        piece.image = self.piece_images[piece_image_key]
                    self.get_player(color).add_piece(piece)
                    tile.piece = piece
                    self.board[(r, c)] = tile

                    # Track the king's position
                    if char.upper() == "K":
                        self.get_player(color).king = (r, c)

                    c += 1

    def _initialize_castling(self, castling_part: str):
        """
        Initializes the castling rights for the chessboard based on the provided castling notation.
        This function sets up the castling rights for both players (white and black) 
        and both directions (king-side and queen-side). If no castling rights are 
        available (indicated by "-"), all castling options are set to False. Otherwise, 
        it determines the castling rights based on the provided notation and the 
        positions of the rooks.
        Parameters:
            castling_part (str): A string representing the castling rights in standard 
                                 chess notation. For example:
                                 - "KQkq" indicates all castling rights are available.
                                 - "KQ" indicates only white's castling rights are available.
                                 - "-" indicates no castling rights are available.
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
        Determines if a rook is available for castling in the specified direction.

        This function checks the row of the king for the given player color and 
        iterates in the specified direction to find a rook that belongs to the 
        same player and is eligible for castling.

        Args:
            color (int): The color of the player (e.g., 0 for white, 1 for black).
            direction (int): The direction to search for the rook. 
                             Use -1 for left and 1 for right.

        Returns:
            bool: True if a rook is found in the specified direction that is 
                  eligible for castling, False otherwise.
        """
        row, king_col = self.get_player(color).king
        for col in range(king_col, -1 if direction == -1 else config.columns, direction):
            piece = self.get_piece((row, col))
            if piece and piece.notation == "R" and piece.color == color:
                return True
        return False

    def _parse_en_passant(self, ep_part: str):
        """
        Parses the en passant notation from a FEN string and converts it into 
        board coordinates.
        En passant is a special pawn capture move in chess. This function 
        interprets the en passant target square provided in the FEN string 
        and returns its corresponding row and column on the board.
        Parameters:
            ep_part (str): The en passant target square in FEN notation. 
                           It can be a valid square (e.g., "e3") or '-'/'–' 
                           if no en passant target square exists.
        Returns:
            tuple or None: A tuple (row, col) representing the board coordinates 
                           of the en passant target square, or None if no en passant 
                           target square is specified.
        Raises:
            ValueError: If the provided en passant notation is invalid.
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
        Transforms a standard FEN string into a Chess960-compatible FEN string by 
        rearranging the back rank pieces according to Chess960 rules.
        This function modifies the placement of the pieces on the first and last 
        ranks to comply with Chess960 (Fischer Random Chess) rules, ensuring that 
        the bishops are on opposite-colored squares, and the king is placed between 
        the rooks.
        Parameters:
            fen (str): The standard FEN string representing the current state of 
                       the chessboard.
        Returns:
            str: A modified FEN string with the back rank pieces rearranged for 
                 Chess960.
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
        Checks the current state of the chess game and determines if the game has ended.
        Updates the winner and game_over attributes accordingly based on the rules and 
        conditions of the game.

        This function evaluates various endgame conditions such as special rules 
        (e.g., "king of the hill", "+3 checks", "giveaway"), stalemates, draws 
        (e.g., 50-move rule, insufficient material, threefold repetition), and 
        determines the winner or if the game ends in a draw.
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
            play_sound(self.sounds, "game-end")

    def is_threefold_repetition(self):
        """
        Determines if the current board position has occurred at least three times,
        indicating a threefold repetition, which is a condition for a draw in chess.

        Returns:
        bool: True if a threefold repetition is detected, False otherwise.
        """
        positions = [move.fen.split(" ")[:4] for move in self.move_tree.get_root_to_leaf()[self.last_irreversible_move:]]
        return any(positions.count(pos) >= 3 for pos in positions)

    def is_stalemate(self):
        """
        Determines if the current game state is a stalemate.

        A stalemate occurs when the current player has no legal moves available,
        but their king is not in check. This function checks the number of legal
        moves for the current player to determine if a stalemate condition exists.

        Returns:
            bool: True if the game is in a stalemate, False otherwise.
        """
        return len(self.current_player.get_legal_moves(self)) == 0
    
    def is_insufficient_material(self):
        """
        Determines if the current board state constitutes insufficient material 
        to checkmate, which would result in a draw according to chess rules.

        This function checks the number and type of pieces remaining on the board 
        to identify scenarios where checkmate is impossible. The conditions checked 
        include:
        - Only kings remain on the board.
        - One side has a king and a single bishop or knight.
        - Both sides have a king and a bishop, and the bishops are on squares of 
          the same color.

        Returns:
            bool: True if the board state represents insufficient material to 
            checkmate, otherwise False.
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
        Counts the total number of pieces currently on the board.

        This method iterates through all the tiles on the board and checks if a piece is present on each tile.
        It returns the total count of tiles that have a piece.

        Returns:
            int: The total number of pieces on the board.
        """
        return sum(1 for tile in self.board.values() if tile.piece is not None)
    
    def find_tile(self, notation, color):
        """
        Finds and returns a tile on the board that contains a piece matching the specified notation and color.

        Parameters:
            notation (str): The notation of the piece to search for (e.g., 'K' for King, 'Q' for Queen).
            color (str): The color of the piece to search for (e.g., 'white', 'black').

        Returns:
            Tile: The tile object containing the piece that matches the given notation and color, or None if no such tile exists.
        """
        return next((tile for tile in self.board.values() if tile.piece and tile.piece.notation == notation and tile.piece.color == color), None)
    
    def convert_to_move(self, from_pos, to_pos, promotion=None):
        """
        Converts the given positions into a Move object.

        This function creates and returns a Move object based on the 
        starting position (`from_pos`), the target position (`to_pos`), 
        and an optional promotion piece.

        Parameters:
            from_pos (tuple): A tuple representing the starting position 
                              of the move (e.g., (row, column)).
            to_pos (tuple): A tuple representing the target position 
                            of the move (e.g., (row, column)).
            promotion (str, optional): A string representing the piece 
                                       to promote to, if applicable 
                                       (e.g., 'Q' for Queen). Defaults to None.

        Returns:
            Move: An instance of the Move class representing the move.
        """
        return Move(self, from_pos, to_pos, promotion)

    def get_tile(self, pos: tuple[int, int]):
        """
        Retrieves the tile at the specified position on the board.

        Args:
            pos (tuple[int, int]): A tuple representing the position on the board 
                where the first element is the row index and the second element 
                is the column index.

        Returns:
            The tile object at the specified position if it exists, otherwise None.
        """
        return self.board.get(pos, None)
    
    def get_piece(self, pos: tuple[int, int]):
        """
        Retrieves the piece located at the specified position on the board.

        Args:
            pos (tuple[int, int]): A tuple representing the position on the board 
                in the format (row, column).

        Returns:
            The piece object located at the specified position.

        Raises:
            ValueError: If the position is invalid or does not correspond to a valid tile.
        """
        try:
            return self.get_tile(pos).piece
        except AttributeError:
            raise ValueError(f"Invalid position: {pos}")
    
    def is_empty(self, pos):
        """
        Checks if a given position on the board is empty.

        Args:
            pos (tuple): A tuple representing the position on the board 
                         (e.g., (row, column)).

        Returns:
            bool: True if the position is empty (no piece is present), 
                  False otherwise.
        """
        return self.get_piece(pos) is None

    def _update_castling(self, move: Move):
        """
        Updates the castling rights based on the given move.

        This function modifies the castling rights for the current player
        depending on the type of piece that is moved and its position. If a King
        moves, all castling rights for that player are reset. If a Rook moves,
        the castling rights for the corresponding side (king-side or queen-side)
        are updated.

        Parameters:
            move (Move): An object representing the move being made. It contains
                         information about the moving piece, its starting position,
                         and its destination.
        """
        piece = move.moving_piece
        if piece.notation == "K":
            # If the King moves, reset castling rights for that player
            self.castling[piece.color] = {1: False, -1: False}
        elif piece.notation == "R":
            # If the Rook moves, update the castling rights for that rook's side
            side = 1 if move.from_pos[1] > self.current_player.king[1] else -1
            self.castling[piece.color][side] = False

    def _update_last_irreversible_move(self, move: Move):
        """
        Updates the index of the last irreversible move in the game.

        This method determines whether the given move is irreversible and updates
        the `last_irreversible_move` attribute accordingly. A move is considered
        irreversible if it is a capture, a pawn move, a castling move, or if it
        changes the castling rights.

        Parameters:
            move (Move): The move to evaluate for irreversibility. This object
            contains details about the move, such as whether it is a capture,
            the piece being moved, and whether it involves castling.
        """
        if move.is_capture() or move.moving_piece.notation == "P" or move.castling or self.move_tree.current.castling != self.castling:
            # If the move is a capture, pawn move, castling, or a change in castling rights, mark it as irreversible
            self.last_irreversible_move = len(self.move_tree.get_root_to_leaf())

    def _is_valid_en_passant(self, pos: tuple[int, int], ep: tuple[int, int]):
        """
        Determines whether an en passant move is valid for a given position and target square.

        This function checks if an en passant capture is possible based on the current board state,
        the position of the pawn attempting the capture, and the en passant target square. It ensures
        that the move adheres to the rules of chess for en passant captures.

        Parameters:
            pos (tuple[int, int]): The current position of the pawn attempting the en passant capture,
                                   represented as a tuple (row, column).
            ep (tuple[int, int]): The en passant target square, represented as a tuple (row, column).

        Returns:
            bool: True if the en passant move is valid, False otherwise.
        """
        d_ep = en_passant_direction[ep[0]]
        for d_col in [-1, 1]:
            new_pos = (pos[0], pos[1] + d_col)
            if not self.in_bounds(new_pos) or self.is_empty(new_pos):
                continue
            piece = self.get_piece(new_pos)
            if piece.notation != "P" or piece.color != d_ep*self.flipped:
                continue
            if self.convert_to_move(new_pos, ep).is_legal(self):
                return True
        return False

    def _update_en_passant(self, move):
        """
        Updates the en passant target square based on the given move.

        This function determines whether an en passant target square should be set
        after a pawn moves two squares forward. If the conditions for en passant
        are met, the target square is updated accordingly.

        Parameters:
            move (Move): An object representing the move being made. It contains:
                - from_pos (tuple): The starting position of the move as (row, column).
                - to_pos (tuple): The ending position of the move as (row, column).
        """
        from_pos, to_pos = move.from_pos, move.to_pos
        self.ep = None
        if not self.is_empty(from_pos) and self.get_piece(from_pos).notation == "P" and abs(from_pos[0] - to_pos[0]) == 2:
            ep = ((from_pos[0] + to_pos[0]) // 2, from_pos[1])
            if self._is_valid_en_passant((to_pos[0], to_pos[1]), ep):
                self.ep = ep
        
    def select(self, pos: tuple[int, int]):
        """
        Handles the selection and movement of pieces on the chessboard.

        This function manages the logic for selecting a piece, handling promotions, 
        deselecting a piece, checking for illegal moves, and executing valid moves. 
        It also allows selecting a new piece if no piece is currently selected.

        Parameters:
            pos (tuple[int, int]): The position on the board being interacted with, 
                                   represented as a tuple of (row, column).
        """
        if self.selected is not None:
            if self._trigger_promotion(pos):
                return
            if self._ally_piece(pos):
                return
            if self._deselect_piece(pos):
                return
            if self._handle_illegal_move(pos):
                return
            if self._set_promotion(pos):
                return
            self.convert_to_move(self.selected.pos, pos).execute(self)
        else:
            self._select_piece(pos)

    def _trigger_promotion(self, pos):
        """
        Handles the promotion of a pawn when it reaches the promotion rank.

        This function checks if the currently selected piece is a pawn eligible for promotion 
        and if the player has clicked within the valid promotion range. If the conditions are met, 
        the pawn is promoted to the selected piece type. If the player clicks outside the promotion 
        range, the promotion is canceled.

        Parameters:
            pos (tuple): A tuple representing the position (row, column) where the player clicked.

        Returns:
            bool: True if a promotion action (either execution or cancellation) was triggered, 
                  False otherwise.
        """
        if self.selected.piece.notation == "P" and self.promotion is not None:
            d = self.selected.piece.color * self.flipped
            if pos[0] in range(flip_pos(0, flipped=d), flip_pos(0, flipped=d) + d*len(self.selected.piece.promotion), d) and pos[1] == self.promotion[1]:
                self.convert_to_move(self.selected.pos, self.promotion, self.selected.piece.promotion[flip_pos(pos[0], flipped=d)]).execute(self)
                return True
            # Cancel promotion if the player doesn't click in the range of promotion
            self.promotion = None
            self.selected = None
            return True
        return False

    def _ally_piece(self, pos):
        """
        Handles the selection of an allied piece on the chessboard.

        This method checks if the given position contains an allied piece 
        (excluding the currently selected piece) and performs actions 
        such as castling or updating the selected piece accordingly.

        Parameters:
            pos (tuple): The position on the chessboard to check, represented 
                         as a tuple of coordinates (e.g., (x, y)).

        Returns:
            bool: True if an allied piece is successfully selected or a 
                  castling move is executed, False otherwise.
        """
        if not self.is_empty(pos) and self.get_piece(pos).is_ally(self.selected.piece) and pos != self.selected.pos:
            # Castling move
            if self.selected.piece.notation == "K" and not self.is_empty(pos) and self.get_piece(pos).notation == "R" and pos in self.selected.calc_moves(self):
                self.convert_to_move(self.selected.pos, pos).execute(self)
                return True
            self.selected = None
            self.select(pos)
            return True
        return False

    def _deselect_piece(self, pos):
        """
        Deselects the currently selected piece on the board.

        This method checks if the given position matches the position of the currently 
        selected piece or if the position is out of bounds. If either condition is met, 
        it deselects the piece by setting `self.selected` to `None`.

        Parameters:
            pos (tuple): A tuple representing the position on the board (row, column) 
                         to check for deselection.

        Returns:
            bool: True if the piece was deselected, False otherwise.
        """
        if pos == self.selected.pos or not self.in_bounds(pos):
            self.selected = None
            return True
        return False

    def _handle_illegal_move(self, pos):
        """
        Handles the scenario where an illegal move is attempted in the chess game.

        This function checks if the given position `pos` is not a valid move for the currently 
        selected piece. If the move is illegal, it deselects the current piece, plays an 
        "illegal move" sound if the current player's king is in check, and optionally selects 
        another piece if the position contains a piece of the current player's color.

        Parameters:
            pos (tuple): The position being checked for legality, represented as a tuple.

        Returns:
            bool: True if the move is illegal and handled, False otherwise.
        """
        if pos not in [move.to_pos for move in self.selected.piece.moves]:
            self.selected = None
            if self.current_player.is_king_check(self):
                play_sound(self.sounds, "illegal")
            if not self.is_empty(pos) and self.get_piece(pos).color == self.turn:
                self.select(pos)
            return True
        return False
    
    def _set_promotion(self, pos):
        """
        Checks if a pawn has reached the promotion rank and sets the promotion position.

        This method determines if the currently selected piece is a pawn ("P") and if it has 
        reached the last rank (either the first row or the last row of the board). If both 
        conditions are met, it sets the promotion position and returns True. Otherwise, it 
        returns False.

        Parameters:
            pos (tuple): A tuple representing the position on the board (row, column) 
                         where the piece is being moved.

        Returns:
            bool: True if the pawn is eligible for promotion and the promotion position 
                  is set, False otherwise.
        """
        if self.selected.piece.notation == "P" and pos[0] in [0, config.rows - 1]:
            self.promotion = pos
            return True
        return False

    def _select_piece(self, pos):
        """
        Selects a piece on the board if it belongs to the current player and is not on an empty tile.

        This method checks if the specified position contains a piece belonging to the current player's turn.
        If so, it sets the selected tile and filters the possible moves for the selected piece.

        Parameters:
            pos (tuple): A tuple representing the position on the board (e.g., (row, column)).
        """
        if self.is_empty(pos) or self.get_piece(pos).color != self.turn:
            return
        self.selected = self.get_tile(pos)
        self.selected.piece.moves = self._filter_moves(self.selected)

    def _filter_moves(self, tile):
        """
        Filters the possible moves for a given tile based on the current game rules.

        This function generates a list of valid moves for the piece on the specified tile,
        applying additional filtering based on the game mode and rules. For example, in
        "giveaway" mode, the function prioritizes capture moves if no capture moves are
        available for the current player.

        Parameters:
            tile (Tile): The tile object containing the piece for which moves are being calculated.
                         The tile must have a `pos` attribute representing its position and a `piece`
                         attribute with a `calc_moves` method to calculate potential moves.

        Returns:
            list[Move]: A list of filtered Move objects that are valid for the current game state.
        """
        moves = [self.convert_to_move(tile.pos, move) for move in tile.piece.calc_moves(self, tile.pos)]
        if config.rules["giveaway"] == True:
            if len([move for move in self.current_player.get_moves() if move.is_capture()]) == 0:
                return [move for move in moves if move.is_capture()]
            else:
                return list(filter(lambda move: not move.castling, moves))
        else:
            return [move for move in moves if move.is_legal(self)]

    def in_bounds(self, pos: tuple[int, int]) -> bool:
        """
        Checks if a given position is within the bounds of the board.

        Args:
            pos (tuple[int, int]): A tuple representing the position on the board,
                where the first element is the row index and the second element is the column index.

        Returns:
            bool: True if the position is within the bounds of the board, False otherwise.
        """
        return self.get_tile(pos) is not None
    
    def flip_board(self) -> None:
        """
        Flips the chessboard state, including the visual representation, 
        piece positions, and game-related attributes.

        This function is used to invert the board's orientation, which is 
        particularly useful in two-player games where the board needs to 
        be flipped after each turn. It updates the internal state of the 
        board, regenerates piece images if necessary, and ensures all 
        positional attributes are correctly flipped.

        - Flips the board tiles and updates the flipped state.
        - Clears the highlight of the selected piece and resets the selection.
        - Resets any ongoing promotion state.
        - Flips the positions of the kings for both players.
        - Adjusts the en passant square if it exists.
        - Flips the move tree to maintain consistency with the flipped board.
        - Regenerates piece images if flipped assets are enabled in the configuration.
        - Flips the visual representation of the board image.
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
        """
        Flips the board tiles and updates their positions.

        This method iterates through all the tiles on the board, flips each tile's state,
        and reassigns them to their new positions based on a flipped coordinate system.
        The board is then updated with the flipped tiles.
        """
        flipped_board = {}
        for pos, tile in self.board.items():
            tile.flip()
            flipped_board[flip_pos(pos)] = tile
        self.board = flipped_board

    def update_images(self):
        """
        Updates the images of all pieces on the board.

        This method iterates through all the tiles on the board and updates the 
        image of each piece based on its color and notation. The images are 
        retrieved from the `piece_images` dictionary using a key composed of 
        the piece's color ('w' for white, 'b' for black) and its notation.
        """
        for tile in self.board.values():
            tile.piece.update_image(self.piece_images[("w" if tile.piece.color == 1 else "b") + tile.piece.notation])

    def get_player(self, color: int) -> Player:
        """
        Retrieves the player object based on the specified color.

        This function determines which player (current or waiting) corresponds
        to the given color and returns the appropriate player object.

        Parameters:
            color (int): The color of the player to retrieve. Typically, this
                         would be an integer representing a specific color (e.g., 0 for white, 1 for black).

        Returns:
            Player: The player object corresponding to the specified color.
        """
        return self.current_player if color == self.turn else self.waiting_player

    def highlight_tile(self, highlight_color: int, *list_pos):
        """
        Highlights specific tiles on the chessboard based on the provided positions and conditions.

        This function updates the highlight color of tiles at the specified positions. If a tile's current 
        highlight color matches the provided highlight color, it resets the highlight. Additionally, it 
        applies specific highlight rules for the current move and the selected piece.

        Parameters:
            highlight_color (int): The color code to use for highlighting the tiles.
            *list_pos: A variable number of positional arguments representing the positions of the tiles 
                       to be highlighted. Each position is expected to be in a format compatible with 
                       the `get_tile` method.

        Behavior:
            - If the tile's current highlight color matches the provided color, it resets the highlight.
            - If the tile corresponds to the current move's starting or ending position, it applies a 
              specific highlight color (3).
            - If a tile corresponds to the currently selected piece, it applies a specific highlight 
              color (4).
        """
        for pos in list_pos:
            tile = self.get_tile(pos)
            if tile.highlight_color != highlight_color:
                tile.highlight_color = highlight_color
            else:
                tile.highlight_color = None
                current_move = self.get_current_move()
                if current_move is not None:
                    to_pos = current_move.to_pos if not current_move.castling else (current_move.to_pos[0], flip_pos(castling_king_column[(1 if current_move.to_pos[1] > current_move.from_pos[1] else -1)*self.flipped], flipped=self.flipped))
                    if pos in [current_move.from_pos, to_pos]:
                        tile.highlight_color = 3
                if self.selected is not None and self.selected.piece is not None:
                    tile.highlight_color = 4

    def clear_highlights(self):
        """
        Clears all highlight colors from the tiles on the board.

        This method iterates through all the tiles in the board and resets their
        `highlight_color` attribute to `None`, effectively removing any visual
        highlights.
        """
        for tile in self.board.values():
            tile.highlight_color = None

    def update_highlights(self):
        """
        Updates the highlighted tiles on the chessboard.

        This function clears any existing highlights, determines the current move,
        and highlights the relevant tiles based on the move or the currently selected piece.
        It handles special cases such as castling moves by calculating the appropriate
        positions to highlight.

        - Clears previous highlights on the board.
        - Highlights the tiles involved in the current move (if any).
        - Highlights the tile of the currently selected piece (if any).
        """
        self.clear_highlights()
        current_move = self.get_current_move()
        if current_move is not None:
            to_pos = current_move.to_pos if not current_move.castling else (current_move.to_pos[0], flip_pos(castling_king_column[(1 if current_move.to_pos[1] > current_move.from_pos[1] else -1)*self.flipped], flipped=self.flipped))
            self.highlight_tile(3, current_move.from_pos, to_pos)
        if self.selected is not None and self.selected.piece is not None:
            self.highlight_tile(4, self.selected.pos)

    def get_current_move(self):
        """
        Retrieves the current move from the move tree.

        This method accesses the move tree associated with the board and returns
        the move that is currently active.

        Returns:
            Move: The current move object from the move tree.
        """
        return self.move_tree.current.move
    
    def get_center(self) -> list[tuple[int, int]]:
        """
        Calculate and return the coordinates of the center square(s) of the board.

        This function determines the center point(s) of a chessboard-like grid based on the 
        number of rows and columns defined in the `config` module. If the board has an odd 
        number of rows or columns, the center will be a single square. If the board has an 
        even number of rows or columns, the center will consist of multiple squares.

        Returns:
            list[tuple[int, int]]: A list of tuples representing the coordinates of the 
            center square(s) of the board.
        """
        mid_x, mid_y = (config.columns - 1) // 2, (config.rows - 1) // 2
        return [(mid_x + i, mid_y + j) for i in range(2 - config.columns % 2) for j in range(2 - config.rows % 2)]

    def __str__(self):
        """
        Generate the FEN (Forsyth-Edwards Notation) string representation of the chessboard.

        This method constructs a FEN string that represents the current state of the chessboard,
        including the positions of pieces, the active player, castling rights, en passant target square,
        halfmove clock, and fullmove number.

        Returns:
            str: A FEN string representing the current state of the chessboard.
        """
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
        """
        Converts the current state of the chessboard into a 3D matrix representation.

        The matrix has dimensions (14, 8, 8), where:
        - Channels 0-5 represent the positions of white pieces (one channel per piece type).
        - Channels 6-11 represent the positions of black pieces (one channel per piece type).
        - Channel 12 indicates whether a piece at a position has legal moves.
        - Channel 13 marks the positions of all legal moves for the current player's turn.

        Returns:
            numpy.ndarray: A 3D matrix representing the chessboard state, piece positions, 
            and legal moves for the current turn.
        """
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
                            if self.convert_to_move(pos, move).is_legal(self):
                                matrix[13, move[0], move[1]] = 1 
                                legal_moves += 1
                            if legal_moves:       
                                matrix[12, pos[0], pos[1]] = 1               
        return matrix

    def convert_uci_to_move(self, uci_move):
        """
        Converts a UCI (Universal Chess Interface) string representation of a move 
        into a move object if the move is valid.

        Utility:
        This function takes a UCI string (e.g., "e2e4" or "e7e8q") and translates it 
        into a move object that can be processed by the chess game. It ensures the 
        move is valid and belongs to the current player's available moves.

        Parameters:
        - uci_move (str): A string in UCI format representing a chess move. 
          For example:
            - "e2e4" represents a pawn moving from e2 to e4.
            - "e7e8q" represents a pawn promotion to a queen on e8.

        Returns:
        - Move object: If the UCI move is valid and corresponds to a legal move.
        - None: If the UCI move is invalid or does not match any legal move.
        """
        columns = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
        from_pos = (8-int(uci_move[1]), columns[uci_move[0]])
        to_pos = (8-int(uci_move[3]), columns[uci_move[2]])
        promotion = notation_to_piece(uci_move[4]) if len(uci_move) == 5 else None
        if self.is_empty(from_pos):
            return None
        exist = False
        for move in self.current_player.get_moves(self):
            if (move.from_pos, move.to_pos) == (from_pos, to_pos):
                exist = True
        if not exist:
            return None
        return self.convert_to_move(from_pos, to_pos, promotion)

    def update_history(self):
        """
        Updates the history of moves displayed on the chessboard.
        This function retrieves the sequence of moves from the move tree, determines
        the range of moves to display (up to the last 20 moves), and creates a list
        of `Label` objects to visually represent the moves and their corresponding
        move numbers on the board. The labels are positioned dynamically based on
        the configuration of the board's dimensions.
        """
        moves = self.move_tree.get_root_to_leaf()
        start_num = max(1, ceil((len(moves) - 20) / 2)) if len(moves) > 20 else 1
        moves = moves[-(22 if len(moves) % 2 == 0 else 21):]

        self.history = [
            Label(
                center=(config.width * 0.7 + (config.width * 0.1 * (i % 2)), 
                        config.height * 0.1 + (config.height * 0.035) * (i - i % 2)),
                text=move.notation,
                font_name=Fonts.TYPE_MACHINE,
                font_size=int(config.height * 0.05),
                color=Colors.WHITE.value
            )
            for i, move in enumerate(moves)
        ] + [
            Label(
                center=(config.width * 0.6, config.height * 0.1 + (config.height * 0.035) * 2 * i),
                text=f"{start_num + i}.",
                font_name=Fonts.TYPE_MACHINE,
                font_size=int(config.height * 0.05),
                color=Colors.WHITE.value
            )
            for i in range(ceil(len(moves) / 2))
        ]
