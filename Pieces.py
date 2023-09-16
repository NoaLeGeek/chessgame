class Piece:
    def __init__(self, square_size, image, color, type, row, column):
        self.square_size = square_size
        self.image = image
        self.color = color
        self.type = type
        self.row = row
        self.column = column
        self.x = 0
        self.y = 0
        self.available_moves = []

    def piece_move(self, row, column):
        self.row = row
        self.column = column
        self.calc_pos()

    def calc_pos(self):
        self.x = self.column * self.square_size
        self.y = self.row * self.square_size

    def clear_available_moves(self):
        if self.available_moves:
            self.available_moves = []


class Pawn(Piece):
    def __init__(self, square_size, image, color, type, row, column):
        super().__init__(square_size, image, color, type, row, column)
        self.first_move = True

    def get_available_moves(self, row, column, board):
        self.clear_available_moves()
        if self.color == "white":
            if row < 1:
                pass
            if board[row - 1][column] == 0:
                self.available_moves.append((row - 1, column))
            if self.first_move and board[row - 1][column] == 0 and board[row - 2][column] == 0:
                self.available_moves.append((row - 2, column))
            if column > 0 and board[row - 1][column - 1] != 0 and board[row - 1][column - 1].color != self.color:
                self.available_moves.append((row - 1, column - 1))
            if column < len(board[0]) - 1 and board[row - 1][column + 1] != 0 and board[row - 1][
                column + 1].color != self.color:
                self.available_moves.append((row - 1, column + 1))
        if self.color == "black":
            if row >= len(board[0]) - 1:
                pass
            if board[row + 1][column] == 0:
                self.available_moves.append((row + 1, column))
            if self.first_move and board[row + 1][column] == 0 and board[row + 2][column] == 0:
                self.available_moves.append((row + 2, column))
            if column > 0 and board[row + 1][column - 1] != 0 and board[row + 1][column - 1].color != self.color:
                self.available_moves.append((row + 1, column - 1))
            if column < len(board[0]) - 1 and board[row + 1][column + 1] != 0 and board[row + 1][
                column + 1].color != self.color:
                self.available_moves.append((row + 1, column + 1))
        return self.available_moves


class Rook(Piece):
    def __init__(self, square_size, image, color, type, row, column):
        super().__init__(square_size, image, color, type, row, column)

    def get_available_moves(self, row, column, board):
        self.clear_available_moves()
        for i in range(row + 1, len(board[0])):
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
        for i in range(column + 1, len(board[0])):
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
    def __init__(self, square_size, image, color, type, row, column):
        super().__init__(square_size, image, color, type, row, column)

    def get_available_moves(self, row, column, board):
        self.clear_available_moves()
        row_temp = row + 1
        column_temp = column + 1
        while row_temp < len(board[0]) and column_temp < len(board[0]):
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
        while row_temp < len(board[0]) and column_temp > -1:
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
        while row_temp > -1 and column_temp < len(board[0]):
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
    def __init__(self, square_size, image, color, type, row, column):
        super().__init__(square_size, image, color, type, row, column)

    def get_available_moves(self, row, column, board):
        self.clear_available_moves()
