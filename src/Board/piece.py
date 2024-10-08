import pygame

class Piece:
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None) -> None:
        self.color = color
        self.row = row
        self.column = column
        self.moves = []
        self.x = 0
        self.y = 0
        if image:
            self.image = image
            #CALC POS

    def piece_move(self, row: int, column: int) -> None:
        self.row = row
        self.column = column
        if self.image:
            self.calc_pos(self.image)
            
    def get_square_color(self):
        return (self.row + self.column) % 2

    def calc_pos(self, image: pygame.Surface) -> None:
        w, h = image.get_width(), image.get_height()
        self.x = config["margin"] + (self.column + 0.5) * square_size - 0.5*w
        self.y = config["margin"] + (self.row + 0.5) * square_size - (h - 0.5*w if config["selected_piece_asset"].startswith("3d") else 0.5*h)

    def is_ally(self, piece: "Piece") -> bool:
        return self.color == piece.color
    
    def is_enemy(self, piece: "Piece") -> bool:
        return not self.is_ally(piece)

class Pawn(Piece):

    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)
        # Indicates whether the pawn has moved or not
        self.first_move = True

    def calc_moves(self, board, row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        moves = []
        en_passant = kwds["en_passant"]
        x = self.color * flipped
        if -1 < row - x < len(board):
            if board[row - x][column] == 0:
                moves.append((row - x, column))
                if self.first_move and ((x > 0 and -1 < row - 2 * x) or (x < 0 and row - 2 * x < len(board))) and board[row - 2 * x][column] == 0:
                    moves.append((row - 2 * x, column))
            if 0 < column and board[row - x][column - 1] != 0 and board[row - x][column - 1].is_enemy(self):
                moves.append((row - x, column - 1))
            if column < len(board[row]) - 1 and board[row - x][column + 1] != 0 and board[row - x][column + 1].is_enemy(self):
                moves.append((row - x, column + 1))
            
            # En passant
            if en_passant and en_passant[0] == row - x:
                if 0 < column and en_passant[1] == column - 1:
                    moves.append((row - x, column - 1))
                if column < len(board[row]) - 1 and en_passant[1] == column + 1:
                    moves.append((row - x, column + 1))
        return moves

class Rook(Piece):
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)
        # Indicates whether the rook has moved or not
        self.first_move = True

    def calc_moves(self, board, row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        moves = []
        for i in range(row + 1, len(board)):
            if board.get_piece(i, column) == 0:
                moves.append((i, column))
            elif board[i][column].is_enemy(self):
                moves.append((i, column))
                break
            else:
                break
        for i in range(row - 1, -1, -1):
            if board[i][column] == 0:
                moves.append((i, column))
            elif board[i][column].is_enemy(self):
                moves.append((i, column))
                break
            else:
                break
        for i in range(column + 1, len(board[row])):
            if board[row][i] == 0:
                moves.append((row, i))
            elif board[row][i].is_enemy(self):
                moves.append((row, i))
                break
            else:
                break
        for i in range(column - 1, -1, -1):
            if board[row][i] == 0:
                moves.append((row, i))
            elif board[row][i].is_enemy(self):
                moves.append((row, i))
                break
            else:
                break
        return moves


class Bishop(Piece):
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)

    def calc_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        moves = []
        row_temp = row + 1
        column_temp = column + 1
        while row_temp < len(board) and column_temp < len(board[row]):
            if board[row_temp][column_temp] == 0:
                moves.append((row_temp, column_temp))
                row_temp += 1
                column_temp += 1
            elif board[row_temp][column_temp].is_enemy(self):
                moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row - 1
        column_temp = column - 1
        while row_temp > -1 and column_temp > -1:
            if board[row_temp][column_temp] == 0:
                moves.append((row_temp, column_temp))
                row_temp -= 1
                column_temp -= 1
            elif board[row_temp][column_temp].is_enemy(self):
                moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row + 1
        column_temp = column - 1
        while row_temp < len(board) and column_temp > -1:
            if board[row_temp][column_temp] == 0:
                moves.append((row_temp, column_temp))
                row_temp += 1
                column_temp -= 1
            elif board[row_temp][column_temp].is_enemy(self):
                moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row - 1
        column_temp = column + 1
        while row_temp > -1 and column_temp < len(board[row]):
            if board[row_temp][column_temp] == 0:
                moves.append((row_temp, column_temp))
                row_temp -= 1
                column_temp += 1
            elif board[row_temp][column_temp].is_enemy(self):
                moves.append((row_temp, column_temp))
                break
            else:
                break
        return moves


class Knight(Piece):
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)
        self.directions = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]

    def calc_moves(self, board, row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        for d_row, d_col in self.directions:
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                piece = board.get_piece(new_row, new_col)
                if not piece or piece.is_enemy(self):
                    self.moves.append((new_row, new_col))


class Queen(Piece):
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)

    def calc_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        moves = []
        row_temp = row + 1
        column_temp = column + 1
        while row_temp < len(board) and column_temp < len(board[row]):
            if board[row_temp][column_temp] == 0:
                moves.append((row_temp, column_temp))
                row_temp += 1
                column_temp += 1
            elif board[row_temp][column_temp].is_enemy(self):
                moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row - 1
        column_temp = column - 1
        while row_temp > -1 and column_temp > -1:
            if board[row_temp][column_temp] == 0:
                moves.append((row_temp, column_temp))
                row_temp -= 1
                column_temp -= 1
            elif board[row_temp][column_temp].is_enemy(self):
                moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row + 1
        column_temp = column - 1
        while row_temp < len(board) and column_temp > -1:
            if board[row_temp][column_temp] == 0:
                moves.append((row_temp, column_temp))
                row_temp += 1
                column_temp -= 1
            elif board[row_temp][column_temp].is_enemy(self):
                moves.append((row_temp, column_temp))
                break
            else:
                break
        row_temp = row - 1
        column_temp = column + 1
        while row_temp > -1 and column_temp < len(board[row]):
            if board[row_temp][column_temp] == 0:
                moves.append((row_temp, column_temp))
                row_temp -= 1
                column_temp += 1
            elif board[row_temp][column_temp].is_enemy(self):
                moves.append((row_temp, column_temp))
                break
            else:
                break
        for i in range(row + 1, len(board)):
            if board[i][column] == 0:
                moves.append((i, column))
            elif board[i][column].is_enemy(self):
                moves.append((i, column))
                break
            else:
                break
        for i in range(row - 1, -1, -1):
            if board[i][column] == 0:
                moves.append((i, column))
            elif board[i][column].is_enemy(self):
                moves.append((i, column))
                break
            else:
                break
        for i in range(column + 1, len(board[row])):
            if board[row][i] == 0:
                moves.append((row, i))
            elif board[row][i].is_enemy(self):
                moves.append((row, i))
                break
            else:
                break
        for i in range(column - 1, -1, -1):
            if board[row][i] == 0:
                moves.append((row, i))
            elif board[row][i].is_enemy(self):
                moves.append((row, i))
                break
            else:
                break
        return moves
    
class King(Piece):
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)
        # Indicates whether the king has moved or not
        self.first_move = True

    def calc_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        moves = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (-1 < row + i < len(board) and -1 < column + j < len(board[row])) and not (i == 0 and j == 0) and (board[row + i][column + j] == 0 or board[row + i][column + j].is_enemy(self)):
                    moves.append((row + i, column + j))
        # Castling
        if self.first_move:
            # O-O-O
            rook = next((board[row][i] for i in range(column - flipped, flip_coords(-1, flipped=flipped), -flipped) if isinstance(board[row][i], Rook) and board[row][i].first_move), None)
            if rook is not None and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(2, flipped=flipped), column, sign(column - flip_coords(2, flipped=flipped)))) and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(3, flipped=flipped), rook.column, sign(rook.column - flip_coords(3, flipped=flipped)))):
                moves.append((row, rook.column))
            # O-O   
            rook = next((board[row][i] for i in range(column + flipped, flip_coords(8, flipped = flipped), flipped) if isinstance(board[row][i], Rook) and board[row][i].first_move), None)
            if rook is not None and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(6, flipped=flipped), column, sign(column - flip_coords(6, flipped=flipped)))) and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(5, flipped=flipped), rook.column, sign(rook.column - flip_coords(5, flipped=flipped)))):
                moves.append((row, rook.column))
        return moves