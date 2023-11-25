import Pieces
from Board import Board
from constants import *


class Game:
    def __init__(self, width, height, rows, columns, square_size, window):
        self.window = window
        self.board = Board(width, height, rows, columns, square_size, window)
        self.create_board()
        self.square_size = square_size
        self.selected = None
        self.turn = 1
        self.valid_moves = []
        self.black_pieces_left = 16
        self.white_pieces_left = 16

    def create_board(self):
        self.board.board = [[0] * 8 for _ in range(8)]
        fen = {
            'p': (Pieces.Pawn, (square_size, pieces[6], -1)), 'n': (Pieces.Knight, (square_size, pieces[7], -1)), 'b': (Pieces.Bishop, (square_size, pieces[8], -1)), 'r': (Pieces.Rook, (square_size, pieces[9], -1)), 'q': (Pieces.Queen, (square_size, pieces[10], -1)), 'k': (Pieces.King, (square_size, pieces[11], -1)),
            'P': (Pieces.Pawn, (square_size, pieces[0], 1)), 'N': (Pieces.Knight, (square_size, pieces[1], 1)), 'B': (Pieces.Bishop, (square_size, pieces[2], 1)), 'R': (Pieces.Rook, (square_size, pieces[3], 1)), 'Q': (Pieces.Queen, (square_size, pieces[4], 1)), 'K': (Pieces.King, (square_size, pieces[5], 1))
        }
        split = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w – – 0 1".split(' ')
        #TODO il faut s'occuper des autres paramètres comme w, KQkq, etc...
        for i in range(len(split)):
            match i:
                case 0:
                    for j, rang in enumerate(split[i].split('/')):
                        k = 0
                        for char in rang:
                            if char.isdigit():
                                k += int(char)
                            else:
                                self.board.board[j][k] = fen[char][0](*fen[char][1], j, k)
                                k += 1
                case 1:
                    self.turn = 1 if split[i] == 'w' else -1
                case 2:
                    if "K" not in split[i]:
                        self.board.board[7][7].first_move = False
                    if "Q" not in split[i]:
                        self.board.board[7][0].first_move = False
                    if "k" not in split[i]:
                        self.board.board[0][7].first_move = False
                    if "q" not in split[i]:
                        self.board.board[0][0].first_move = False

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
        if self.is_checkmate():
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
                if self.board.board[row][column] != 0 and isinstance(self.board.board[row][column], Pieces.King) and self.board.board[row][column].color == color:
                    return row, column

    def possible_moves(self, board: list[list[int | Pieces.Piece]]):
        possible_moves = []
        for row in range(len(board)):
            for column in range(len(board[0])):
                if board[row][column] != 0 and board[row][column].color == self.turn and isinstance(board[row][column], Pieces.King):
                    possible_moves += board[row][column].get_available_moves(board, row, column)
        return possible_moves

    def is_checkmate(self) -> bool:
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
        piece.en_passant = (isinstance(piece, Pieces.Pawn) and abs(piece.row - row) == 2)
        if isinstance(piece, Pieces.King) and abs(piece.column - column) == 2 and not self.is_king_checked():
            if column == 6:
                self.board.board[row][5], self.board.board[row][7] = self.board.board[row][7], self.board.board[row][5]
                self.board.board[row][5].piece_move(row, 5)
            else:
                self.board.board[row][3], self.board[row][0] = self.board.board[row][0], self.board.board[row][3]
                self.board.board[row][3].piece_move(row, 3)
            piece.not_castled = False
        if isinstance(piece, Pieces.Pawn) and self.board.board[row + piece.color][column] != 0 and \
                self.board.board[row + piece.color][
                    column].en_passant:
            self.board.board[row + piece.color][column] = 0
        self.board.board[piece.row][piece.column], self.board.board[row][column] = self.board.board[row][column], \
            self.board.board[piece.row][piece.column]
        piece.piece_move(row, column)
        if isinstance(piece, (Pieces.King, Pieces.Rook, Pieces.Pawn)) and piece.first_move:
            piece.first_move = False
        for row in range(rows):
            for column in range(columns):
                if self.board.board[row][column] != 0 and isinstance(self.board.board[row][column], Pieces.Pawn) and self.board.board[row][column].en_passant and self.board.board[row][column].color != piece.color:
                    self.board.board[row][column].en_passant = False

    def can_move(self, piece: Pieces.Piece, row: int, column: int) -> bool:
        if isinstance(piece, Pieces.King) and abs(piece.column - column) == 2:
            return (row, column + (piece.column - column > 0) - (piece.column - column < 0)) not in self.get_color_moves(-piece.color)
        else:
            piece_row, piece_column = piece.row, piece.column
            save_piece = self.board.board[row][column]
            if self.board.board[row][column] != 0:
                self.board.board[row][column] = 0
            self.board.board[piece.row][piece.column], self.board.board[row][column] = self.board.board[row][column], self.board.board[piece.row][piece.column]
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
            # TODO can be optimised by removing all moves that are not in the "Cross pin" if there is one, see chessprogramming.org/Pin
            self.valid_moves = [move for move in piece.get_available_moves(self.board.board, row, column) if
                                self.can_move(self.selected, move[0], move[1])]

    def make_move(self, row, column):
        piece = self.board.board[row][column]
        if not self.selected or (row, column) not in self.valid_moves or (piece != 0 and piece.color == self.selected.color):
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
