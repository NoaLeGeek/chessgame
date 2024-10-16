import pygame
from constants import bishop_directions, rook_directions, queen_directions, king_directions, knight_directions
from utils import flip_coords, sign

class Piece:
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None) -> None:
        self.color = color
        self.row = row
        self.column = column
        self.moves = []
        self.x = 0
        self.y = 0
        self.image = image

    def move(self, row: int, column: int) -> None:
        self.row = row
        self.column = column

    @staticmethod
    def notation_to_piece(notation:str):
        return {'P':Pawn, 'K':King, 'R':Rook, 'B':Bishop, 'N':Knight, 'Q':Queen}[notation.upper()]
    
    @staticmethod
    def piece_to_notation(piece: "Piece"):
        return {Pawn: 'P', King: 'K', Rook: 'R', Bishop: 'B', Knight: 'N', Queen: 'Q'}[type(piece)]
            
    def get_square_color(self):
        return (self.row + self.column) % 2

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
        en_passant = kwds["en_passant"] if "en_passant" in kwds else None
        x = self.color * flipped

        # Déplacement de base vers l'avant
        if 0 <= row - x < board.config.rows and board.get_object(row - x, column) == 0:
            self.moves.append((row - x, column))
            # Premier déplacement du pion (2 cases vers l'avant)
            if self.first_move and 0 <= row - 2 * x < board.config.rows and board.get_object(row - 2 * x, column) == 0:
                self.moves.append((row - 2 * x, column))

        # Capture diagonale et en passant
        for d_row, d_col in [(-x, -1), (-x, 1)]:  # Diagonales (-x, -1) et (-x, 1)
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                piece = board.get_object(new_row, new_col)
                # Capture normale
                if piece and piece.is_enemy(self):
                    self.moves.append((new_row, new_col))
                # Capture en passant
                if en_passant and en_passant == (new_row, new_col):
                    self.moves.append((new_row, new_col))


class Rook(Piece):
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)
        # Indicates whether the rook has moved or not
        self.first_move = True

    def calc_moves(self, board, row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        for d_row, d_col in rook_directions:
            row_temp, column_temp = row + d_row, column + d_col
            while 0 <= row_temp < board.config.rows and 0 <= column_temp < board.config.columns:
                piece = board.get_object(row_temp, column_temp)
                if piece == 0:
                    self.moves.append((row_temp, column_temp))
                elif piece.is_enemy(self):
                    self.moves.append((row_temp, column_temp))
                    break
                else:
                    break
                row_temp += d_row
                column_temp += d_col

class Bishop(Piece):
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)

    def calc_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        for d_row, d_col in bishop_directions:
            row_temp, column_temp = row + d_row, column + d_col
            while 0 <= row_temp < board.config.rows and 0 <= column_temp < board.config.columns:
                piece = board.get_object(row_temp, column_temp)
                # Case vide
                if piece == 0:
                    self.moves.append((row_temp, column_temp))
                # Pièce ennemie
                elif piece.is_enemy(self):  
                    self.moves.append((row_temp, column_temp))
                    break
                # Pièce alliée
                else:  
                    break
                row_temp += d_row
                column_temp += d_col


class Knight(Piece):
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)

    def calc_moves(self, board, row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        for d_row, d_col in knight_directions:
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                piece = board.get_object(new_row, new_col)
                if not piece or piece.is_enemy(self):
                    self.moves.append((new_row, new_col))


class Queen(Piece):
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)

    def calc_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        for d_row, d_col in queen_directions:
            row_temp, column_temp = row + d_row, column + d_col
            while 0 <= row_temp < board.config.rows and 0 <= column_temp < board.config.columns:
                piece = board.get_object(row_temp, column_temp)
                if piece == 0:  # Case vide
                    self.moves.append((row_temp, column_temp))
                elif piece.is_enemy(self):  # Pièce ennemie
                    self.moves.append((row_temp, column_temp))
                    break
                else:  # Pièce alliée
                    break
                row_temp += d_row
                column_temp += d_col

    
class King(Piece):
    def __init__(self, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(color, row, column, image)
        # Indicates whether the king has moved or not
        self.first_move = True

    def calc_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        for d_row, d_col in king_directions:
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                piece = board.get_object(new_row, new_col)
                if not piece or piece.is_enemy(self):
                    self.moves.append((new_row, new_col))
        # Castling
        if self.first_move:
            # O-O-O
            rook = next((board[row][i] for i in range(column - flipped, flip_coords(-1, flipped=flipped), -flipped) if isinstance(board[row][i], Rook) and board[row][i].first_move), None)
            if rook is not None and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(2, flipped=flipped), column, sign(column - flip_coords(2, flipped=flipped)))) and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(3, flipped=flipped), rook.column, sign(rook.column - flip_coords(3, flipped=flipped)))):
                self.moves.append((row, rook.column))
            # O-O   
            rook = next((board[row][i] for i in range(column + flipped, flip_coords(8, flipped = flipped), flipped) if isinstance(board[row][i], Rook) and board[row][i].first_move), None)
            if rook is not None and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(6, flipped=flipped), column, sign(column - flip_coords(6, flipped=flipped)))) and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(5, flipped=flipped), rook.column, sign(rook.column - flip_coords(5, flipped=flipped)))):
                self.moves.append((row, rook.column))