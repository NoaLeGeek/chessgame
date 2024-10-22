import pygame
import os
from Board.tile import Tile
from utils import get_position, generate_piece_images, play_sound, generate_board_image, generate_sounds, flip_coords
from Board.piece import Piece
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
        self.ep_square = None
        self.promotion = False
        self.history = []
        self.halfMoves = 0
        self.fullMoves = 1
        self.flipped = 1
        self.piece_images = generate_piece_images(self.config.piece_asset, self.config.tile_size)
        #self.reserves = {player: {piece: [] for piece in 'PLNSGBR'} for player in (-1, 1)}
        self.debug = False
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
                                tile = Tile(r, c, self.config.tile_size, self.config.margin)
                                tile.object = Piece.notation_to_piece(char)(self.config.rules, color, r, c, self.piece_images[("w" if color == 1 else "b") + char.upper()])
                                self.board[(r, c)] = tile
                                c += 1
                # Turn
                case 1:
                    self.turn = 1 if part == "w" else -1
                # Castling rights
                case 2:
                    # TODO doesn't work with 960
                    if "K" not in part and self.get(7, 7).object.notation == "R":
                        self.get(7, 7).object.first_move = False
                    if "Q" not in part and self.get(7, 0).object.notation == "R":
                        self.get(7, 0).object.first_move = False
                    if "k" not in part and self.get(0, 7).object.notation == "R":
                        self.get(0, 7).object.first_move = False
                    if "q" not in part and self.get(0, 0).object.notation == "R":
                        self.get(0, 0).object.first_move = False
                # En passant square
                case 3:
                    if part not in ['-', '–']:
                        self.ep_square = (flip_coords(int(part[1]) - 1, flipped = -self.flipped), flip_coords(ord(part[0]) - 97, flipped = self.flipped))
                # Half moves
                case 4:
                    self.halfMoves = int(part)
                # Full moves
                case 5:
                    self.fullMoves = int(part)
        play_sound(self.sounds, "game-start")         

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

    # def select(self, row: int, column: int):
    #     self.selected = None
    #     if 0 <= row < 9 and 0 <= column < 9:
    #         piece = self.get(row, column).object
    #         if piece and piece.color == self.turn:
    #             self.selected = piece
    #             self.selected.calc_moves(self, row, column)
    #     elif self.is_valid_reserve_selection(row, column):
    #         self.selected = self.get_object_from_reserve(column)

    # def is_valid_reserve_selection(self, row, column):
    #     return ((row == -1 and 1 <= column < 8 and self.turn == 1) or
    #             (row == 9 and 1 <= column < 8 and self.turn == -1))

    # def get_object_from_reserve(self, column):
    #     piece_type = list(self.reserves[self.turn].keys())[column - 1]
    #     if self.reserves[self.turn][piece_type]:
    #         piece = self.reserves[self.turn][piece_type][0]
    #         piece.moves = self.get_empty_tiles()
    #         return piece
    #     return None

    def make_move(self, move):
        capture = self.get(*move).object
        self.move_piece(self.selected, move)
        if capture:
            self.capture_piece(capture)
        if (self.selected.row <= 2 and self.turn == -1 or self.selected.row >= 6 and self.turn == 1):
            self.promotion = True
            self.selected.moves = []
            return
        self.change_turn()

    def make_drop(self, move):
        self.place_piece(self.selected, move)
        self.change_turn()

    def move_piece(self, piece, move):
        self.board[piece.row][piece.column].object = None
        self.board[move[0]][move[1]].object = piece
        piece.move(*move)

    def capture_piece(self, piece):
        if piece.notation != 'K':
            piece.__init__(None, None, self.turn, None)
            piece.image = self.piece_images[piece.player][piece.notation]
            self.reserves[self.turn][piece.notation].append(piece)
        else :
            self.winner = self.turn
            print(f'{'black' if self.winner == 1 else 'white'} win')

    def place_piece(self, piece, move):
        self.board[move[0]][move[1]].object = piece
        piece.move(*move)
        self.remove_piece_from_reserve(piece)
        self.selected = None

    def remove_piece_from_reserve(self, piece):
        self.reserves[self.turn][piece.notation].remove(piece)
    
    def promote_piece(self, type_piece):
        new_piece = type_piece(self.selected.color, self.selected.row, self.selected.column)
        new_piece.image = self.piece_images[new_piece.notation]
        self.promotion = False
        self.change_turn()

    def change_turn(self):
        self.selected = None
        self.turn *= -1
    
    def get_tile(self, row, column):
        return self.board.get((row, column), None)
    
    def get_object(self, row, column):
        return self.get_tile(row, column).object
    
    def is_empty(self, row, column):
        return self.get_tile(row, column) is None
    
    def is_occupied(self, row, column):
        return not self.is_empty(row, column) and self.get_object(row, column).has_hitbox()
    
    def get_empty_tiles(self):
        return [(r, c) for r, c in self.board.keys() if self.is_empty(r, c)]

    def select_object(self, row, column):
        if self.selected:
            x = self.selected.color * self.flipped
            # If in the state of promotion
            if self.selected.notation == "P" and self.promotion:
                # Promote the pawn
                if row in range(flip_coords(0, x), flip_coords(0, x) + x*len(self.selected.promotion), x) and column == self.promotion[1] + self.selected.column:

                    self.promote_piece(self.selected.promotion[flip_coords(row, flipped=x)])
                    return
                # Remove the promotion
                self.promotion = False
                # Reselect the pawn if clicked
                if (row, column) == (self.selected.row, self.selected.column):
                    self.selected = None
                    self.select_object(row, column)
                    return
            # If the player clicks on one of his pieces, it will change the selected piece
            if self.board[row][column] != 0 and self.board[row][column].is_ally(self.selected) and (row, column) != (self.selected.row, self.selected.column):
                # Castling move
                if self.selected.notation == "R" and self.get(row, column).object.notation == "K" and self.get(row, column).object.is_ally(self.selected) and (row, column) in self.selected.moves:
                    self.execute_move(row, column)
                    return
                self.selected = None
                self.select_object(row, column)
                return
            # If the play clicks on the selected piece, the selection is removed
            if (row, column) == (self.selected.row, self.selected.column):
                self.selected = None
                return
            # If the player clicks on a square where the selected piece can't move, it will remove the selection
            if (row, column) not in self.selected.moves:
                self.selected = None
                if self.is_king_checked():
                    play_sound("illegal")
                return
            # If the player push a pawn to one of the last rows, it will be in the state of promotion
            if self.selected.notation == "P" and row in [0, self.config.rows - 1]:
                self.selected.move(row, column)
                self.promotion = True
                if self.config.rules["giveaway"] == True:
                    self.promote_piece(self.selected.promotion)
                    return
                return
            self.execute_move(row, column)
        else:
            # Empty tile
            if self.is_empty(row, column):
                return
            # Not a piece
            if not self.get_object(row, column).is_piece():
                return
            # Not the player's piece
            if self.get_object(row, column).color != self.turn:
                return
            piece = self.get_object(row, column)
            self.selected = piece
            if self.config.rules["giveaway"] == True and any([self.is_capture(self.selected, *move) for move in self.selected.moves]):
                moves = list(filter(lambda move: self.is_capture(self.selected, *move), moves))
            else:
                moves = list(filter(lambda move: self.is_legal(self.selected, *move), moves))
            self.selected.moves = moves

    def handle_left_click(self):
        x, y = pygame.mouse.get_pos()
        row, column = get_position(x, y, self.config.margin, self.config.tile_size)
        if not self.is_empty(row, column) and self.get_object(row, column).is_piece() and self.get_object(row, column).color == self.turn:
            self.get_object(row, column).calc_moves(self, row, column, self.flipped, ep_square=self.ep_square)
        self.select_object(row, column)

    def draw(self, screen):
        self.draw_tiles(screen)
        self.draw_pieces(screen)
        if self.selected:
            self.draw_moves(screen)
        self.draw_reserves(screen)
        if self.promotion:
            self.draw_promotion(screen)
        
class FEN:
    def __init__(self, board, turn, castling_rights, ep_square, half_move, full_move):
        self.board = board
        self.turn = turn
        self.castling_rights = castling_rights
        self.ep_square = ep_square
        self.half_move = half_move
        self.full_move = full_move
    
    def to_literal():
        pass
