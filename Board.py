import pygame.draw
import os

from Pieces import *
from constants import *
import constants


class Board:
    def __init__(self, width, height, rows, columns, frame):
        self.width = width
        self.height = height
        self.rows = rows
        self.columns = columns
        self.frame = frame
        self.board = []
        self.debug = False

    def draw_board(self):
        self.frame.blit(board_assets[constants.selected_board_asset], (margin, margin))

    def draw_piece(self, piece, window):
        window.blit(piece.image, (piece.x, piece.y))

    def draw_rect(self, row, column):
        pygame.draw.rect(self.frame, (255, 0, 0), (column * square_size + margin, row * square_size + margin, square_size, square_size))

    def draw_pieces(self, promotion=None):
        for row in range(self.rows):
            for column in range(self.columns):
                if self.debug:
                    self.frame.blit(pygame.font.SysFont("monospace", 15).render(f"({column},{row})", 1, (0, 0, 0)), (row*square_size+35, column*square_size+60))
                piece = self.board[row][column]
                if piece == 0 or (promotion and promotion[0] == piece):
                    continue
                self.draw_piece(piece, self.frame)

    def draw_moves(self, moves):
        for pos in moves:
            row, column = pos[0], pos[1]
            transparent_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            pygame.draw.circle(transparent_surface, (0, 0, 0, 63), (square_size // 2, square_size // 2), square_size // 8)
            self.frame.blit(transparent_surface, (column * square_size + margin, row * square_size + margin))

    def draw_promotion(self, promotion, offset, flipped):
        # TODO add exit button with a X
        x = (promotion.color * -flipped)
        pygame.draw.rect(self.frame, (99, 33, 65), (200, 200, 100, 43))
        pygame.draw.rect(self.frame, (255, 255, 255), ((promotion.column + offset) * square_size + margin, 2 * (1 - x) * square_size + margin, square_size, 4.5*square_size))
        if constants.selected_piece_asset == "blindfold":
            return
        for i in range(5):
            if i < 4:
                render = [Queen, Knight, Rook, Bishop][i](promotion.color, 7 * (1 - x) // 2 + x * i, promotion.column + offset)
                render.image = piece_assets[selected_piece_asset][Piece.piece_to_index(render) + 3 * (1 - render.color)]
                self.frame.blit(render.image, (render.x, render.y))
            else:
                pygame.draw.line(self.frame, (0, 0, 0), (200, 200), (300, 300), 3)
                pygame.draw.line(self.frame, (0, 0, 0), (300, 200), (200, 300), 3)
            
    def draw_highlightedSquares(self, highlightedSquares):
        for ((row, column), highlight) in highlightedSquares.items():
            match highlight:
                # Right click
                case 0:
                    r, g, b = 255, 0, 0
                # Shift + Right click
                case 1:
                    r, g, b = 0, 255, 0
                # Ctrl + Right click
                case 2:
                    r, g, b = 255, 165, 0
                # History move
                case 3:
                    r, g, b = 255, 255, 0
                # Selected piece
                case 4:
                    r, g, b = 0, 255, 255
                case _:
                    continue
            transparent_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            transparent_surface.fill((r, g, b, 75))
            self.frame.blit(transparent_surface, (column * square_size + margin, row * square_size + margin))

    def draw_background(self):
        self.frame.blit(background_assets[constants.selected_background_asset], (0, 0))

    def flip_board(self):
        for row in range(self.rows):
            for column in range(self.columns):
                piece = self.board[row][column]
                if piece != 0:
                    piece.piece_move(7 - piece.row, 7 - piece.column)
        for row in self.board:
            row.reverse()
        self.board.reverse()

    def change_piece(self, asset):
        constants.selected_piece_asset = asset
        if constants.selected_piece_asset == "blindfold":
            return
        piece_assets[selected_piece_asset] = generate_images(asset)
        for row in range(self.rows):
            for column in range(self.columns):
                piece = self.board[row][column]
                if piece != 0:
                    piece.image = piece_assets[selected_piece_asset][Piece.piece_to_index(piece) + 3 * (1 - piece.color)]
                    piece.calc_pos(piece.image)

    def change_background(self, asset):
        background_assets[asset] = pygame.transform.scale(pygame.image.load(os.path.join("assets", "backgrounds", asset + ".png")), (self.width, self.height))
        constants.selected_background_asset = asset

    def change_sound(self, asset):
        sound_assets.update(generate_sounds(asset))
        constants.selected_sound_asset = asset

    def change_board(self, asset):
        board_assets[asset] = generate_board(asset)
        constants.selected_board_asset = asset

    def play_sound(self, sound):
        sound_assets[("all" if sound in ["illegal", "notify", "tenseconds"] else constants.selected_sound_asset, sound)].play()