import pygame
import os
from Board.tile import Tile
from constants import castling_rook_pos
from utils import get_position, generate_piece_images, generate_board_image, generate_sounds, flip_coords, sign
from Board.piece import notation_to_piece, piece_to_notation
from Board.move import Move
from config import Config
from random import choice

class Board:
    def __init__(self, config: Config, size: int):
        self.config = config
        self.image = generate_board_image(self.config.board_asset, self.config.tile_size)
        self.sounds = generate_sounds(self.config.sound_asset)
        self.sounds.update({name: pygame.mixer.Sound(os.path.join("assets", "sounds", f"{name}.ogg")) for name in ['illegal', 'notify', 'tenseconds']})
        self.size = size
        self.selected = None
        self.turn = 1
        self.winner = None
        self.ep = None
        self.epLogs = []
        self.promotion = False
        self.moveLogs = []
        self.halfMoves = 0
        self.fullMoves = 1
        self.flipped = 1
        self.kings = {1: None, -1: None}
        self.castling = Castling(True, True, True, True)
        self.castlingLogs = []
        self.game_over = False
        if self.config.rules["+3_checks"] == True:
            self.win_condition = 0
        self.piece_images = generate_piece_images(self.config.piece_asset, self.config.tile_size)
        #self.reserves = {player: {piece: [] for piece in 'PLNSGBR'} for player in (-1, 1)}
        self.create_board()

    def create_board(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq – 0 1"
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
                                tile = Tile(self, (r, c), self.config.tile_size)
                                tile.piece = notation_to_piece(char)(self.config.rules, color, self.piece_images[("w" if color == 1 else "b") + char.upper()])
                                self.board[(r, c)] = tile
                                self.update_kings((r, c))
                                c += 1
                # Turn
                case 1:
                    self.turn = 1 if part == "w" else -1
                # Castling rights
                case 2:
                    # for d in [-1, 1]:
                    #     for row in 
                    # TODO doesn't work with 960
                    if "K" not in part and self.get_piece((7, 7)).notation == "R":
                        self.get_piece((7, 7)).first_move = False
                    if "Q" not in part and self.get_piece((7, 0)).notation == "R":
                        self.get_piece((7, 0)).first_move = False
                    if "k" not in part and self.get_piece((0, 7)).notation == "R":
                        self.get_piece((0, 7)).first_move = False
                    if "q" not in part and self.get_piece((0, 0)).notation == "R":
                        self.get_piece((0, 0)).first_move = False
                # En passant square
                case 3:
                    if part not in ['-', '–']:
                        self.ep = (flip_coords(int(part[1]) - 1, flipped = -self.flipped), flip_coords(ord(part[0]) - 97, flipped = self.flipped))
                # Half moves
                case 4:
                    self.halfMoves = int(part)
                # Full moves
                case 5:
                    self.fullMoves = int(part)
        self.play_sound("game-start")         

    def generate_960_row(self, parts):
        last_row = [None]*len(self.config.columns)
        for index, piece in enumerate(["B", "B", "N", "N", "Q", "R", "K", "R"]):
            # Bishops
            if index < 2:
                last_row[choice(range(index, self.config.columns, 2))] = piece
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
        if self.config.rules["king_of_the_hill"] == True and any([not self.is_empty(center) and self.get_piece(center).notation == "K" for center in self.get_center()]):
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.config.rules["+3_checks"] == True and self.win_condition >= 3:
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.config.rules["giveaway"] == True and (any([self.dict_color_pieces(color) == dict() for color in [1, -1]]) or self.is_stalemate()):
            print("{} Wins".format("Black" if self.turn == -1 else "White"))
            self.game_over = True
        elif self.config.rules["giveaway"] == False and self.is_checkmate():
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.is_stalemate():
            print("Stalemate")
            self.game_over = True
        elif self.halfMoves >= 100:
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
        last_index = 0
        # TODO maybe make this a global variable to avoid recalculating it
        for i in range(len(self.moveLogs)-1, -1, -1):
            move = self.moveLogs[i]
            # Irreversible move are captures, pawn moves, castling or losing castling rights
            if move.is_capture() or move.from_tile.piece.notation == "P" or move.is_castling() or move.fen.split(" ")[2] != self.moveLogs[i-1].fen.split(" ")[2]:
                last_index = i
                break
        for i in range(last_index, len(self.moveLogs)):
            position1 = self.moveLogs[i].fen.split(" ")[0:4]
            count = 0
            for j in range(last_index, len(self.moveLogs)):
                position2 = self.moveLogs[j].fen.split(" ")[0:4]
                # Two positions are the same if the pieces are in the same position, if it's the same player to play, if the castling rights are the same and if the en passant square is the same
                if position1 == position2:
                    count += 1
                    if count == 3:
                        return True
        return False
    
    def is_checkmate(self):
        return self.in_check() and self.is_stalemate()

    def is_stalemate(self):
        for pos in self.board.keys():
            if self.is_empty(pos):
                continue
            tile = self.get_tile(pos)
            if tile.piece.color != self.turn:
                continue
            tile.calc_moves()
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
        return len([piece for piece in self.board.values() if piece.piece is not None])
    
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

    def get_center(self):
        return [(i, j) for i in range((self.config.rows-1)//2, (self.config.rows//2)+1) for j in range((self.config.columns-1)//2, (self.config.columns//2)+1)]
    
    def convert_to_move(self, from_, to):
        return Move(self, from_, to)

    def make_move(self, move):
        capture = self.get(move).piece
        self.move_piece(self.selected, move)
        if capture:
            self.capture_piece(capture)
        if (self.selected.row <= 2 and self.turn == -1 or self.selected.row >= 6 and self.turn == 1):
            self.promotion = True
            self.selected.moves = []
            return
        self.change_turn()
    
    def promote_piece(self, type_piece):
        new_piece = type_piece(self.selected.color, self.selected.row, self.selected.column)
        if self.config.piece_asset != "blindfold":
            new_piece.image = self.piece_images[new_piece.notation]
        self.board[(self.selected.row, self.selected.column)].piece = new_piece
        self.promotion = False

    def change_turn(self):
        self.selected = None
        self.turn *= -1

    def update_kings(self, pos: tuple[int, int]) -> None:
        piece = self.get_piece(pos)
        if piece.notation == "K":
            self.kings[piece.color] = pos

    def is_in_check(self):
        return self.get_piece(*self.kings[self.turn]).in_check(self)

    def get_tile(self, pos: tuple[int, int]):
        return self.board.get(pos, None)
    
    def get_piece(self, pos: tuple[int, int]):
        if self.is_empty(pos):
            return None
        return self.get_tile(pos).piece
    
    # True = Tile has no object
    def is_empty(self, pos: tuple[int, int]) -> bool:
        return self.get_tile(pos) is None
    
    def get_empty_tiles(self):
        return [pos for pos in self.board.keys() if self.is_empty(pos)]
    
    def play_sound(self, type: str):
        assert type in self.sounds, f"Sound {type} not found"
        self.sounds[type].play()
    
    def move_piece(self, move: Move):
        print("BOARD BEFORE MOVE", str(self))
        # from_tile is never None, to_tile can be
        from_tile, to_pos = move.from_tile, move.to_pos
        print("PIECE POS BEFORE MOVE", from_tile.pos)
        print("TO POS", to_pos)
        assert not self.is_empty(from_tile.pos), f"There is no piece at {from_tile.pos}"
        # Capture en passant
        if move.is_en_passant():
            print("IM DOING EN PASSANT")
            del self.board[(from_tile.pos[0], to_pos[1])]
        # Update en passant square
        self.ep = None
        if from_tile.piece.notation == "P" and abs(from_tile.pos[0] - to_pos[0]) == 2:
            self.ep = (from_tile.pos[0] - from_tile.piece.color, from_tile.pos[1])
        save_tile = self.board[from_tile.pos]
        print("SAVE TILE", save_tile.coord)
        del self.board[from_tile.pos]
        self.board[to_pos] = save_tile
        self.board[to_pos].calc_position()
        print("AFTER SAVE TILE", self.board[to_pos].coord)
        from_tile.move(to_pos)
        print("PIECE POS AFTER MOVE", from_tile.pos)
        # Remembering the move for undo
        self.moveLogs.append(move)
        self.update_kings(to_pos)
        # Remembering the current castling rights for undo
        self.castlingLogs.append(self.castling)
        x = from_tile.piece.color * self.flipped
        # Castling
        if move.is_castling():
            d = sign(to_pos[1] - from_tile.pos[1])
            # Rook and King's positions are swapped to avoid King's deletion during some 960 castling
            # King is now at to_tile.pos
            # Rook is now at (row, piece.column)
            self.board[to_pos], self.board[(to_pos[1], from_tile.pos[1])] = self.board[(to_pos[1], from_tile.pos[1])], self.board[to_pos]
            # Calculate the new position for the rook
            rook_column = flip_coords(castling_rook_pos[d*self.flipped], flipped=d*self.flipped)
            # piece.column hasn't updated, we can use it as the old King's pos where the rook is
            self.get_tile((to_pos[0], from_tile.pos[1])).move((to_pos[0], rook_column))
            self.board[(to_pos[0], from_tile.pos[1])], self.board[(to_pos[0], rook_column)] = self.board[(to_pos[0], rook_column)], self.board[(to_pos[0], from_tile.pos[1])]
            # King's pos is updated
            self.get_tile(to_pos).move(to_pos)
            # Calculate the new position for the king
            column = flip_coords(castling_rook_pos[d*self.flipped]+d, flipped=d*self.flipped)
        # Remembering the en passant square for undo
        self.epLogs.append(self.ep)
        """if to_pos[1] != from_tile.pos[1] or from_tile.pos[0] != to_pos[0]:
            if not self.is_empty(to_pos):
                del self.board[to_pos]
            self.board[from_tile.pos], self.board[to_pos] = self.board[to_pos], self.board[from_tile.pos]
            from_tile.move(to_pos)"""
        # Update the first_move attribute of the piece if it moved
        if from_tile.piece.notation in "KRP" and from_tile.piece.first_move:
            from_tile.piece.first_move = False
        print("BOARD AFTER MOVE", str(self))

    def select_piece(self, pos: tuple[int, int]):
        if self.selected is not None:
            x = self.selected.piece.color * self.flipped
            # If in the state of promotion
            if self.selected.piece.notation == "P" and self.promotion:
                # User clicked in the range of promotion
                if pos[0] in range(flip_coords(0, flipped=x), flip_coords(0, flipped=x) + x*len(self.selected.promotion), x) and pos[1] == self.promotion[1] + self.selected.column:
                    self.promote_piece(self.selected.promotion[flip_coords(pos[0], flipped=x)])
                    return
                # User did not click in the range of promotion
                self.promotion = False
                # Reselect the pawn if clicked
                if pos == self.selected.pos:
                    self.selected = None
                    self.select_piece(pos)
                    return
            # If the player clicks on one of his pieces, it will change the selected piece
            if not self.is_empty(pos) and self.get_piece(pos).is_ally(self.selected.piece) and pos != self.selected.pos:
                # Castling move
                if self.selected.piece.notation == "R" and self.get_piece(pos).notation == "K" and pos in self.selected.piece.moves:
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
                if self.kings[self.turn] is None or self.in_check():
                    self.play_sound("illegal")
                return
            # If the player push a pawn to one of the last rows, it will be in the state of promotion
            if self.selected.piece.notation == "P" and pos[0] in [0, self.config.rows - 1]:
                self.selected.move(pos)
                self.promotion = True
                if self.config.rules["giveaway"] == True:
                    self.promote_piece(self.selected.promotion)
                    return
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
            if self.config.rules["giveaway"] == True and any(lambda move: self.convert_to_move(pos, move).is_capture(), moves):
                moves = list(filter(lambda move: self.convert_to_move(pos, move).is_capture(), moves))
            else:
                moves = list(filter(lambda move: self.convert_to_move(pos, move).is_legal(), moves))
            self.selected.piece.moves = moves

    def in_bounds(self, pos: tuple[int, int]) -> bool:
        return 0 <= pos[0] < self.config.rows and 0 <= pos[1] < self.config.columns

    def in_check(self):
        if self.config.rules["giveaway"] == True:
            return False
        for pos in self.board.keys():
            # Empty tile
            if self.is_empty(pos):
                continue
            # Not opponent's piece
            if self.get_piece(pos).color == self.turn:
                continue
            opponent_tile = self.get_tile(pos)
            opponent_tile.calc_moves()
            if self.kings[self.turn] in opponent_tile.piece.moves:
                return True
        return False

    def handle_left_click(self):
        x, y = pygame.mouse.get_pos()
        pos = get_position(x, y, self.config.margin, self.config.tile_size)
        print("CLICK", pos)
        if not self.is_empty(pos) and self.get_piece(pos).color == self.turn:
            self.get_tile(pos).calc_moves()
        self.select_piece(pos)

    """def draw(self, screen):
        self.draw_tiles(screen)
        self.draw_pieces(screen)
        if self.selected:
            self.draw_moves(screen)
        self.draw_reserves(screen)
        if self.promotion:
            self.draw_promotion(screen)"""

    # FEN format
    def __str__(self) -> str:
        fen = ""
        # Board
        for row in range(self.config.rows):
            empty_squares = 0
            for column in range(self.config.columns):
                piece = self.get_piece((row, column))
                if piece is None:
                    empty_squares += 1
                else:
                    if empty_squares > 0:
                        fen += str(empty_squares)
                        empty_squares = 0
                    char = piece_to_notation(piece)
                    fen += (char if piece.color == 1 else char.lower())
            if empty_squares > 0:
                fen += str(empty_squares)
            if row < self.config.rows - 1:
                fen += "/"
        fen += " " + ("w" if self.turn == 1 else "b")
        # Castling rights
        castling = " "
        for color in [1, -1]:
            king_tile = self.find_tile("K", color)
            if king_tile is None or not king_tile.piece.first_move:
                continue
            # 1 = O-O-O, -1 = O-O
            for d in [1, -1]:
                for i in range(flip_coords(0, flipped=d*self.flipped), column, d*self.flipped):
                    # Skip if empty square
                    if self.is_empty((row, i)):
                        continue
                    piece = self.get_piece((row, i))
                    if piece.notation == "R" and piece.first_move and piece.is_ally(king_tile.piece):
                        # 1 = Queenside, -1 = Kingside
                        char = ("Q" if d == 1 else "K")
                        # White = uppercase, Black = lowercase
                        castling += char if color == 1 else char.lower()
                        break
        # If no castling rights
        if castling == " ":
            castling += "-"
        fen += castling
        en_passant = " "
        # No en passant
        if self.ep is None:
            en_passant += "-"
        # Verify if there is a pawn that can be captured en passant
        else:
            x = 1 if self.ep[0] == 3 else -1
            r, c = self.ep
            if not any([not self.is_empty((r + x, c + i)) and self.get_piece((r + x, c + i)).notation == "P" and self.get_piece((r + x, c + i)).color == x*self.flipped for i in [-1, 1]]):
                en_passant += "-"
        # En passant possible
        if en_passant == " ":
            en_passant += chr(97 + flip_coords(self.ep[1], flipped = self.flipped)) + str(flip_coords(self.ep[0], flipped = -self.flipped) + 1)
        fen += en_passant
        fen += " " + str(self.halfMoves)
        fen += " " + str(self.fullMoves)
        return fen

class Castling:
    def __init__(self, wOO, wOOO, bOO, bOOO):
        self.wOO = wOO
        self.wOOO = wOOO
        self.bOO = bOO
        self.bOOO = bOOO