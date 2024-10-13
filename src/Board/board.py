import pygame
import os
from Board.tile import Tile
from utils import get_position, generate_piece_images, play_sound, generate_board_image, generate_sounds, flip_coords
from Board.piece import Piece, Rook
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
        self.promotion = None
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
        self.board = [[Tile(i, j, self.config.tile_size, self.config.margin) for j in range(self.config.columns)] for i in range(self.config.rows)]
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
                                self.board[r][c].object = Piece.notation_to_piece(char)(color, r, c, self.piece_images[("w" if color == 1 else "b") + char.upper()])
                                c += 1
                # Turn
                case 1:
                    self.turn = 1 if part == "w" else -1
                # Castling rights
                case 2:
                    # TODO doesn't work with 960
                    if "K" not in part and isinstance(self.board[7][7], Rook):
                        self.get_object(7, 7).first_move = False
                    if "Q" not in part and isinstance(self.board[7][0], Rook):
                        self.get_object(7, 0).first_move = False
                    if "k" not in part and isinstance(self.board[0][7], Rook):
                        self.get_object(0, 7).first_move = False
                    if "q" not in part and isinstance(self.board[0][0], Rook):
                        self.get_object(0, 0).first_move = False
                # En passant square
                case 3:
                    if part not in ['-', '–']:
                        self.en_passant = (flip_coords(int(part[1]) - 1, flipped = -self.flipped), flip_coords(ord(part[0]) - 97, flipped = self.flipped))
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

    def select(self, row: int, column: int):
        self.selected = None
        if 0 <= row < 9 and 0 <= column < 9:
            piece = self.get_object(row, column)
            if piece and piece.color == self.turn:
                self.selected = piece
                self.selected.calc_moves(self, row, column)
        elif self.is_valid_reserve_selection(row, column):
            self.selected = self.get_object_from_reserve(column)

    def is_valid_reserve_selection(self, row, column):
        return ((row == -1 and 1 <= column < 8 and self.turn == 1) or
                (row == 9 and 1 <= column < 8 and self.turn == -1))

    def get_object_from_reserve(self, column):
        piece_type = list(self.reserves[self.turn].keys())[column - 1]
        if self.reserves[self.turn][piece_type]:
            piece = self.reserves[self.turn][piece_type][0]
            piece.moves = self.get_empty_tiles()
            return piece
        return None

    def make_move(self, move):
        capture = self.get_object(*move)
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
    
    def promote_piece(self):
        self.selected.notation = '+'+self.selected.notation
        self.selected.image = self.piece_images[self.turn][self.selected.notation]
        self.promotion = False
        self.change_turn()

    def decline_promotion(self):
        self.selected.promotion_declined = True
        self.promotion = False
        self.change_turn()

    def change_turn(self):
        self.selected = None
        self.turn *= -1

    def get_object(self, row, column):
        return self.board[row][column].object
    
    def get_highlight(self, row, column):
        return self.board[row][column].highlight_color

    def get_empty_tiles(self):
        return [(tile.row, tile.column) for row in self.board for tile in row if not tile.object]

    def handle_left_click(self):
        x, y = pygame.mouse.get_pos()
        row, column = get_position(x, y, self.config.margin, self.config.tile_size)
        if not self.promotion:
            if self.selected and (row, column) in self.selected.moves:
                if self.selected.row is not None:
                    self.make_move((row, column))
                else:
                    self.make_drop((row, column))
            else:
                self.select(row, column)
        else :
            if row == self.selected.row and column == self.selected.column :
                self.promote_piece()
            elif row == self.selected.row+1 and column == self.selected.column :
                self.decline_promotion()


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
