class Move:
    def __init__(self, from_, to, piece, capture=False, promotion=False):
        self.from_ = from_
        self.to = to
        self.piece = piece
        self.capture = capture
        self.promotion = promotion
