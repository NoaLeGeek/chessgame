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
        self.moves = []
        d = self.color * board.flipped
        # Déplacement de base vers l'avant
        if board.in_bounds((from_[0] - d, from_[1])) and board.is_empty((from_[0] - d, from_[1])):
            self.moves.append((from_[0] - d, from_[1]))
            # Premier déplacement du pion (2 cases vers l'avant)
            if self.first_move and board.in_bounds((from_[0] - 2*d, from_[1])) and board.is_empty((from_[0] - 2*d, from_[1])):
                self.moves.append((from_[0] - 2*d, from_[1]))

        # Capture diagonale et en passant
        for d_pos in [(-d, -1), (-d, 1)]:  # Diagonales
            new_pos = (from_[0] + d_pos[0], from_[1] + d_pos[1])
            if board.in_bounds(new_pos):
                if board.is_empty(new_pos):
                    continue
                piece = board.get_piece(new_pos)
                # Capture normale
                if piece.is_enemy(self):
                    self.moves.append(new_pos)
                # Capture en passant
                if board.ep is not None and board.ep == new_pos:
                    self.moves.append(new_pos)


class Rook(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
        self.notation = 'R'
        # Indicates whether the rook has moved or not
        self.first_move = True

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        self.moves = []
        for d_pos in rook_directions:
            new_pos = (from_[0] + d_pos[0], from_[1] + d_pos[1])
            while board.in_bounds(new_pos):
                if board.is_empty(new_pos):
                    self.moves.append(new_pos)
                elif board.get_piece(new_pos).is_enemy(self):
                    self.moves.append(new_pos)
                    break
                else:
                    break
                new_pos = (new_pos[0] + d_pos[0], new_pos[1] + d_pos[1])

class Bishop(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
        self.notation = 'B'

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        self.moves = []
        for d_pos in bishop_directions:
            new_pos = (from_[0] + d_pos[0], from_[1] + d_pos[1])
            while board.in_bounds(new_pos):
                if board.is_empty(new_pos):
                    self.moves.append(new_pos)
                elif board.get_piece(new_pos).is_enemy(self):
                    self.moves.append(new_pos)
                    break
                else:
                    break
                new_pos = (new_pos[0] + d_pos[0], new_pos[1] + d_pos[1])


class Knight(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
        self.notation = 'N'

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        self.moves = []
        for d_pos in knight_directions:
            new_pos = (from_[0] + d_pos[0], from_[1] + d_pos[1])
            if board.in_bounds(new_pos):
                if board.is_empty(new_pos) or board.get_piece(new_pos).is_enemy(self):
                    self.moves.append(new_pos)


class Queen(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
        self.notation = 'Q'

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        self.moves = []
        for d_pos in queen_directions:
            new_pos = (from_[0] + d_pos[0], from_[1] + d_pos[1])
            while board.in_bounds(new_pos):
                if board.is_empty(new_pos):  # Case non occupée
                    self.moves.append(new_pos)
                elif board.get_piece(new_pos).is_enemy(self):  # Pièce ennemie
                    self.moves.append(new_pos)
                    break
                else:  # Pièce alliée
                    break
                new_pos = (new_pos[0] + d_pos[0], new_pos[1] + d_pos[1])

    
class King(Piece):
    def __init__(self, rules, color: int, image: pygame.Surface = None):
        super().__init__(rules, color, image)
        self.notation = 'K'
        # Indicates whether the king has moved or not
        self.first_move = True

    def calc_moves(self, board, from_: tuple[int, int], **kwds) -> None:
        self.moves = []
        for d_pos in queen_directions:
            new_pos = (from_[0] + d_pos[0], from_[1] + d_pos[1])
            if board.in_bounds(new_pos) and (board.is_empty(new_pos) or board.get_piece(new_pos).is_enemy(self)):
                self.moves.append(new_pos)

        # Castling
        if self.first_move and board.config.rules["no_castling"] == False and board.config.rules["giveaway"] == False and not board.in_check():
            rooks = {1: None, -1: None}

            # 1 = O-O-O, -1 = O-O
            # Find the rook(s) that can castle
            for d in [1, -1]:
                for i in range(flip_coords(0, flipped=d*board.flipped), from_[1], d*board.flipped):
                    # Skip if empty square
                    if board.is_empty((from_[0], i)):
                        continue
                    if rooks[d] is not None:
                        rooks[d] = None
                        break
                    piece = board.get_piece((from_[0], i))
                    if piece.notation == "R" and piece.first_move and piece.is_ally(self):
                        rooks[d] = i

            # Check if the squares between the king and the found rook(s) are empty
            for d in [1, -1]:
                if rooks[d] is None:
                    continue
                if all(board.is_empty((from_[0], i)) or i == rooks[d] for i in range(min(flip_coords(i, flipped=d*board.flipped), flip_coords(get_value(d, 2, 6), flipped=d*board.flipped)), from_[1], d*board.flipped)):
                    self.moves.append((from_[0], rooks[d]))