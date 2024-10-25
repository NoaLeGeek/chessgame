import pygame
from constants import bishop_directions, rook_directions, queen_directions, knight_directions
from utils import flip_coords, get_value
from Board.object import Object

class Piece(Object):
    def __init__(self, rules, color: int, row: int, column: int, image: pygame.Surface = None) -> None:
        super().__init__(row, column)
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
        print("going", (self.row, self.column), (row, column))
        piece_row, piece_column = self.row, self.column
        # When called, (row, column) is empty, is occupied by a object with no hitbox or is occupied by a opponent piece
        # Save the destination square object
        if not board.is_empty(row, column):
            save_tile = board.get_tile(row, column)
        self_tile = board.get_tile(piece_row, piece_column)
        # Swap the piece with the destination square
        board.board[(row, column)] = board.board[(self.row, self.column)]
        print("row, column", row, column)
        print("self.row, self.column", self.row, self.column)
        print("piece_row, piece_column", piece_row, piece_column)
        for r in range(board.config.rows):
            for c in range(board.config.columns):
                if board.board.get((r, c), "a") == "a":
                    print("1", (r, c), "emmpty")
                elif board.board.get((r, c)) is None:
                    print("1", (r, c), "NONE that is not good")
                else:
                    print("1", (r, c), board.board[(r, c)])
        del board.board[(self.row, self.column)]
        print("row, column", row, column)
        print("self.row, self.column", self.row, self.column)
        print("piece_row, piece_column", piece_row, piece_column)
        for r in range(board.config.rows):
            for c in range(board.config.columns):
                if board.board.get((r, c), "a") == "a":
                    print("2", (r, c), "emmpty")
                elif board.board.get((r, c)) is None:
                    print("2", (r, c), "NONE that is not good")
                else:
                    print("2", (r, c), board.board[(r, c)])
        self.row, self.column = row, column
        # Check if the king is in check after the move
        can_move = not board.is_in_check()
        print("row, column", row, column)
        print("self.row, self.column", self.row, self.column)
        print("piece_row, piece_column", piece_row, piece_column)
        for r in range(board.config.rows):
            for c in range(board.config.columns):
                if board.board.get((r, c), "a") == "a":
                    print("3", (r, c), "emmpty")
                elif board.board.get((r, c)) is None:
                    print("3", (r, c), "NONE that is not good")
                else:
                    print("3", (r, c), board.board[(r, c)])
        # Restore the initial state of the board
        board.board[(piece_row, piece_column)] = self_tile
        print("row, column", row, column)
        print("self.row, self.column", self.row, self.column)
        print("piece_row, piece_column", piece_row, piece_column)
        for r in range(board.config.rows):
            for c in range(board.config.columns):
                if board.board.get((r, c), "a") == "a":
                    print("4", (r, c), "emmpty")
                elif board.board.get((r, c)) is None:
                    print("4", (r, c), "NONE that is not good")
                else:
                    print("4", (r, c), board.board[(r, c)])
        if not board.is_empty(row, column):
            board.board[(row, column)] = save_tile
        print("row, column", row, column)
        print("self.row, self.column", self.row, self.column)
        print("piece_row, piece_column", piece_row, piece_column)
        for r in range(board.config.rows):
            for c in range(board.config.columns):
                if board.board.get((r, c), "a") == "a":
                    print("5", (r, c), "emmpty")
                elif board.board.get((r, c)) is None:
                    print("5", (r, c), "NONE that is not good")
                else:
                    print("5", (r, c), board.board[(r, c)])
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
        if 0 <= row - x < board.config.rows and not board.is_occupied(row - x, column):
            self.moves.append((row - x, column))
            # Premier déplacement du pion (2 cases vers l'avant)
            if self.first_move and 0 <= row - 2 * x < board.config.rows and not board.is_occupied(row - 2 * x, column):
                self.moves.append((row - 2 * x, column))

        # Capture diagonale et en passant
        for d_row, d_col in [(-x, -1), (-x, 1)]:  # Diagonales
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                if not board.is_occupied(new_row, new_col):
                    continue
                object = board.get_object(new_row, new_col)
                if not object.is_piece():
                    continue
                # Capture normale
                if object and object.is_enemy(self):
                    self.moves.append((new_row, new_col))
                # Capture en passant
                if ep_square and ep_square == (new_row, new_col):
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
                if not board.is_occupied(row_temp, column_temp):
                    self.moves.append((row_temp, column_temp))
                elif board.get_object(row_temp, column_temp).is_piece() and board.get_object(row_temp, column_temp).is_enemy(self):
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
                if not board.is_occupied(row_temp, column_temp):
                    self.moves.append((row_temp, column_temp))
                # Pièce ennemie
                elif board.get_object(row_temp, column_temp).is_piece() and board.get_object(row_temp, column_temp).is_enemy(self):  
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
                if not board.is_occupied(new_row, new_col) or (board.get_object(new_row, new_col).is_piece() and board.get_object(new_row, new_col).is_enemy(self)):
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
                if not board.is_occupied(row_temp, column_temp):  # Case non occupée
                    self.moves.append((row_temp, column_temp))
                elif board.get_object(row_temp, column_temp).is_piece() and board.get_object(row_temp, column_temp).is_enemy(self):  # Pièce ennemie
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
            # Not a piece
            if not board.get_object(row, column).is_piece():
                continue
            # Not opponent's piece
            if board.get_object(row, column).color == board.turn:
                continue
            opponent = board.get_object(row, column)
            opponent.calc_moves(board, row, column, board.flipped, ep_square=board.ep_square)
            if (self.row, self.column) in opponent.moves:
                return True
        return False

    def calc_moves(self, board: list[list[int | Piece]], row: int, column: int, flipped: bool = False, **kwds) -> list[tuple[int, int]]:
        self.moves = []
        for d_row, d_col in queen_directions:
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                if not board.is_occupied(new_row, new_col) or (board.get_object(new_row, new_col).is_piece() and board.get_object(new_row, new_col).is_enemy(self)):
                    self.moves.append((new_row, new_col))

        # Castling
        if self.first_move and board.config.rules["no_castling"] == False and board.config.rules["giveaway"] == False and not self.in_check():
            rooks = {1: None, -1: None}

            # 1 = O-O-O, -1 = O-O
            for d in [1, -1]:
                for i in range(flip_coords(0, flipped=d*flipped), column, d*flipped):
                    # Skip if empty square or not a piece
                    if not board.is_occupied(row, i) or not board.get_object(row, i).is_piece():
                        continue
                    if rooks[d] is not None:
                        rooks[d] = None
                        break
                    piece = board.get_object(row, i)
                    if piece.notation == "R" and piece.first_move and piece.is_ally(self):
                        rooks[d] = i

            for d in [1, -1]:
                if rooks[d] is None:
                    continue
                if all(board[row][i] == 0 or i == rooks[d] for i in range(min(flip_coords(i, flipped=d*flipped), flip_coords(get_value(d, 2, 6), flipped=d*flipped)), column, d*flipped)):
                    self.moves.append((row, rooks[d]))
                    
            
            # rook = next((board[row][i] for i in range(column - flipped, flip_coords(-1, flipped=flipped), -flipped) if isinstance(board[row][i], Rook) and board[row][i].first_move), None)
            # if rook is not None and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(2, flipped=flipped), column, sign(column - flip_coords(2, flipped=flipped)))) and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(3, flipped=flipped), rook.column, sign(rook.column - flip_coords(3, flipped=flipped)))):
            #     self.moves.append((row, rook.column))
            # rook = next((board[row][i] for i in range(column + flipped, flip_coords(8, flipped = flipped), flipped) if isinstance(board[row][i], Rook) and board[row][i].first_move), None)
            # if rook is not None and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(6, flipped=flipped), column, sign(column - flip_coords(6, flipped=flipped)))) and all((isinstance(board[row][i], King) and board[row][i].is_ally(board[row][column])) or board[row][i] == 0 or board[row][i] == rook for i in range(flip_coords(5, flipped=flipped), rook.column, sign(rook.column - flip_coords(5, flipped=flipped)))):
            #     self.moves.append((row, rook.column))