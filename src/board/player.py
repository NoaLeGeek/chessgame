class Player:
    def __init__(self, color: int):
        self.color = color
        # Pieces' position depending on their type
        self.pieces = {"P": [], "R": [], "N": [], "B": [], "Q": [], "K": []}
        # King's position
        self.king = None
        self.ia = None

    def add_piece(self, piece):
        self.pieces[piece.notation].append(piece)
        if piece.notation == 'K':
            self.king = piece

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
            moves += tile.calc_moves(board)
        return moves
    
    def is_king_check(self, board, opponent):
        return self.king in opponent.get_moves(board)