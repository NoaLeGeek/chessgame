import constants

from constants import config, square_size

class Piece:
    def __init__(self, color, row, column):
        self.color = color
        self.row = row
        self.column = column
        self.x = 0
        self.y = 0
        self.available_moves = []
        if config["selected_piece_asset"] != "blindfold":
            self.image = constants.piece_assets[config["selected_piece_asset"]][Piece.piece_to_index(self) + 3 * (1 - self.color)]
            self.calc_pos(self.image)

    def piece_move(self, row, column):
        self.row = row
        self.column = column
        if config["selected_piece_asset"] != "blindfold":
            self.calc_pos(self.image)

    def calc_pos(self, image):
        self.x = config["margin"] + (self.column + 0.5) * square_size - 0.5*image.get_width()
        self.y = config["margin"] + (self.row + 0.5) * square_size - (image.get_height() - 0.5*image.get_width() if config["selected_piece_asset"].startswith("3d") else 0.5*image.get_height())

    def clear_available_moves(self):
        if self.available_moves:
            self.available_moves = []

    def piece_to_index(piece):
        return {Pawn: 0, Knight: 1, Bishop: 2, Rook: 3, Queen: 4, King: 5}[type(piece)]
    
    def index_to_piece(index):
        return [Pawn, Knight, Bishop, Rook, Queen, King][index]


class Pawn(Piece):
    def __init__(self, color, row, column):
        super().__init__(color, row, column)
        self.first_move = True
        self.value = 1

    def get_available_moves(self, board, row, column, flipped: bool = False, **kwds):
        self.clear_available_moves()
        en_passant = kwds["en_passant"]
        x = self.color * flipped
        if -1 < row - x < len(board):
            if board[row - x][column] == 0:
                self.available_moves.append((row - x, column))
                if self.first_move and ((x > 0 and -1 < row - 2 * x) or (x < 0 and row - 2 * x < len(board))) and board[row - 2 * x][column] == 0:
                    self.available_moves.append((row - 2 * x, column))
            if 0 < column and board[row - x][column - 1] != 0 and board[row - x][column - 1].color != self.color:
                self.available_moves.append((row - x, column - 1))
            if column < len(board[row]) - 1 and board[row - x][column + 1] != 0 and board[row - x][column + 1].color != self.color:
                self.available_moves.append((row - x, column + 1))
            
            # Check for en passant
            if en_passant and en_passant[0] == row - x:
                if 0 < column and en_passant[1] == column - 1:
                    self.available_moves.append((row - x, column - 1))
                if column < len(board[row]) - 1 and en_passant[1] == column + 1:
                    self.available_moves.append((row - x, column + 1))
        return self.available_moves


class Rook(Piece):
    def __init__(self, color, row, column):
        super().__init__(color, row, column)
        self.first_move = True
        self.value = 5

    def get_available_moves(self, board, row, column, flipped: bool = False, **kwds):
        self.clear_available_moves()
        for i in range(row + 1, len(board)):
            if board[i][column] == 0:
                self.available_moves.append((i, column))
            elif board[i][column].color != self.color:
                self.available_moves.append((i, column))
                break
            else:
                break
        for i in range(row - 1, -1, -1):
            if board[i][column] == 0:
                self.available_moves.append((i, column))
            elif board[i][column].color != self.color:
                self.available_moves.append((i, column))
                break
            else:
                break
        for i in range(column + 1, len(board[row])):
            if board[row][i] == 0:
                self.available_moves.append((row, i))
            elif board[row][i].color != self.color:
                self.available_moves.append((row, i))
                break
            else:
                break
        for i in range(column - 1, -1, -1):
            if board[row][i] == 0:
                self.available_moves.append((row, i))
            elif board[row][i].color != self.color:
                self.available_moves.append((row, i))
                break
            else:
                break
        return self.available_moves


class Bishop(Piece):
    def __init__(self, color, row, column):
        super().__init__(color, row, column)
        self.value = 3

    def get_available_moves(self, board, row, column, flipped: bool = False, **kwds):
        self.clear_available_moves()
        row_temp = row + 1
        column_temp = column + 1
        while row_temp < len(board) and column_temp < len(board[row]):
            if board[row_temp][column_temp] == 0:
                self.available_moves.append((row_temp, column_temp))
                row_temp += 1
                column_temp += 1
            elif board[row_temp][column_temp].color != self.color:
                self.available_moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row - 1
        column_temp = column - 1
        while row_temp > -1 and column_temp > -1:
            if board[row_temp][column_temp] == 0:
                self.available_moves.append((row_temp, column_temp))
                row_temp -= 1
                column_temp -= 1
            elif board[row_temp][column_temp].color != self.color:
                self.available_moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row + 1
        column_temp = column - 1
        while row_temp < len(board) and column_temp > -1:
            if board[row_temp][column_temp] == 0:
                self.available_moves.append((row_temp, column_temp))
                row_temp += 1
                column_temp -= 1
            elif board[row_temp][column_temp].color != self.color:
                self.available_moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row - 1
        column_temp = column + 1
        while row_temp > -1 and column_temp < len(board[row]):
            if board[row_temp][column_temp] == 0:
                self.available_moves.append((row_temp, column_temp))
                row_temp -= 1
                column_temp += 1
            elif board[row_temp][column_temp].color != self.color:
                self.available_moves.append((row_temp, column_temp))
                break
            else:
                break
        return self.available_moves


class Knight(Piece):
    def __init__(self, color, row, column):
        super().__init__(color, row, column)
        self.value = 3

    def get_available_moves(self, board, row, column, flipped: bool = False, **kwds):
        self.clear_available_moves()
        if row > 1 and column > 0 and (
                board[row - 2][column - 1] == 0 or board[row - 2][column - 1].color != self.color):
            self.available_moves.append((row - 2, column - 1))
        if row > 1 and column < len(board[row]) - 1 and (
                board[row - 2][column + 1] == 0 or board[row - 2][column + 1].color != self.color):
            self.available_moves.append((row - 2, column + 1))
        if row < len(board) - 2 and column > 0 and (
                board[row + 2][column - 1] == 0 or board[row + 2][column - 1].color != self.color):
            self.available_moves.append((row + 2, column - 1))
        if row < len(board) - 2 and column < len(board[row]) - 1 and (
                board[row + 2][column + 1] == 0 or board[row + 2][column + 1].color != self.color):
            self.available_moves.append((row + 2, column + 1))
        if row > 0 and column > 1 and (
                board[row - 1][column - 2] == 0 or board[row - 1][column - 2].color != self.color):
            self.available_moves.append((row - 1, column - 2))
        if row > 0 and column < len(board[row]) - 2 and (
                board[row - 1][column + 2] == 0 or board[row - 1][column + 2].color != self.color):
            self.available_moves.append((row - 1, column + 2))
        if row < len(board) - 1 and column > 1 and (
                board[row + 1][column - 2] == 0 or board[row + 1][column - 2].color != self.color):
            self.available_moves.append((row + 1, column - 2))
        if row < len(board) - 1 and column < len(board[row]) - 2 and (
                board[row + 1][column + 2] == 0 or board[row + 1][column + 2].color != self.color):
            self.available_moves.append((row + 1, column + 2))
        return self.available_moves


class Queen(Piece):
    def __init__(self, color, row, column):
        super().__init__(color, row, column)
        self.value = 9

    def get_available_moves(self, board, row, column, flipped: bool = False, **kwds):
        self.clear_available_moves()
        row_temp = row + 1
        column_temp = column + 1
        while row_temp < len(board) and column_temp < len(board[row]):
            if board[row_temp][column_temp] == 0:
                self.available_moves.append((row_temp, column_temp))
                row_temp += 1
                column_temp += 1
            elif board[row_temp][column_temp].color != self.color:
                self.available_moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row - 1
        column_temp = column - 1
        while row_temp > -1 and column_temp > -1:
            if board[row_temp][column_temp] == 0:
                self.available_moves.append((row_temp, column_temp))
                row_temp -= 1
                column_temp -= 1
            elif board[row_temp][column_temp].color != self.color:
                self.available_moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row + 1
        column_temp = column - 1
        while row_temp < len(board) and column_temp > -1:
            if board[row_temp][column_temp] == 0:
                self.available_moves.append((row_temp, column_temp))
                row_temp += 1
                column_temp -= 1
            elif board[row_temp][column_temp].color != self.color:
                self.available_moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row - 1
        column_temp = column + 1
        while row_temp > -1 and column_temp < len(board[row]):
            if board[row_temp][column_temp] == 0:
                self.available_moves.append((row_temp, column_temp))
                row_temp -= 1
                column_temp += 1
            elif board[row_temp][column_temp].color != self.color:
                self.available_moves.append((row_temp, column_temp))
                break
            else:
                break
        for i in range(row + 1, len(board)):
            if board[i][column] == 0:
                self.available_moves.append((i, column))
            elif board[i][column].color != self.color:
                self.available_moves.append((i, column))
                break
            else:
                break
        for i in range(row - 1, -1, -1):
            if board[i][column] == 0:
                self.available_moves.append((i, column))
            elif board[i][column].color != self.color:
                self.available_moves.append((i, column))
                break
            else:
                break
        for i in range(column + 1, len(board[row])):
            if board[row][i] == 0:
                self.available_moves.append((row, i))
            elif board[row][i].color != self.color:
                self.available_moves.append((row, i))
                break
            else:
                break
        for i in range(column - 1, -1, -1):
            if board[row][i] == 0:
                self.available_moves.append((row, i))
            elif board[row][i].color != self.color:
                self.available_moves.append((row, i))
                break
            else:
                break
        return self.available_moves
    
class King(Piece):
    def __init__(self, color, row, column):
        super().__init__(color, row, column)
        self.first_move = True
        self.not_castled = True

    def get_available_moves(self, board, row, column, flipped: bool = False, **kwds):
        self.clear_available_moves()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (-1 < row + i < len(board) and -1 < column + j < len(board[row])) and not (i == 0 and j == 0) and (board[row + i][column + j] == 0 or board[row + i][column + j].color != self.color):
                    self.available_moves.append((row + i, column + j))

        # Castling
        if self.column == (7 + flipped) // 2 and self.first_move:
            # O-O-O
            
            if any([isinstance(board[row][i], Rook) and board[row][i].first_move for i in range(column, 7 * (1 - flipped) - flipped, -flipped)]) and all(board[row][i] == 0 for i in range(column - flipped, 7 * (1 - flipped) // 2, -flipped)):
                self.available_moves.append((row, (7 + 3 * flipped) // 2))
            # O-O
            if any([isinstance(board[row][i], Rook) and board[row][i].first_move for i in range(column, 7 * (1 + flipped) + flipped, flipped)]) and all(board[row][i] == 0 for i in range(column + flipped, 7 * (1 + flipped) // 2, flipped)):
                self.available_moves.append((row, (7 - 5 * flipped) // 2))
        return self.available_moves
