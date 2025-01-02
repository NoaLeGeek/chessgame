import pygame
import os
from Board.tile import Tile
from constants import castling_king_column, en_passant_direction
from utils import generate_piece_images, generate_board_image, generate_sounds, flip_pos, sign
from Board.piece import notation_to_piece, piece_to_notation
from Board.move import Move
from random import choice
from config import config

class Board:
    def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq – 0 1"):
        # Keys are (row, column) tuples and values are Tile() objects
        self.board = {}
        self.image = generate_board_image()
        self.sounds = generate_sounds()
        self.sounds.update({name: pygame.mixer.Sound(os.path.join("assets", "sounds", f"{name}.ogg")) for name in ['illegal', 'notify', 'tenseconds']})
        self.selected = None
        self.turn = 1
        self.winner = None
        self.ep = None
        self.ep_logs = []
        self.promotion = None
        self.move_logs = []
        self.half_moves = 0
        self.full_moves = 1
        self.flipped = 1
        self.kings = {1: None, -1: None}
        # Castling rights
        # 1 = White, -1 = Black
        # 1 = King side O-O, -1 = Queen side O-O-O
        self.castling = {1: {1: False, -1: False}, -1: {1: False, -1: False}}
        self.castling_logs = []
        self.last_irreversible_move = 0
        self.game_over = False
        self.piece_images = generate_piece_images(self.flipped)
        self.create_board(fen)

    def create_board(self, fen: str) -> None:
        self.board = {}
        for i, part in enumerate(fen.split()):
            match i:
                # Initialize the board
                case 0:
                    for r, string in enumerate(part.split("/")):
                        c = 0
                        for char in string:
                            if char.isdigit():
                                c += int(char)
                            else:
                                if char not in "rnbqkbnpRNBQKBNP":
                                    raise ValueError("Not a valid FEN")
                                color = 1 if char.isupper() else -1
                                tile = Tile((r, c))
                                tile.piece = notation_to_piece(char)(color, self.piece_images[("w" if color == 1 else "b") + char.upper()])
                                self.board[(r, c)] = tile
                                if char.upper() == "K":
                                    self.kings[color] = (r, c)
                                c += 1
                # Turn
                case 1:
                    self.turn = 1 if part == "w" else -1
                # Castling rights
                case 2:
                    for color in [1, -1]:
                        for d, letter in zip([1, -1], ["K", "Q"]):
                            letter = letter.lower() if color == -1 else letter
                            if letter not in part:
                                continue
                            # Find a rook that can castle in the direction d and for the given color
                            for i in range(flip_pos(0, flipped=-d*self.flipped), self.kings[color][1], -d*self.flipped):
                                piece = self.get_piece((self.kings[color][0], i))
                                if piece.notation == "R" and piece.color == color:
                                    self.castling[color][d] = True
                                    break
                    print(self.castling)
                # En passant square
                case 3:
                    if part not in ['-', '–']:
                        self.ep = (flip_pos(int(part[1]) - 1, flipped = -self.flipped), flip_pos(ord(part[0]) - 97, flipped = self.flipped))
                # Half moves
                case 4:
                    self.half_moves = int(part)
                # Full moves
                case 5:
                    self.full_moves = int(part)
        self.play_sound("game-start")         

    def generate_960_row(self, parts):
        last_row = [None]*len(config.columns)
        for index, piece in enumerate(["B", "B", "N", "N", "Q", "R", "K", "R"]):
            # Bishops
            if index < 2:
                last_row[choice(range(index, config.columns, 2))] = piece
            # Knights and Queen
            elif index < 5:
                last_row[choice([i for i, val in enumerate(last_row) if val is None])] = piece
            # Rooks and King
            else:
                last_row[[i for i, val in enumerate(last_row) if val is None][0]] = piece
        rows = parts[0].split("/")
        for row in [0, 7]:
            rows[row] = "".join(last_row)
            if row == 0:
                rows[row] = rows[row].lower()
        parts[0] = "/".join(rows)
        return parts
    
    def check_game(self) -> None:
        if self.is_stalemate():
            if self.is_king_checked():
                print("{} Wins".format("Black" if self.turn == 1 else "White"))
                self.game_over = True
            else:
                print("Stalemate")
                self.game_over = True
        elif self.half_moves >= 100:
            print("Draw by the 50 moves rule")
            self.game_over = True
        elif self.is_insufficient_material():
            self.game_over = True
            print("Draw by insufficient material")
        elif self.is_threesold_repetition():
            self.game_over = True
            print("Draw by threesold repetition")
        if self.game_over:
            self.play_sound("game-end")

    def is_threesold_repetition(self):
        for i in range(self.last_irreversible_move, len(self.move_logs)):
            position1 = self.move_logs[i].fen.split(" ")[0:4]
            count = 0
            for j in range(self.last_irreversible_move, len(self.move_logs)):
                position2 = self.move_logs[j].fen.split(" ")[0:4]
                # Two positions are the same if the pieces are in the same position, if it's the same player to play, if the castling rights are the same and if the en passant square is the same
                if position1 == position2:
                    count += 1
                    if count == 3:
                        return True
        return False

    def is_stalemate(self):
        # We have to copy the keys because .is_legal() will modify the keys and "RuntimeError: dictionary changed size during iteration" will be raised
        for pos in list(self.board.keys()).copy():
            if self.is_empty(pos):
                continue
            tile = self.get_tile(pos)
            if tile.piece.color != self.turn:
                continue
            tile.calc_moves(self)
            if len(list(filter(lambda move: self.convert_to_move(tile.pos, move).is_legal(), tile.piece.moves))) != 0:
                return False
        return True
    
    def is_insufficient_material(self):
        match self.count_pieces():
            case 2:
                return True
            case 3:
                if any([self.dict_color_pieces(color).get("B", 0) == 1 for color in [-1, 1]]):
                    return True
                if any([self.dict_color_pieces(color).get("K", 0) == 1 for color in [-1, 1]]):
                    return True
            case 4:
                if all([self.dict_color_pieces(color).get("B", 0) == 1 for color in [-1, 1]]) and self.find_tile("B", 1).get_square_color() == self.find_tile("B", -1).get_square_color():
                    return True
            case _:
                return False
    
    def count_pieces(self):
        return len([tile for tile in self.board.values() if tile.piece is not None])
    
    def find_tile(self, notation, color):
        for tile in self.board.values():
            if tile.piece is not None and tile.piece.notation == notation and tile.piece.color == color:
                return tile
        return None
    
    def dict_color_pieces(self, color):
        groups = {}
        for piece in self.board.values():
            if piece.piece is not None and piece.piece.color == color:
                groups[piece.piece.notation] = groups.get(piece.piece.notation, 0) + 1
        return groups
    
    def convert_to_move(self, from_, to, promotion=None):
        return Move(self, from_, to, promotion)
    
    def promote_piece(self, type_piece):
        new_piece = type_piece(self.selected.piece.color)
        if config.piece_asset != "blindfold":
            new_piece.image = self.piece_images[("w" if new_piece.color == 1 else "b") + new_piece.notation]
        self.board[self.promotion].piece = new_piece
        del self.board[self.selected.pos]
        self.promotion = None

    def get_tile(self, pos: tuple[int, int]):
        return self.board.get(pos, None)
    
    def get_piece(self, pos: tuple[int, int]):
        if self.is_empty(pos):
            return None
        return self.get_tile(pos).piece
    
    # True = No tile at pos in board
    def is_empty(self, pos: tuple[int, int]) -> bool:
        return self.get_tile(pos) is None
    
    def get_empty_tiles(self):
        return [pos for pos in self.board.keys() if self.is_empty(pos)]
    
    def play_sound(self, type: str):
        assert type in self.sounds, f"Sound {type} not found"
        self.sounds[type].play()

    def update_castling(self, move: Move):
        piece_tile = move.piece_tile
        # Either a castling move or a normal king move
        if piece_tile.piece.notation == "K":
            self.castling[piece_tile.piece.color] = {1: False, -1: False}
        elif piece_tile.piece.notation == "R":
            if piece_tile.column < self.kings[piece_tile.piece.color][1]:
                self.castling[piece_tile.piece.color][-1] = False
            elif piece_tile.column > self.kings[piece_tile.piece.color][1]:
                self.castling[piece_tile.piece.color][1] = False

    def update_last_irreversible_move(self, move: Move):
        if move.is_capture() or move.piece_tile.piece.notation == "P" or move.is_castling() or self.castling_logs[-1] != self.castling:
            self.last_irreversible_move = len(self.move_logs)
    
    def move_piece(self, move: Move):
        # piece_tile is never None, capture_tile can be
        piece_tile, to_pos = move.piece_tile, move.to_pos
        assert not self.is_empty(piece_tile.pos), f"There is no piece at {piece_tile.pos}"
        # Capture en passant
        if move.is_en_passant():
            del self.board[(piece_tile.pos[0], to_pos[1])]
        # Update en passant square
        self.ep = None
        if piece_tile.piece.notation == "P" and abs(piece_tile.pos[0] - to_pos[0]) == 2:
            # Check if there are opponent pawns that can capture en passant legally
            for d in [-1, 1]:
                pos = (to_pos[0], to_pos[1] + d)
                # Need a piece
                if self.is_empty(pos):
                    continue
                # Pawn only
                if self.get_piece(pos).notation != "P":
                    continue
                # Opponent's piece only
                if self.get_piece(pos).is_ally(piece_tile.piece):
                    continue
                ep = ((piece_tile.pos[0] + to_pos[0])//2, piece_tile.pos[1])
                # Verify if the opponent's pawn can capture en passant legally
                if self.convert_to_move(pos, ep).is_legal():
                    self.ep = ep
                    break
        # Castling
        if move.is_castling():
            # Castling's rook is at to_pos
            # We get the rook_tile before the king's movement because the king could overwrite the rook_tile
            rook_tile = self.get_tile(to_pos)
            d = sign(to_pos[1] - piece_tile.pos[1])
            king_column = flip_pos(castling_king_column[d*self.flipped], flipped=self.flipped)
            rook_column = flip_pos(castling_king_column[d*self.flipped]-d*self.flipped, flipped=self.flipped)
            # Moving the king
            king_tile = self.get_tile(piece_tile.pos)
            del self.board[piece_tile.pos]
            self.board[(piece_tile.pos[0], king_column)] = king_tile
            king_tile.move((piece_tile.pos[0], king_column))
            # Moving the rook
            del self.board[to_pos]
            self.board[(piece_tile.pos[0], rook_column)] = rook_tile
            rook_tile.move((piece_tile.pos[0], rook_column))
        # Normal move
        else:
            save_tile = self.board[piece_tile.pos]
            del self.board[piece_tile.pos]
            self.board[to_pos] = save_tile
            self.board[to_pos].calc_position()
            piece_tile.move(to_pos)
        # Remembering the move for undo
        self.move_logs.append(move)
        # Update castling rights
        self.update_castling(move)
        # It's important to update the king's position after the update_castling because we don't want the new king's position
        if piece_tile.piece.notation == "K":
            self.kings[piece_tile.piece.color] = to_pos
        # Remembering the current castling rights for undo
        self.castling_logs.append(self.castling)
        # Remembering the en passant square for undo
        self.ep_logs.append(self.ep)
        self.update_last_irreversible_move(move)

    def select_piece(self, pos: tuple[int, int]):
        if self.selected is not None:
            # If in the state of promotion
            if self.selected.piece.notation == "P" and self.promotion is not None:
                d = self.selected.piece.color * self.flipped
                # User clicked in the range of promotion
                if pos[0] in range(flip_pos(0, flipped=d), flip_pos(0, flipped=d) + d*len(self.selected.piece.promotion), d) and pos[1] == self.promotion[1]:
                    self.convert_to_move(self.selected.pos, self.promotion, self.selected.piece.promotion[flip_pos(pos[0], flipped=d)]).execute()
                    return
                # User did not click in the range of promotion
                self.promotion = None
                self.selected = None
                return
            # If the player clicks on one of his pieces, it will change the selected piece
            if not self.is_empty(pos) and self.get_piece(pos).is_ally(self.selected.piece) and pos != self.selected.pos:
                # Castling move
                if self.selected.piece.notation == "K" and not self.is_empty(pos) and self.get_piece(pos).notation == "R" and pos in self.selected.piece.moves:
                    self.convert_to_move(self.selected.pos, pos).execute()
                    return
                self.selected = None
                self.select_piece(pos)
                return
            # If the play clicks on the selected piece, the selection is removed
            if pos == self.selected.pos:
                self.selected = None
                return
            # If the player clicks on a square where the selected piece can't move, it will remove the selection
            if pos not in self.selected.piece.moves:
                self.selected = None
                if self.kings[self.turn] is None or self.is_king_checked():
                    self.play_sound("illegal")
                return
            # If the player push a pawn to one of the last rows, it will be in the state of promotion
            if self.selected.piece.notation == "P" and pos[0] in [0, config.rows - 1]:
                self.promotion = pos
                return
            self.convert_to_move(self.selected.pos, pos).execute()
        else:
            # Tile is empty
            if self.is_empty(pos):
                return
            # Not the player's piece
            if self.get_piece(pos).color != self.turn:
                return
            self.selected = self.get_tile(pos)
            moves = self.selected.piece.moves
            if config.rules["giveaway"] == True and any(lambda move: self.convert_to_move(pos, move).is_capture(), moves):
                moves = list(filter(lambda move: self.convert_to_move(pos, move).is_capture(), moves))
            else:
                moves = list(filter(lambda move: self.convert_to_move(pos, move).is_legal(), moves))
            self.selected.piece.moves = moves

    def in_bounds(self, pos: tuple[int, int]) -> bool:
        return 0 <= pos[0] < config.rows and 0 <= pos[1] < config.columns

    def is_king_checked(self):
        if config.rules["giveaway"] == True:
            return False
        for tile in self.board.values():
            # Not opponent's piece
            if tile.piece.color == self.turn:
                continue
            if tile.piece.notation == "K":
                continue
            tile.calc_moves(self)
            if self.kings[self.turn] in tile.piece.moves:
                return True
        return False
    
    def flip_board(self) -> None:
        # Flipping the board
        board = {}
        for pos, tile in self.board.items():
            tile.flip()
            board[flip_pos(pos)] = tile
        self.board = board
        self.flipped *= -1
        self.selected = None
        self.promotion = None
        # Flipping the kings' positions
        self.kings = {color: flip_pos(pos) for color, pos in self.kings.items()}
        # Flipping the en passant square
        if self.ep:
            self.ep = flip_pos(self.ep)
        # Flipping the last move
        if self.move_logs:
            self.move_logs[-1].from_pos, self.move_logs[-1].to_pos = flip_pos(self.move_logs[-1].from_pos), flip_pos(self.move_logs[-1].to_pos)
        # Regenerating the piece images depending on the flipped state
        if config.flipped_assets:
            self.piece_images = generate_piece_images(self.flipped)
            self.update_images()
        # Flipping the board image
        self.image = pygame.transform.flip(self.image, True, False)

    def update_images(self):
        for tile in self.board.values():
            tile.piece.update_image(self.piece_images[("w" if tile.piece.color == 1 else "b") + tile.piece.notation])

    # FEN format
    def __str__(self) -> str:
        fen = ""
        # Board
        for row in range(config.rows):
            empty_squares = 0
            for column in range(config.columns):
                piece = self.get_piece((row, column))
                if piece is None:
                    empty_squares += 1
                else:
                    if empty_squares > 0:
                        fen += str(empty_squares)
                        empty_squares = 0
                    char = piece_to_notation(type(piece))
                    fen += (char if piece.color == 1 else char.lower())
            if empty_squares > 0:
                fen += str(empty_squares)
            if row < config.rows - 1:
                fen += "/"
        fen += " " + ("w" if self.turn == 1 else "b")
        # Castling rights
        castling = " "
        for color in [1, -1]:
            for d, letter in zip([1, -1], ["K", "Q"]):
                letter = letter.lower() if color == -1 else letter
                if self.castling[color][d]:
                    castling += letter
        if castling == " ":
            castling += "-"
        fen += castling
        en_passant = " "
        # No en passant
        if self.ep is None:
            en_passant += "-"
        # Verify if there is a pawn that can be captured en passant legally
        else:
            # No need to flip the en passant row because it's the same for each board orientation
            d = en_passant_direction[self.ep[0]]
            r, c = self.ep
            string_ep = "-"
            for i in [-1, 1]:
                # Need a piece
                if self.is_empty((r + d, c + i)):
                    continue
                # Pawn only
                if self.get_piece((r + d, c + i)).notation != "P":
                    continue
                # Opponent's piece only
                if self.get_piece((r + d, c + i)).color != d*self.flipped:
                    continue
                # Verify if the opponent's pawn can capture en passant legally
                if self.convert_to_move((r + d, c + i), self.ep).is_legal():
                    string_ep = chr(97 + flip_pos(self.ep[1], flipped = self.flipped)) + str(flip_pos(self.ep[0], flipped = -self.flipped) + 1)
                    break
            en_passant += string_ep
        fen += en_passant
        fen += " " + str(self.half_moves)
        fen += " " + str(self.full_moves)
        return fen