import Pieces
from Board import Board
from constants import *


class Game:
    def __init__(self, width, height, rows, columns, square_size, window):
        self.window = window
        self.board = Board(width, height, rows, columns, square_size, window)
        self.square_size = square_size
        self.selected = None
        self.turn = 1
        self.valid_moves = []
        self.black_pieces_left = 16
        self.white_pieces_left = 16

    def update_window(self):
        self.board.draw_board()
        self.board.draw_pieces()
        self.draw_available_moves()
        pygame.display.update()

    def reset(self, window):
        self.board = Board(width, height, rows, columns, square_size, window)
        self.square_size = square_size
        self.selected = None

    def is_king_checked(self):
        return self.get_king_position(self.turn) in self.get_color_moves(-self.turn)

    def check_game(self):
        if self.black_pieces_left == 0:
            print("Whites win")
            return True
        if self.white_pieces_left == 0:
            print("Blacks win")
            return True
        if self.checkmate():
            if self.turn == 1:
                print("Black Wins")
                return True
            else:
                print("White wins")
                return True

    def get_color_moves(self, color: int):
        color_moves = []
        for row in range(len(self.board.board)):
            for column in range(len(self.board.board[0])):
                if self.board.board[row][column] != 0 and self.board.board[row][column].color == color:
                    color_moves += self.board.board[row][column].get_available_moves(self.board.board, row, column)
        return color_moves

    def change_turn(self):
        self.turn *= -1

    def get_king_position(self, color: int):
        for row in range(len(self.board.board)):
            for column in range(len(self.board.board[0])):
                if self.board.board[row][column] != 0 and self.board.board[row][column].type == "K" and \
                        self.board.board[row][column].color == color:
                    return row, column

    def possible_moves(self, board: list[list[int | Pieces.Piece]]):
        possible_moves = []
        for row in range(len(board)):
            for column in range(len(board[0])):
                if board[row][column] != 0 and board[row][column].color == self.turn and board[row][column].type != "K":
                    possible_moves += board[row][column].get_available_moves(board, row, column)
        return possible_moves

    def checkmate(self):
        if not self.is_king_checked():
            return False
        king_pos = self.get_king_position(self.turn)
        king = self.board.board[king_pos[0]][king_pos[1]]
        king_moves = set(king.get_available_moves(self.board.board, king_pos[0], king_pos[1]))
        enemies_moves_set = set(self.get_color_moves(-king.color))
        only_moves = king_moves - enemies_moves_set
        set1 = king_moves.intersection(enemies_moves_set)
        for tup in set1:
            Board.draw_rect(self.board, tup[0], tup[1])
        return len(only_moves) == 0 and len(king_moves) != 0 and len(
            set1.intersection(set(self.get_color_moves(king.color)) - king_moves)) == 0

    def draw_available_moves(self):
        if self.valid_moves:
            for pos in self.valid_moves:
                row, column = pos[0], pos[1]
                pygame.draw.circle(self.window, (127, 255, 0), (
                    column * self.square_size + self.square_size // 2, row * self.square_size + self.square_size // 2),
                                   self.square_size // 8)

    def remove(self, piece: Pieces.Piece, row: int, column: int):
        if piece != 0:
            self.board.board[row][column] = 0
            if piece.color == 1:
                self.white_pieces_left -= 1
            else:
                self.black_pieces_left -= 1

    def move(self, piece: Pieces.Piece, row: int, column: int):
        # TODO i think that this function should be in Game py
        piece.en_passant = (piece.type == "P" and abs(piece.row - row) == 2)
        if piece.type == "K" and abs(piece.column - column) == 2 and not self.is_king_checked():
            if column == 6:
                self.board.board[row][5], self.board.board[row][7] = self.board.board[row][7], self.board.board[row][5]
                self.board.board[row][5].piece_move(row, 5)
            else:
                self.board.board[row][3], self.board[row][0] = self.board.board[row][0], self.board.board[row][3]
                self.board.board[row][3].piece_move(row, 3)
            piece.not_castled = False
        # TODO apparently this don't work if the en passant can be done due to a pin
        x = 1 if piece.color == 1 else -1
        if piece.type == "P" and self.board.board[row + x][column] != 0 and self.board.board[row + x][
            column].en_passant:
            self.board.board[row + x][column] = 0
        self.board.board[piece.row][piece.column], self.board.board[row][column] = self.board.board[row][column], \
            self.board.board[piece.row][piece.column]
        piece.piece_move(row, column)
        if piece.type in ["P", "R", "K"] and piece.first_move:
            piece.first_move = False
        for row in range(rows):
            for column in range(columns):
                if self.board.board[row][column] != 0 and self.board.board[row][column].type == "P" and \
                        self.board.board[row][column].en_passant and self.board.board[row][column].color != piece.color:
                    self.board.board[row][column].en_passant = False

    def can_move(self, piece: Pieces.Piece, row: int, column: int) -> bool:
        piece_row, piece_column = piece.row, piece.column
        save_piece = self.board.board[row][column]
        if self.board.board[row][column] != 0:
            self.board.board[row][column] = 0
        self.board.board[piece.row][piece.column], self.board.board[row][column] = self.board.board[row][column], \
            self.board.board[piece.row][piece.column]
        is_checked = self.is_king_checked()
        piece.row, piece.column = piece_row, piece_column
        self.board.board[piece_row][piece_column] = piece
        self.board.board[row][column] = save_piece
        return not is_checked

    def select(self, row, column):
        if self.selected:
            move = self.make_move(row, column)
            if not move:
                self.selected = None
                self.select(row, column)
        piece = self.board.board[row][column]
        if piece != 0 and self.turn == piece.color:
            self.selected = piece
            self.valid_moves = [move for move in piece.get_available_moves(self.board.board, row, column) if self.can_move(self.selected, move[0], move[1])]

    def make_move(self, row, column):
        piece = self.board.board[row][column]
        if not self.selected or (row, column) not in self.valid_moves or (
                piece != 0 and piece.color == self.selected.color):
            return False
        self.remove(piece, row, column)
        self.move(self.selected, row, column)
        self.change_turn()
        print("turn", self.turn)
        self.valid_moves = []
        self.selected = None
        return True

    def get_board(self):
        return self.board
