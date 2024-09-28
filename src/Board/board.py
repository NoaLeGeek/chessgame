import pygame
from Board.tile import Tile
from Board.pieces import *
from utils import notation_to_piece, generate_piece_images, load_image
from config import Config

class Board:
    def __init__(self, config: Config, size: int):
        self.config = config
        self.image = load_image()
        self.sounds = load_sounds()
        self.size = size
        self.selected_piece = None
        self.current_player = -1
        self.winner = None
        self.promotion_in_progress = False
        self.piece_images = generate_piece_images(self.config.piece_asset, self.config.tile_size)
        self.reserves = {player: {piece: [] for piece in 'PLNSGBR'} for player in (-1, 1)}
        self.create_board()

    def create_board(self):
        config = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq – 0 1'
        self.board = [[Tile(i, j, self.config.tile_size) for j in range(9)] for i in range(9)]
        for i, row in enumerate(config.split('/')):
            for j, char in enumerate(row):
                if char != '0':
                    player = 1 if i < 3 else -1
                    self.board[i][j].occupying_piece = notation_to_piece(char)(i, j, player, self.piece_images[player][char])

    def select(self, row: int, column: int):
        self.selected_piece = None
        if 0 <= row < 9 and 0 <= column < 9:
            piece = self.get_piece(row, column)
            if piece and piece.player == self.current_player:
                self.selected_piece = piece
                self.selected_piece.get_moves(row, column, self)
        elif self.is_valid_reserve_selection(row, column):
            self.selected_piece = self.get_piece_from_reserve(column)

    def is_valid_reserve_selection(self, row, column):
        return ((row == -1 and 1 <= column < 8 and self.current_player == 1) or
                (row == 9 and 1 <= column < 8 and self.current_player == -1))

    def get_piece_from_reserve(self, column):
        piece_type = list(self.reserves[self.current_player].keys())[column - 1]
        if self.reserves[self.current_player][piece_type]:
            piece = self.reserves[self.current_player][piece_type][0]
            piece.moves = self.get_empty_tiles()
            return piece
        return None

    def make_move(self, move):
        capture = self.get_piece(*move)
        self.move_piece(self.selected_piece, move)
        if capture:
            self.capture_piece(capture)
        if isinstance(self.selected_piece, (Pawn, Knight, Queen, Rook, Bishop)) and (self.selected_piece.row <= 2 and self.current_player == -1 or self.selected_piece.row >= 6 and self.current_player == 1) and not self.selected_piece.promoted and not self.selected_piece.promotion_declined:
            self.promotion_in_progress = True
            self.selected_piece.moves = []
            return
        self.change_turn()

    def make_drop(self, move):
        self.place_piece(self.selected_piece, move)
        self.change_turn()

    def move_piece(self, piece, move):
        self.board[piece.row][piece.column].occupying_piece = None
        self.board[move[0]][move[1]].occupying_piece = piece
        piece.move(*move)

    def capture_piece(self, piece):
        if piece.notation != 'K':
            piece.__init__(None, None, self.current_player, None)
            piece.image = self.piece_images[piece.player][piece.notation]
            self.reserves[self.current_player][piece.notation].append(piece)
        else :
            self.winner = self.current_player
            print(f'{'black' if self.winner == 1 else 'white'} win')

    def place_piece(self, piece, move):
        self.board[move[0]][move[1]].occupying_piece = piece
        piece.move(*move)
        self.remove_piece_from_reserve(piece)
        self.selected_piece = None

    def remove_piece_from_reserve(self, piece):
        self.reserves[self.current_player][piece.notation].remove(piece)
    
    def promote_piece(self):
        self.selected_piece.promoted = True
        self.selected_piece.notation = '+'+self.selected_piece.notation
        self.selected_piece.image = self.piece_images[self.current_player][self.selected_piece.notation]
        self.promotion_in_progress = False
        self.change_turn()

    def decline_promotion(self):
        self.selected_piece.promotion_declined = True
        self.promotion_in_progress = False
        self.change_turn()

    def change_turn(self):
        self.selected_piece = None
        self.current_player *= -1

    def get_piece(self, row, column):
        return self.board[row][column].occupying_piece

    def get_empty_tiles(self):
        return [(tile.row, tile.column) for row in self.board for tile in row if not tile.occupying_piece]

    def handle_left_click(self):
        x, y = pygame.mouse.get_pos()
        row, column = int((y-self.config.margin-self.config.tile_size) // self.config.tile_size), int((x-self.config.margin) // self.config.tile_size)
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
