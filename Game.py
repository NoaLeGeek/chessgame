import pygame
from Board import Board
from constants import *
from copy import deepcopy


class Game:
    def __init__(self, width, height, rows, columns, square_size, window):
        self.window = window
        self.board = Board(width, height, rows, columns, square_size, window)
        self.square_size = square_size
        self.selected = None
        self.turn = "white"
        self.valid_moves = []
        self.Black_pieces_left = 16
        self.White_pieces_left = 16

    def update_window(self):
        self.board.draw_board()
        self.board.draw_pieces()
        self.draw_available_moves()
        pygame.display.update()

    def reset(self, window):
        self.board = Board(width, height, rows, columns, square_size, window)
        self.square_size = square_size
        self.selected = None

    def check_game(self):
        if self.Black_pieces_left == 0:
            print("Whites win")
            return True
        if self.White_pieces_left == 0:
            print("Blacks win")
            return True
        if self.checkmate(self.board):
            if self.turn == "white":
                print("Black Wins")
                return True
            else:
                print("White wins")
                return True

    def enemies_moves(self, piece, board):
        enemies_moves = []
        for row in range(len(board)):
            for column in range(len(board[0])):
                if board[row][column] != 0 and board[row][column].color != piece.color:
                    enemies_moves += board[row][column].get_available_moves(row, column, board)
        return enemies_moves

    def change_turn(self):
        self.turn = "white" if self.turn == "black" else "black"

    def get_king_pos(self, board):
        for row in range(len(board)):
            for column in range(len(board[0])):
                if board[row][column] != 0 and board[row][column].type == "King" and board[row][
                    column].color == self.turn:
                    return row, column

    def possible_moves(self, board):
        possible_moves = []
        for row in range(len(board)):
            for column in range(len(board[0])):
                if board[row][column] != 0 and board[row][column].color == self.turn and board[row][
                    column].type != "King":
                    possible_moves += board[row][column].get_available_moves(row, column, board)

        return possible_moves

    def checkmate(self, board):
        king_pos = self.get_king_pos(board.board)
        get_king = board.get_piece(king_pos[0], king_pos[1])
        king_available_moves = set(get_king.get_available_moves(king_pos[0], king_pos[1], board.board))
        enemies_moves_set = set(self.enemies_moves(get_king, board.board))
        king_moves = king_available_moves - enemies_moves_set
        set1 = king_available_moves.intersection(enemies_moves_set)
        possible_moves_to_def = set1.intersection(self.possible_moves(board.board))
        return len(king_moves) == 0 and len(king_available_moves) != 0 and possible_moves_to_def == 0

    def draw_available_moves(self):
        if len(self.valid_moves) > 0:
            for pos in self.valid_moves:
                row, column = pos[0], pos[1]
                pygame.draw.circle(self.window, (127, 255, 0), (
                column * self.square_size + self.square_size // 2, row * self.square_size + self.square_size // 2),
                                   self.square_size // 8)

    def remove(self, board, piece, row, column):
        if piece != 0:
            board[row][column] = 0
            if piece.color == "white":
                self.White_pieces_left -= 1
            else:
                self.Black_pieces_left -= 1

    def simulate_move(self, piece, row, column):
        piece_row, piece_column = piece.row, piece.column
        save_piece = self.board.board[row][column]
        if self.board.board[row][column] != 0:
            self.board.board[row][column] = 0
        self.board.board[piece.row][piece.column], self.board.board[row][column] = self.board.board[row][column], \
        self.board.board[piece.row][piece.column]
        king_pos = self.get_king_pos(self.board.board)
        if king_pos in self.enemies_moves(piece, self.board.board):
            piece.row, piece.column = piece_row, piece_column
            self.board.board[piece_row][piece_column] = piece
            self.board.board[row][column] = save_piece
            return False

        piece.row, piece.column = piece_row, piece_column
        self.board.board[piece_row][piece_column] = piece
        self.board.board[row][column] = save_piece
        return True

    def select(self, row, col):
        if self.selected:
            move = self._move(row, col)
            if not move:
                self.selected = None
                self.select(row, col)
        piece = self.board.get_piece(row, col)
        if piece != 0 and self.turn == piece.color:
            self.selected = piece
            self.valid_moves = piece.get_available_moves(row, col, self.board.board)

    def _move(self, row, column):
        piece = self.board.get_piece(row, column)
        if self.selected and (row, column) in self.valid_moves:
            if piece == 0 or piece.color != self.selected.color:
                if self.simulate_move(self.selected, row, column):
                    self.remove(self.board.board, piece, row, column)
                    self.board.move(self.selected, row, column)
                    self.change_turn()
                    print("turn", self.turn)
                    self.valid_moves = []
                    self.selected = None
                    return True
                return False
        return False

    def get_board(self):
        return self.board
