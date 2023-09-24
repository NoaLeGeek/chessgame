import pygame
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
        self.create_board()

    def create_board(self):
        for row in range(self.rows):
            self.board.append([0 for _ in range(self.columns)])
            for column in range(self.columns):
                if row == 6:
                    self.board[row][column] = Pawn(self.square_size, pieces[0], "white", "P", row, column)
                elif row == 1:
                    self.board[row][column] = Pawn(self.square_size, pieces[6], "black", "P", row, column)
                elif row == 7:
                    if column == 0 or column == 7:
                        self.board[row][column] = Rook(self.square_size, pieces[3], "white", "R", row, column)
                    elif column == 1 or column == 6:
                        self.board[row][column] = Knight(self.square_size, pieces[1], "white", "N", row, column)
                    elif column == 2 or column == 5:
                        self.board[row][column] = Bishop(self.square_size, pieces[2], "white", "B", row, column)
                    elif column == 3:
                        self.board[row][column] = Queen(self.square_size, pieces[4], "white", "Q", row, column)
                    elif column == 4:
                        self.board[row][column] = King(self.square_size, pieces[5], "white", "K", row, column)
                elif row == 0:
                    if column == 0 or column == 7:
                        self.board[row][column] = Rook(self.square_size, pieces[9], "black", "R", row, column)
                    elif column == 1 or column == 6:
                        self.board[row][column] = Knight(self.square_size, pieces[7], "black", "N", row, column)
                    elif column == 2 or column == 5:
                        self.board[row][column] = Bishop(self.square_size, pieces[8], "black", "B", row, column)
                    elif column == 3:
                        self.board[row][column] = Queen(self.square_size, pieces[10], "black", "Q", row, column)
                    elif column == 4:
                        self.board[row][column] = King(self.square_size, pieces[11], "black", "K", row, column)

    def get_piece(self, row, column):
        return self.board[row][column]

    def move(self, piece, row, column):
        self.board[piece.row][piece.column], self.board[row][column] = self.board[row][column], self.board[piece.row][piece.column]
        piece.move(row, column)
        if piece.type == "P":
            piece.first_move = False

    def draw_board(self):
        self.window.fill(tile_assets[selected_asset][0])
        for row in range(rows):
            for column in range(row % 2, columns, 2):
                pygame.draw.rect(self.window, tile_assets[selected_asset][1],(row * self.square_size, column * self.square_size, self.square_size, self.square_size))

    def draw_piece(self, piece, window):
        window.blit(piece.image, (piece.x, piece.y))

    def draw_pieces(self):
        for row in range(self.rows):
            for column in range(self.columns):
                piece = self.board[row][column]
                if piece != 0:
                    self.draw_piece(piece, self.window)



