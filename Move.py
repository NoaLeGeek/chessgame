import Pieces

class Move:
    #TODO game.move() should be moved here too?
    def __init__(self, game, from_, to, piece, capture=False, promotion=False):
        self.game = game
        self.from_ = from_
        self.to = to
        self.piece = piece
        self.capture = capture
        self.promotion = promotion

    def make_move(self):
        row, column = self.to[0], self.to[1]
        piece = self.game.board.board[row][column]
        self.game.remove(piece, row, column)
        self.game.move(self.game.selected, row, column)
        self.game.change_turn()
        print("turn", self.game.turn)
        self.game.valid_moves = []
        self.game.selected = None
        for row in self.game.board.board:
            print(row)
        self.game.check_game()

    def promote(self, type: Pieces.Piece):
        self.game.remove(self.game.board.board[7*(1 - self.game.selected.color)//2][self.game.selected.column + self.game.selected.promotion[1]], 7*(1 - self.game.selected.color)//2, self.game.selected.column + self.game.selected.promotion[1])
        self.game.move(self.game.selected, 7*(1 - self.game.selected.color)//2, self.game.selected.column + self.game.selected.promotion[1])
        self.game.board.board[7*(1 - self.game.selected.color)//2][self.game.selected.column] = type(self.game.selected.color, 7*(1 - self.game.selected.color)//2, self.game.selected.column)
        self.game.change_turn()
        print("turn", self.game.turn)
        self.game.valid_moves = []
        self.game.selected = None
        self.game.check_game()