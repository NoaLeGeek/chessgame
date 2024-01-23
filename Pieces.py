class Piece:
    def __init__(self, square_size, image, color, row, column):
        self.square_size = square_size
        self.image = image
        self.color = color
        self.row = row
        self.column = column
        self.x = 0
        self.y = 0
        self.available_moves = []
        self.calc_pos(image)

    def piece_move(self, row, column):
        self.row = row
        self.column = column
        self.calc_pos(self.image)

    def calc_pos(self, image):
        self.x = (self.column+0.5-0.5*image.get_width()/self.square_size)*self.square_size
        self.y = (self.row+0.5-0.5*image.get_height()/self.square_size)*self.square_size

    def clear_available_moves(self):
        if self.available_moves:
            self.available_moves = []


class Pawn(Piece):
    def __init__(self, square_size, image, color, row, column):
        super().__init__(square_size, image, color, row, column)
        self.first_move = True
        self.en_passant = False
        self.value = 1
        # Contains a tuple with (piece that wants to promote, the offset: -1 if it was a capture from the left, 0 if there's no offset, 1 if it was a capture from the right)
        self.promotion = (False, None)

    def get_available_moves(self, board, row, column):
        self.clear_available_moves()
        # TODO there will be a lot of trouble when "flip board" will be added due to the (row - self.color) by example
        if 1 <= row <= len(board) - 2:
            if board[row - self.color][column] == 0:
                self.available_moves.append((row - self.color, column))
                if self.first_move and ((self.color > 0 and 2 <= row) or (self.color < 0 and row <= len(board) - 3)) and board[row - self.color - (1 if self.color > 0 else -1)][column] == 0:
                    self.available_moves.append((row - self.color - (1 if self.color > 0 else -1), column))
            if 1 <= column and board[row - self.color][column - 1] != 0 and board[row - self.color][column - 1].color != self.color:
                self.available_moves.append((row - self.color, column - 1))
            if column <= len(board[0]) - 2 and board[row - self.color][column + 1] != 0 and board[row - self.color][column + 1].color != self.color:
                self.available_moves.append((row - self.color, column + 1))
            if 1 <= column and board[row][column - 1] != 0 and board[row][column - 1].color != self.color and isinstance(board[row][column - 1], Pawn) and board[row][column - 1].en_passant and board[row - self.color][column - 1] == 0:
                self.available_moves.append((row - self.color, column - 1))
            if column <= len(board[0]) - 2 and board[row][column + 1] != 0 and board[row][column + 1].color != self.color and isinstance(board[row][column + 1], Pawn) and board[row][column + 1].en_passant and board[row - self.color][column + 1] == 0:
                self.available_moves.append((row - self.color, column + 1))
        # TODO add promotion, the gui for white is going from top to bottom with this order: Queen Knight Rook Bishop, for black it's from bottom to top with same order just reversed, the gui has a exit to cancel the promotion
        return self.available_moves


class Rook(Piece):
    def __init__(self, square_size, image, color, row, column):
        super().__init__(square_size, image, color, row, column)
        self.first_move = True
        self.value = 5

    def get_available_moves(self, board, row, column):
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
    def __init__(self, square_size, image, color, row, column):
        super().__init__(square_size, image, color, row, column)
        self.value = 3

    def get_available_moves(self, board, row, column):
        self.clear_available_moves()
        row_temp = row + 1
        column_temp = column + 1
        while row_temp < len(board) and column_temp < len(board[0]):
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
    def __init__(self, square_size, image, color, row, column):
        super().__init__(square_size, image, color, row, column)
        self.value = 3

    def get_available_moves(self, board, row, column):
        self.clear_available_moves()
        if row > 1 and column > 0 and (
                board[row - 2][column - 1] == 0 or board[row - 2][column - 1].color != self.color):
            self.available_moves.append((row - 2, column - 1))
        if row > 1 and column < len(board[0]) - 1 and (
                board[row - 2][column + 1] == 0 or board[row - 2][column + 1].color != self.color):
            self.available_moves.append((row - 2, column + 1))
        if row < len(board) - 2 and column > 0 and (
                board[row + 2][column - 1] == 0 or board[row + 2][column - 1].color != self.color):
            self.available_moves.append((row + 2, column - 1))
        if row < len(board) - 2 and column < len(board[0]) - 1 and (
                board[row + 2][column + 1] == 0 or board[row + 2][column + 1].color != self.color):
            self.available_moves.append((row + 2, column + 1))
        if row > 0 and column > 1 and (
                board[row - 1][column - 2] == 0 or board[row - 1][column - 2].color != self.color):
            self.available_moves.append((row - 1, column - 2))
        if row > 0 and column < len(board[0]) - 2 and (
                board[row - 1][column + 2] == 0 or board[row - 1][column + 2].color != self.color):
            self.available_moves.append((row - 1, column + 2))
        if row < len(board) - 1 and column > 1 and (
                board[row + 1][column - 2] == 0 or board[row + 1][column - 2].color != self.color):
            self.available_moves.append((row + 1, column - 2))
        if row < len(board) - 1 and column < len(board[0]) - 2 and (
                board[row + 1][column + 2] == 0 or board[row + 1][column + 2].color != self.color):
            self.available_moves.append((row + 1, column + 2))
        return self.available_moves


class Queen(Piece):
    def __init__(self, square_size, image, color, row, column):
        super().__init__(square_size, image, color, row, column)
        self.value = 9

    def get_available_moves(self, board, row, column):
        self.clear_available_moves()
        row_temp = row + 1
        column_temp = column + 1
        while row_temp < len(board) and column_temp < len(board[0]):
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


class King(Piece):
    def __init__(self, square_size, image, color, row, column):
        super().__init__(square_size, image, color, row, column)
        self.first_move = True
        self.not_castled = True

    def get_available_moves(self, board, row, column):
        self.clear_available_moves()
        if row > 0 and column > 0 and (
                board[row - 1][column - 1] == 0 or board[row - 1][column - 1].color != self.color):
            self.available_moves.append((row - 1, column - 1))
        if row > 0 and (board[row - 1][column] == 0 or board[row - 1][column].color != self.color):
            self.available_moves.append((row - 1, column))
        if row > 0 and column < len(board[0]) - 1 and (
                board[row - 1][column + 1] == 0 or board[row - 1][column + 1].color != self.color):
            self.available_moves.append((row - 1, column + 1))
        if column > 0 and (board[row][column - 1] == 0 or board[row][column - 1].color != self.color):
            self.available_moves.append((row, column - 1))
        if column < len(board[0]) - 1 and (board[row][column + 1] == 0 or board[row][column + 1].color != self.color):
            self.available_moves.append((row, column + 1))
        if row < len(board) - 1 and column > 0 and (
                board[row + 1][column - 1] == 0 or board[row + 1][column - 1].color != self.color):
            self.available_moves.append((row + 1, column - 1))
        if row < len(board) - 1 and (board[row + 1][column] == 0 or board[row + 1][column].color != self.color):
            self.available_moves.append((row + 1, column))
        if row < len(board) - 1 and column < len(board[0]) - 1 and (
                board[row + 1][column + 1] == 0 or board[row + 1][column + 1].color != self.color):
            self.available_moves.append((row + 1, column + 1))
        if self.column == 4 and self.first_move:
            if board[row][0] != 0 and isinstance(board[row][0], Rook) and board[row][0].first_move and board[row][1] == 0 and board[row][2] == 0 and board[row][3] == 0:
                self.available_moves.append((row, 2))
            if board[row][7] != 0 and isinstance(board[row][7], Rook) and board[row][7].first_move and board[row][6] == 0 and board[row][5] == 0:
                self.available_moves.append((row, 6))
        return self.available_moves
