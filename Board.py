import pygame
from Pieces import *


class Board:
    def __init__(self, width, height, rows, columns, square_size, window):
        self.width = width
        self.height = height
        self.rows = rows
        self.columns = columns
        self.square_size = square_size
        self.window = window
        self.board = []
        self.create_board()

    def create_board(self):
        for row in range(self.rows):
            self.board.append([0 for _ in range(self.columns)])
            for column in range(self.columns):
                pass
