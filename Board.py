from Pieces import *
from constants import *


class Board:
    def __init__(self, width, height, rows, columns, square_size, window):
        self.width = width
        self.height = height
        self.rows = rows
        self.columns = columns
        self.square_size = square_size
        self.window = window
        self.board = []
        self.debug = True

    def draw_board(self):
        self.window.fill(tile_assets[selected_asset][0])
        for row in range(rows):
            for column in range(row % 2, columns, 2):
                pygame.draw.rect(self.window, tile_assets[selected_asset][1],(row * self.square_size, column * self.square_size, self.square_size, self.square_size))

    def draw_piece(self, piece, window):
        window.blit(piece.image, (piece.x, piece.y))

    def draw_rect(self, row, column):
        pygame.draw.rect(self.window, (255, 0, 0), (row * self.square_size, column * self.square_size, self.square_size, self.square_size), 2)

    def draw_pieces(self):
        for row in range(self.rows):
            for column in range(self.columns):
                if self.debug:
                    self.window.blit(pygame.font.SysFont("monospace", 15).render(f"({column},{row})", 1, (0, 0, 0)), (row*square_size+35, column*square_size+60))
                piece = self.board[row][column]
                if piece != 0:
                    self.draw_piece(piece, self.window)