import pygame
from constants import bishop_directions, rook_directions, queen_directions, knight_directions
from utils import flip_coords, get_value

@staticmethod
def notation_to_piece(notation: str):
    return {'P':Pawn, 'K':King, 'R':Rook, 'B':Bishop, 'N':Knight, 'Q':Queen}[notation.upper()]
    
@staticmethod
def piece_to_notation(piece: "Piece"):
    return {Pawn:'P', King:'K', Rook:'R', Bishop:'B', Knight:'N', Queen:'Q'}[piece.__class__]

class Piece():
    def __init__(self, rules, color: int, image: pygame.Surface = None) -> None:
        self.color = color
        self.moves = []
        self.image = image

    def can_move(self, board, to: tuple[int, int]) -> bool:
        row, column = to
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

    def is_ally(self, piece: "Piece") -> bool:
        return self.color == piece.color
    
    def is_enemy(self, piece: "Piece") -> bool:
        return not self.is_ally(piece)

class Pawn(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
        self.notation = 'P'
        if rules["no_promotion"] == False:
            self.promotion = (Queen, Rook, Bishop, Knight) if rules["giveaway"] == True else King
        # Indicates whether the pawn has moved or not
        self.first_move = True

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        row, column = from_
        self.moves = []
        d = self.color * board.flipped
        ep = kwds["ep"] if "ep" in kwds else None
        # Déplacement de base vers l'avant
        if 0 <= row - d < board.config.rows and board.is_empty(row - d, column):
            self.moves.append((row - d, column))
            # Premier déplacement du pion (2 cases vers l'avant)
            if self.first_move and 0 <= row - 2 * d < board.config.rows and board.is_empty(row - 2 * d, column):
                self.moves.append((row - 2 * d, column))

        # Capture diagonale et en passant
        for d_row, d_col in [(-d, -1), (-d, 1)]:  # Diagonales
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                if board.is_empty(new_row, new_col):
                    continue
                piece = board.get_piece(new_row, new_col)
                # Capture normale
                if piece.is_enemy(self):
                    self.moves.append((new_row, new_col))
                # Capture en passant
                if ep is not None and ep == (new_row, new_col):
                    self.moves.append((new_row, new_col))


class Rook(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
        self.notation = 'R'
        # Indicates whether the rook has moved or not
        self.first_move = True

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        row, column = from_
        self.moves = []
        for d_row, d_col in rook_directions:
            row_temp, column_temp = row + d_row, column + d_col
            while 0 <= row_temp < board.config.rows and 0 <= column_temp < board.config.columns:
                if board.is_empty(row_temp, column_temp):
                    self.moves.append((row_temp, column_temp))
                elif board.get_piece(row_temp, column_temp).is_enemy(self):
                    self.moves.append((row_temp, column_temp))
                    break
                else:
                    break
                row_temp += d_row
                column_temp += d_col

class Bishop(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
        self.notation = 'B'

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        row, column = from_
        self.moves = []
        for d_row, d_col in bishop_directions:
            row_temp, column_temp = row + d_row, column + d_col
            while 0 <= row_temp < board.config.rows and 0 <= column_temp < board.config.columns:
                # Case non occupée
                if board.is_empty(row_temp, column_temp):
                    self.moves.append((row_temp, column_temp))
                # Pièce ennemie
                elif board.get_piece(row_temp, column_temp).is_enemy(self):  
                    self.moves.append((row_temp, column_temp))
                    break
                # Pièce alliée
                else:  
                    break
                row_temp += d_row
                column_temp += d_col


class Knight(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
        self.notation = 'N'

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        row, column = from_
        self.moves = []
        for d_row, d_col in knight_directions:
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                if board.is_empty(new_row, new_col) or board.get_piece(new_row, new_col).is_enemy(self):
                    self.moves.append((new_row, new_col))


class Queen(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
        self.notation = 'Q'

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        row, column = from_
        self.moves = []
        for d_row, d_col in queen_directions:
            row_temp, column_temp = row + d_row, column + d_col
            while 0 <= row_temp < board.config.rows and 0 <= column_temp < board.config.columns:
                if board.is_empty(row_temp, column_temp):  # Case non occupée
                    self.moves.append((row_temp, column_temp))
                elif board.get_piece(row_temp, column_temp).is_enemy(self):  # Pièce ennemie
                    self.moves.append((row_temp, column_temp))
                    break
                else:  # Pièce alliée
                    break
                row_temp += d_row
                column_temp += d_col

    
class King(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
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
            opponent.calc_moves(board, row, column, board.flipped, ep=board.ep)
            if (self.row, self.column) in opponent.moves:
                return True
        return False

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        row, column = from_
        self.moves = []
        for d_row, d_col in queen_directions:
            new_row, new_col = row + d_row, column + d_col
            if 0 <= new_row < board.config.rows and 0 <= new_col < board.config.columns:
                if board.is_empty(new_row, new_col) or board.get_piece(new_row, new_col).is_enemy(self):
                    self.moves.append((new_row, new_col))

        # Castling
        if self.first_move and board.config.rules["no_castling"] == False and board.config.rules["giveaway"] == False and not self.in_check():
            rooks = {1: None, -1: None}

            # 1 = O-O-O, -1 = O-O
            # Find the rook(s) that can castle
            for d in [1, -1]:
                for i in range(flip_coords(0, flipped=d*board.flipped), column, d*board.flipped):
                    # Skip if empty square
                    if board.is_empty(row, i):
                        continue
                    if rooks[d] is not None:
                        rooks[d] = None
                        break
                    piece = board.get_piece(row, i)
                    if piece.notation == "R" and piece.first_move and piece.is_ally(self):
                        rooks[d] = i

            # Check if the squares between the king and the found rook(s) are empty
            for d in [1, -1]:
                if rooks[d] is None:
                    continue
                if all(board.is_empty(row, i) or i == rooks[d] for i in range(min(flip_coords(i, flipped=d*board.flipped), flip_coords(get_value(d, 2, 6), flipped=d*board.flipped)), column, d*board.flipped)):
                    self.moves.append((row, rooks[d]))