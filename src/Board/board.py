import pygame
import os
from Board.tile import Tile
from utils import get_position, notation_to_piece, generate_piece_images, generate_board_image, generate_sounds
from config import Config

class Board:
    def __init__(self, config: Config, size: int):
        self.config = config
        self.image = generate_board_image(self.config.board_asset, self.config.tile_size)
        self.sounds = generate_sounds(self.config.sound_asset)
        self.sounds.update({name: pygame.mixer.Sound(os.path.join("assets", "sounds", f"{name}.ogg")) for name in ['illegal', 'notify', 'tenseconds']})
        self.size = size
        self.selected_piece = None
        self.turn = 1
        self.winner = None
        self.promotion_in_progress = False
        self.piece_images = generate_piece_images(self.config.piece_asset, self.config.tile_size)
        #self.reserves = {player: {piece: [] for piece in 'PLNSGBR'} for player in (-1, 1)}
        self.create_board()

    def create_board(self):
        config = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
        self.board = [[Tile(i, j, self.config.tile_size, self.config.margin) for j in range(self.config.columns)] for i in range(self.config.rows)]
        for i, row in enumerate(config.split('/')):
            for j, char in enumerate(row):
                if char in  "rnbqkbnpRNBQKBNP":
                    player = -1 if char.islower() else 1 
                    self.board[i][j].object = notation_to_piece(char)(player, i, j, self.piece_images[("b" if player == -1 else "w") + char.upper()])

    def select(self, row: int, column: int):
        self.selected_piece = None
        if 0 <= row < 9 and 0 <= column < 9:
            piece = self.get_piece(row, column)
            print(piece.color if piece else "rien", self.turn)
            if piece and piece.color == self.turn:
                self.selected_piece = piece
                self.selected_piece.calc_moves(self, row, column)
        elif self.is_valid_reserve_selection(row, column):
            self.selected_piece = self.get_piece_from_reserve(column)

    def is_valid_reserve_selection(self, row, column):
        return ((row == -1 and 1 <= column < 8 and self.turn == 1) or
                (row == 9 and 1 <= column < 8 and self.turn == -1))

    def get_piece_from_reserve(self, column):
        piece_type = list(self.reserves[self.turn].keys())[column - 1]
        if self.reserves[self.turn][piece_type]:
            piece = self.reserves[self.turn][piece_type][0]
            piece.moves = self.get_empty_tiles()
            return piece
        return None

    def make_move(self, move):
        capture = self.get_piece(*move)
        self.move_piece(self.selected_piece, move)
        if capture:
            self.capture_piece(capture)
        if (self.selected_piece.row <= 2 and self.turn == -1 or self.selected_piece.row >= 6 and self.turn == 1) and not self.selected_piece.promoted and not self.selected_piece.promotion_declined:
            self.promotion_in_progress = True
            self.selected_piece.moves = []
            return
        self.change_turn()

    def make_drop(self, move):
        self.place_piece(self.selected_piece, move)
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
        self.selected_piece = None

    def remove_piece_from_reserve(self, piece):
        self.reserves[self.turn][piece.notation].remove(piece)
    
    def promote_piece(self):
        self.selected_piece.promoted = True
        self.selected_piece.notation = '+'+self.selected_piece.notation
        self.selected_piece.image = self.piece_images[self.turn][self.selected_piece.notation]
        self.promotion_in_progress = False
        self.change_turn()

    def decline_promotion(self):
        self.selected_piece.promotion_declined = True
        self.promotion_in_progress = False
        self.change_turn()

    def change_turn(self):
        self.selected_piece = None
        self.turn *= -1

    def get_piece(self, row, column):
        return self.board[row][column].object

    def get_empty_tiles(self):
        return [(tile.row, tile.column) for row in self.board for tile in row if not tile.object]

    def handle_left_click(self):
        x, y = pygame.mouse.get_pos()
        row, column = get_position(x, y, self.config.margin, self.config.tile_size)
        if not self.promotion_in_progress :
            if self.selected_piece and (row, column) in self.selected_piece.moves:
                if self.selected_piece.row is not None:
                    self.make_move((row, column))
                else:
                    self.make_drop((row, column))
            else:
                self.select(row, column)
        else :
            if row == self.selected_piece.row and column == self.selected_piece.column :
                self.promote_piece()
            elif row == self.selected_piece.row+1 and column == self.selected_piece.column :
                self.decline_promotion()


    def draw(self, screen):
        self.draw_tiles(screen)
        self.draw_pieces(screen)
        if self.selected_piece:
            self.draw_moves(screen)
        self.draw_reserves(screen)
        if self.promotion_in_progress :
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
