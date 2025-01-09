import pygame
from constants import bishop_directions, rook_directions, queen_directions, knight_directions, castling_king_column
from utils import flip_pos
from config import config

@staticmethod
def notation_to_piece(notation: str):
    return {'P':Pawn, 'K':King, 'R':Rook, 'B':Bishop, 'N':Knight, 'Q':Queen}[notation.upper()]
    
@staticmethod
def piece_to_notation(piece: "Piece"):
    return {Pawn:'P', King:'K', Rook:'R', Bishop:'B', Knight:'N', Queen:'Q'}[piece]

class Piece():
    def __init__(self, color: int, image: pygame.Surface = None) -> None:
        self.color = color
        self.moves = []
        self.image = image

    def is_ally(self, piece: "Piece") -> bool:
        return self.color == piece.color
    
    def is_enemy(self, piece: "Piece") -> bool:
        return not self.is_ally(piece)
    
    def update_image(self, image: pygame.Surface) -> None:
        self.image = image

class Pawn(Piece):
    def __init__(self, color: int, image: pygame.Surface = None):
        super().__init__(color, image)
        self.notation = 'P'
        self.promotion = (Queen, Rook, Bishop, Knight)

    def calc_moves(self, board, from_pos: tuple[int, int]) -> None:
        self.moves = []
        d = self.color * board.flipped
        # Déplacement de base vers l'avant
        if board.in_bounds((from_pos[0] - d, from_pos[1])) and board.is_empty((from_pos[0] - d, from_pos[1])):
            self.moves.append((from_pos[0] - d, from_pos[1]))
            # Premier déplacement du pion (2 cases vers l'avant)
            if from_pos[0] in [1, config.rows-2] and board.in_bounds((from_pos[0] - 2*d, from_pos[1])) and board.is_empty((from_pos[0] - 2*d, from_pos[1])):
                self.moves.append((from_pos[0] - 2*d, from_pos[1]))

        # Capture diagonale et en passant
        for d_pos in [(-d, -1), (-d, 1)]:  # Diagonales
            new_pos = (from_pos[0] + d_pos[0], from_pos[1] + d_pos[1])
            if not board.in_bounds(new_pos):
                continue
            # En passant
            if board.ep == new_pos and not board.is_empty((from_pos[0], from_pos[1] + d_pos[1])) and board.get_piece((from_pos[0], from_pos[1] + d_pos[1])).is_enemy(self):
                self.moves.append(new_pos)
            # Capture normale 
            if board.is_empty(new_pos):
                continue
            piece = board.get_piece(new_pos)
            if piece.is_enemy(self):
                self.moves.append(new_pos)
        return self.moves


class Rook(Piece):
    def __init__(self, color: int, image: pygame.Surface = None):
        super().__init__(color, image)
        self.notation = 'R'

    def calc_moves(self, board, from_pos: tuple[int, int]) -> None:
        self.moves = []
        for d_pos in rook_directions:
            new_pos = (from_pos[0] + d_pos[0], from_pos[1] + d_pos[1])
            while board.in_bounds(new_pos):
                if board.is_empty(new_pos):
                    self.moves.append(new_pos)
                elif board.get_piece(new_pos).is_enemy(self):
                    self.moves.append(new_pos)
                    break
                else:
                    break
                new_pos = (new_pos[0] + d_pos[0], new_pos[1] + d_pos[1])
        return self.moves

class Bishop(Piece):
    def __init__(self, color: int, image: pygame.Surface = None):
        super().__init__( color, image)
        self.notation = 'B'

    def calc_moves(self, board, from_pos: tuple[int, int]) -> None:
        self.moves = []
        for d_pos in bishop_directions:
            new_pos = (from_pos[0] + d_pos[0], from_pos[1] + d_pos[1])
            while board.in_bounds(new_pos):
                if board.is_empty(new_pos):
                    self.moves.append(new_pos)
                elif board.get_piece(new_pos).is_enemy(self):
                    self.moves.append(new_pos)
                    break
                else:
                    break
                new_pos = (new_pos[0] + d_pos[0], new_pos[1] + d_pos[1])
        return self.moves


class Knight(Piece):
    def __init__(self, color: int, image: pygame.Surface = None):
        super().__init__( color, image)
        self.notation = 'N'

    def calc_moves(self, board, from_pos: tuple[int, int]) -> None:
        self.moves = []
        for d_pos in knight_directions:
            new_pos = (from_pos[0] + d_pos[0], from_pos[1] + d_pos[1])
            if board.in_bounds(new_pos):
                if board.is_empty(new_pos) or board.get_piece(new_pos).is_enemy(self):
                    self.moves.append(new_pos)
        return self.moves


class Queen(Piece):
    def __init__(self, color: int, image: pygame.Surface = None):
        super().__init__(color, image)
        self.notation = 'Q'

    def calc_moves(self, board, from_pos: tuple[int, int]) -> None:
        self.moves = []
        for d_pos in queen_directions:
            new_pos = (from_pos[0] + d_pos[0], from_pos[1] + d_pos[1])
            while board.in_bounds(new_pos):
                if board.is_empty(new_pos):  # Case non occupée
                    self.moves.append(new_pos)
                elif board.get_piece(new_pos).is_enemy(self):  # Pièce ennemie
                    self.moves.append(new_pos)
                    break
                else:  # Pièce alliée
                    break
                new_pos = (new_pos[0] + d_pos[0], new_pos[1] + d_pos[1])
        return self.moves

    
class King(Piece):
    def __init__(self, color: int, image: pygame.Surface = None):
        super().__init__(color, image)
        self.notation = 'K'

    def calc_moves(self, board, from_pos: tuple[int, int]) -> None:
        self.moves = []
        for d_pos in queen_directions:
            new_pos = (from_pos[0] + d_pos[0], from_pos[1] + d_pos[1])
            if board.in_bounds(new_pos) and (board.is_empty(new_pos) or board.get_piece(new_pos).is_enemy(self)):
                self.moves.append(new_pos)
        # Castling
        if not board.is_king_checked():
            rooks = {1: None, -1: None}
            # -1 = O-O-O, 1 = O-O
            # Calculate possible castling
            possible_castling = []
            if board.castling[self.color][1]:
                possible_castling.append(1)
            if board.castling[self.color][-1]:
                possible_castling.append(-1)
            # Find the rook(s) that can castle
            for d in possible_castling:
                for i in range(flip_pos(0, flipped=-d*board.flipped), from_pos[1], -d*board.flipped):
                    # Skip if empty square
                    if board.is_empty((from_pos[0], i)):
                        continue
                    if rooks[d] is not None:
                        rooks[d] = None
                        break
                    piece = board.get_piece((from_pos[0], i))
                    if piece.notation == "R" and piece.is_ally(self):
                        rooks[d] = i
            # Check if the squares between the king and the found rook(s) are empty
            for d in possible_castling:
                if rooks[d] is None:
                    continue
                if all(board.is_empty((from_pos[0], i)) or i == rooks[d] for i in range(min(flip_pos(i, flipped=-d*board.flipped), flip_pos(castling_king_column[d], flipped=-d*board.flipped)), from_pos[1], -d*board.flipped)):
                    self.moves.append((from_pos[0], rooks[d]))
        return self.moves
