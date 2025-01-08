class Player:
    def __init__(self, notation:int):
        self.notation = notation 
        self.pieces = []
        self.king = None

    def add_piece(self, piece):
        self.pieces.append(piece)
        if piece.notation == 'K':
            self.king = piece

    def get_moves(self, board):
        moves = []
        for piece in self.pieces :
            moves += piece.get_moves(piece.row, piece.column, board)
        return moves
            
    def get_piece_from_reserve(self, column):
        piece_type = list(self.reserve.keys())[column - 1]
        if self.reserve[piece_type]:
            piece = self.reserve[piece_type][0]
            return piece
        return None
    
    def is_king_check(self, board, opponent):
        return (self.king.row, self.king.column) in opponent.get_moves(board)