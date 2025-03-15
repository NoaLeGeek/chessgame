from config import config

class Player:
    def __init__(self, color: int):
        self.color = color
        # Pieces' position depending on their type
        self.pieces = {"P": [], "R": [], "N": [], "B": [], "Q": [], "K": []}
        # King's position
        self.king = None
        self.ia = False

    def add_piece(self, piece):
        self.pieces[piece.notation].append(piece)

    def remove_piece(self, piece):
        self.pieces[piece.notation].remove(piece)
        if piece.notation == 'K':
            self.king = None

    def get_moves(self, board):
        moves = []
        for tile in board.board.values():
            if tile is None:
                raise ValueError("Tile is None")
            if board.is_empty(tile.pos):
                continue
            if tile.piece.color != self.color:
                continue
            moves += [board.convert_to_move(tile.pos, to_pos) for to_pos in tile.calc_moves(board)]
        return moves
    
    def is_king_check(self, board):
        if config.rules["giveaway"]:
            return False
        return self.king in [move.to_pos for move in board.get_player(-self.color).get_moves(board)]