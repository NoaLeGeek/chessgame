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
