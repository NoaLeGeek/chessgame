import constants
import pygame

from constants import config, square_size, flip_coords, sign, get_value

class Piece:
    def __init__(self, color: int, row: int, column: int) -> None:
        self.color = color
        self.row = row
        self.column = column
        self.x = 0
        self.y = 0
        if config["selected_piece_asset"] != "blindfold":
            self.image = constants.piece_assets[config["selected_piece_asset"]][Piece.piece_to_index(self) + get_value(self.color, 0, 6)]
            self.calc_pos(self.image)

    def piece_move(self, row: int, column: int) -> None:
        """
        Moves the piece to the specified row and column.

        Args:
            row (int): The row to move the piece to.
            column (int): The column to move the piece to.
        """
        self.row = row
        self.column = column
        if config["selected_piece_asset"] != "blindfold":
            self.calc_pos(self.image)
            
    def get_square_color(self):
        """
        Returns the color of the square where the piece is located.
        
        The color is determined by the sum of the row and column indices of the square.
        If the sum is even, the square is considered to be black.
        If the sum is odd, the square is considered to be white.
        
        Returns:
            int: The color of the square (0 for black, 1 for white).
        """
        return (self.row + self.column) % 2

    def calc_pos(self, image: pygame.Surface) -> None:
        """
        Calculates the position of the chess piece on the board.

        Args:
            image (Image): The image of the chess piece.

        Returns:
            None
        """
        w, h = image.get_width(), image.get_height()
        self.x = config["margin"] + (self.column + 0.5) * square_size - 0.5*w
        self.y = config["margin"] + (self.row + 0.5) * square_size - (h - 0.5*w if config["selected_piece_asset"].startswith("3d") else 0.5*h)

    def is_ally(self, piece: "Piece") -> bool:
        """
        Check if the given piece is an ally.

        Args:
            piece (Piece): The piece to check.

        Returns:
            bool: True if the given piece is an ally, False otherwise.
        """
        return self.color == piece.color
    
    def is_enemy(self, piece: "Piece") -> bool:
        """
        Check if the given piece is an enemy.

        Args:
            piece (Piece): The piece to check.

        Returns:
            bool: True if the piece is an enemy piece, False otherwise.
        """
        return not self.is_ally(piece)
    
    def is_white(self) -> bool:
        """
        Check if the piece is white.

        Returns:
            bool: True if the piece is white, False otherwise.
        """
        return self.color == 1
    
    def is_black(self) -> bool:
        """
        Check if the piece is black.

        Returns:
            bool: True if the piece is black, False otherwise.
        """
        return not self.is_white()

    def piece_to_index(piece) -> int:
        """
        Converts a chess piece object to its corresponding index.

        Parameters:
        piece (object): The chess piece object.

        Returns:
        int: The index corresponding to the chess piece.

        """
        return {Pawn: 0, Knight: 1, Bishop: 2, Rook: 3, Queen: 4, King: 5}[type(piece)]
    
    def index_to_piece(index) -> "Piece":
        """
        Converts an index to a corresponding chess piece.

        Parameters:
        index (int): The index representing the chess piece.

        Returns:
        Piece: The corresponding chess piece.

        """
        return [Pawn, Knight, Bishop, Rook, Queen, King][index]

class Pawn(Piece):

    def __init__(self, color: int, row: int, column: int):
        super().__init__(color, row, column)
        # Indicates whether the pawn has moved or not
        self.first_move = True

    def get_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        """
        Returns a list of available moves for the pawn on the given chessboard.

        Args:
            board (list): The chessboard represented as a 2D list.
            row (int): The row position of the pawn on the chessboard.
            column (int): The column position of the pawn on the chessboard.
            flipped (bool, optional): Indicates whether the chessboard is flipped or not. Defaults to False.
            **kwds: Additional keyword arguments.

        Returns:
            list: A list of available moves for the pawn.

        """
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
    def __init__(self, color: int, row: int, column: int):
        super().__init__(color, row, column)
        # Indicates whether the rook has moved or not
        self.first_move = True

    def get_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        moves = []
        """
        Returns a list of available moves for the pawn on the given chessboard.

        Args:
            board (list): The chessboard represented as a 2D list.
            row (int): The row position of the pawn on the chessboard.
            column (int): The column position of the pawn on the chessboard.
            flipped (bool, optional): Indicates whether the chessboard is flipped or not. Defaults to False.
            **kwds: Additional keyword arguments.

        Returns:
            list: A list of available moves for the pawn.

        """
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


class Bishop(Piece):
    def __init__(self, color: int, row: int, column: int):
        super().__init__(color, row, column)

    def get_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        """
        Returns a list of available moves for the pawn on the given chessboard.

        Args:
            board (list): The chessboard represented as a 2D list.
            row (int): The row position of the pawn on the chessboard.
            column (int): The column position of the pawn on the chessboard.
            flipped (bool, optional): Indicates whether the chessboard is flipped or not. Defaults to False.
            **kwds: Additional keyword arguments.

        Returns:
            list: A list of available moves for the pawn.

        """
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
    def __init__(self, color: int, row: int, column: int):
        super().__init__(color, row, column)

    def get_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        """
        Returns a list of available moves for the pawn on the given chessboard.

        Args:
            board (list): The chessboard represented as a 2D list.
            row (int): The row position of the pawn on the chessboard.
            column (int): The column position of the pawn on the chessboard.
            flipped (bool, optional): Indicates whether the chessboard is flipped or not. Defaults to False.
            **kwds: Additional keyword arguments.

        Returns:
            list: A list of available moves for the pawn.

        """
        moves = []
        if row > 1 and column > 0 and (
                board[row - 2][column - 1] == 0 or board[row - 2][column - 1].is_enemy(self)):
            moves.append((row - 2, column - 1))
        if row > 1 and column < len(board[row]) - 1 and (
                board[row - 2][column + 1] == 0 or board[row - 2][column + 1].is_enemy(self)):
            moves.append((row - 2, column + 1))
        if row < len(board) - 2 and column > 0 and (
                board[row + 2][column - 1] == 0 or board[row + 2][column - 1].is_enemy(self)):
            moves.append((row + 2, column - 1))
        if row < len(board) - 2 and column < len(board[row]) - 1 and (
                board[row + 2][column + 1] == 0 or board[row + 2][column + 1].is_enemy(self)):
            moves.append((row + 2, column + 1))
        if row > 0 and column > 1 and (
                board[row - 1][column - 2] == 0 or board[row - 1][column - 2].is_enemy(self)):
            moves.append((row - 1, column - 2))
        if row > 0 and column < len(board[row]) - 2 and (
                board[row - 1][column + 2] == 0 or board[row - 1][column + 2].is_enemy(self)):
            moves.append((row - 1, column + 2))
        if row < len(board) - 1 and column > 1 and (
                board[row + 1][column - 2] == 0 or board[row + 1][column - 2].is_enemy(self)):
            moves.append((row + 1, column - 2))
        if row < len(board) - 1 and column < len(board[row]) - 2 and (
                board[row + 1][column + 2] == 0 or board[row + 1][column + 2].is_enemy(self)):
            moves.append((row + 1, column + 2))
        return moves


class Queen(Piece):
    def __init__(self, color: int, row: int, column: int):
        super().__init__(color, row, column)

    def get_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        """
        Returns a list of available moves for the pawn on the given chessboard.

        Args:
            board (list): The chessboard represented as a 2D list.
            row (int): The row position of the pawn on the chessboard.
            column (int): The column position of the pawn on the chessboard.
            flipped (bool, optional): Indicates whether the chessboard is flipped or not. Defaults to False.
            **kwds: Additional keyword arguments.

        Returns:
            list: A list of available moves for the pawn.

        """
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
    def __init__(self, color: int, row: int, column: int):
        super().__init__(color, row, column)
        # Indicates whether the king has moved or not
        self.first_move = True

    def get_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        """
        Returns a list of available moves for the pawn on the given chessboard.

        Args:
            board (list): The chessboard represented as a 2D list.
            row (int): The row position of the pawn on the chessboard.
            column (int): The column position of the pawn on the chessboard.
            flipped (bool, optional): Indicates whether the chessboard is flipped or not. Defaults to False.
            **kwds: Additional keyword arguments.

        Returns:
            list: A list of available moves for the pawn.

        """
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
