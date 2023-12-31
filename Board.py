import pygame.draw

from Pieces import *
from constants import *


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
        self.frame.fill(tile_assets[selected_tile][0])
        for row in range(rows):
            for column in range(row % 2, columns, 2):
                pygame.draw.rect(self.frame, tile_assets[selected_tile][1],(row * square_size, column * square_size, square_size, square_size))

    def draw_piece(self, piece, window):
        window.blit(piece.image, (piece.x, piece.y))

    def draw_rect(self, row, column):
        pygame.draw.rect(self.frame, (255, 0, 0), (row * square_size, column * square_size, square_size, square_size))

    def draw_pieces(self):
        for row in range(self.rows):
            for column in range(self.columns):
                if self.debug:
                    self.frame.blit(pygame.font.SysFont("monospace", 15).render(f"({column},{row})", 1, (0, 0, 0)), (row*square_size+35, column*square_size+60))
                piece = self.board[row][column]
                if piece != 0:
                    self.draw_piece(piece, self.frame)

    def draw_moves(self, moves):
        for pos in moves:
            row, column = pos[0], pos[1]
            pygame.draw.circle(self.frame, (127, 255, 0), (column * square_size + square_size // 2, row * square_size + square_size // 2), square_size // 8)

    def draw_promotion(self, promotion):
        # TODO promotion is offbeat by 1 square if it's a capture
        for row in range((0 if promotion.color == 1 else 7), (0 if promotion.color == 1 else 7)+4*promotion.color, promotion.color):
            pygame.draw.rect(self.frame, (255, 255, 255, 0.5), (promotion.column * square_size, row * square_size, square_size, square_size))

    def draw_test(self):
        for row in range(self.rows):
            for column in range(self.columns):
                pygame.draw.circle(self.frame, (255, 0, 0), (column * square_size + square_size // 2, row * square_size + square_size // 2), square_size // 16)