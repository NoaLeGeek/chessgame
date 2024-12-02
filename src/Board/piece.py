import pygame
from constants import bishop_directions, rook_directions, queen_directions, knight_directions
from utils import flip_coords, get_value

class Piece():
    def __init__(self, rules, color: int, row: int, column: int, image: pygame.Surface = None) -> None:
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

    def can_move(self, board, row: int, column: int) -> bool:
        if board.config.rules["giveaway"] == True:
            return True
        if (self.row, self.column) == (row, column):
            return True
        piece_row, piece_column = self.row, self.column
        # When called, (row, column) is empty, is occupied by a object with no hitbox or is occupied by a opponent piece
        # Save the destination square object
        save_tile = board.get_tile(row, column)
        self_tile = board.get_tile(self.row, self.column)
        # Swap the piece with the destination square
        board.board[(row, column)] = board.board[(self.row, self.column)]
        del board.board[(self.row, self.column)]
        self.row, self.column = row, column
        # Check if the king is in check after the move
        can_move = not board.is_in_check()
        # Restore the initial state of the board
        board.board[(piece_row, piece_column)] = self_tile
        board.board[(row, column)] = save_tile
        # Delete the key if the tile was empty
        if save_tile is None:
            del board.board[(row, column)]
        self.row, self.column = piece_row, piece_column
        return can_move

    @staticmethod
    def notation_to_piece(notation:str):
        return {'P':Pawn, 'K':King, 'R':Rook, 'B':Bishop, 'N':Knight, 'Q':Queen}[notation.upper()]
            
    def get_square_color(self):
        return (self.row + self.column) % 2

    def is_ally(self, piece: "Piece") -> bool:
        return self.color == piece.color
    
    def is_enemy(self, piece: "Piece") -> bool:
        return not self.is_ally(piece)

class Pawn(Piece):
    def __init__(self, rules, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(rules, color, row, column, image)
        self.notation = 'P'
        if rules["no_promotion"] == False:
            self.promotion = (Queen, Rook, Bishop, Knight) if rules["giveaway"] == True else King
        # Indicates whether the pawn has moved or not
        self.first_move = True

    def calc_moves(self, board, row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        self.moves = []
        ep_square = kwds["ep_square"] if "ep_square" in kwds else None
        x = self.color * flipped

        # Déplacement de base vers l'avant
        if 0 <= row - x < board.config.rows and board.is_empty(row - x, column):
            self.moves.append((row - x, column))
            # Premier déplacement du pion (2 cases vers l'avant)
            if self.first_move and 0 <= row - 2 * x < board.config.rows and board.is_empty(row - 2 * x, column):
                self.moves.append((row - 2 * x, column))

        # Capture diagonale et en passant
        for d_row, d_col in [(-x, -1), (-x, 1)]:  # Diagonales
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                if board.is_empty(new_row, new_col):
                    continue
                piece = board.get_piece(new_row, new_col)
                # Capture normale
                if piece.is_enemy(self):
                    self.moves.append((new_row, new_col))
                # Capture en passant
                if ep_square is not None and ep_square == (new_row, new_col):
                    self.moves.append((new_row, new_col))


class Rook(Piece):
    def __init__(self, rules, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(rules, color, row, column, image)
        self.notation = 'R'
        # Indicates whether the rook has moved or not
        self.first_move = True

    def calc_moves(self, board, row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        self.moves = []
        for d_row, d_col in rook_directions:
            row_temp, column_temp = row + d_row, column + d_col
            while 0 <= row_temp < board.config.rows and 0 <= column_temp < board.config.columns:
                if board.is_empty(row_temp, column_temp):
                    self.moves.append((row_temp, column_temp))
                elif board.is_enemy(row_temp, column_temp, self):
                    self.moves.append((row_temp, column_temp))
                    break
                else:
                    break
                row_temp += d_row
                column_temp += d_col

class Bishop(Piece):
    def __init__(self, rules, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(rules, color, row, column, image)
        self.notation = 'B'

    def calc_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        self.moves = []
        for d_row, d_col in bishop_directions:
            row_temp, column_temp = row + d_row, column + d_col
            while 0 <= row_temp < board.config.rows and 0 <= column_temp < board.config.columns:
                # Case non occupée
                if board.is_empty(row_temp, column_temp):
                    self.moves.append((row_temp, column_temp))
                # Pièce ennemie
                elif board.is_enemy(row_temp, column_temp, self):  
                    self.moves.append((row_temp, column_temp))
                    break
                # Pièce alliée
                else:  
                    break
                row_temp += d_row
                column_temp += d_col


class Knight(Piece):
    def __init__(self, rules, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(rules, color, row, column, image)
        self.notation = 'N'

    def calc_moves(self, board, row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        self.moves = []
        for d_row, d_col in knight_directions:
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                if board.is_empty(new_row, new_col) or board.is_enemy(new_row, new_col, self):
                    self.moves.append((new_row, new_col))


class Queen(Piece):
    def __init__(self, rules, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(rules, color, row, column, image)
        self.notation = 'Q'

    def calc_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        self.moves = []
        for d_row, d_col in queen_directions:
            row_temp, column_temp = row + d_row, column + d_col
            while 0 <= row_temp < board.config.rows and 0 <= column_temp < board.config.columns:
                if board.is_empty(row_temp, column_temp):  # Case non occupée
                    self.moves.append((row_temp, column_temp))
                elif board.is_enemy(row_temp, column_temp, self):  # Pièce ennemie
                    self.moves.append((row_temp, column_temp))
                    break
                else:  # Pièce alliée
                    break
                row_temp += d_row
                column_temp += d_col

    
class King(Piece):
    def __init__(self, rules, color: int, row: int, column: int, image: pygame.Surface = None):
        super().__init__(rules, color, row, column, image)
        self.notation = 'K'
        # Indicates whether the king has moved or not
        self.first_move = True

    def in_check(self, board):
        if board.config.rules["giveaway"] == True:
            return False
        for row, column in board.board.keys():
            # Empty tile
            if board.is_empty(row, column):
                continue
            # Not opponent's piece
            if board.get_piece(row, column).color == board.turn:
                continue
            opponent = board.get_piece(row, column)
            opponent.calc_moves(board, row, column, board.flipped, ep_square=board.ep_square)
            if (self.row, self.column) in opponent.moves:
                return True
        return False

    def calc_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        self.moves = []
        for d_row, d_col in queen_directions:
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                if board.is_empty(new_row, new_col) or board.is_enemy(new_row, new_col, self):
                    self.moves.append((new_row, new_col))

        # Castling
        if self.first_move and board.config.rules["no_castling"] == False and board.config.rules["giveaway"] == False and not self.in_check():
            rooks = {1: None, -1: None}

            # 1 = O-O-O, -1 = O-O
            for d in [1, -1]:
                for i in range(flip_coords(0, flipped=d*flipped), column, d*flipped):
                    # Skip if empty square or not a piece
                    #TODO what?
                    if board.is_empty(row, i):
                        continue
                    if rooks[d] is not None:
                        rooks[d] = None
                        break
                    piece = board.get_piece(row, i)
                    if piece.notation == "R" and piece.first_move and piece.is_ally(self):
                        rooks[d] = i

            for d in [1, -1]:
                if rooks[d] is None:
                    continue
                if all(board.is_empty(row, i) or i == rooks[d] for i in range(min(flip_coords(i, flipped=d*flipped), flip_coords(get_value(d, 2, 6), flipped=d*flipped)), column, d*flipped)):
                    self.moves.append((row, rooks[d]))