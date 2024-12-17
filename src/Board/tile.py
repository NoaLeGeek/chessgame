import pygame
class Tile:
    def __init__(self, board, row, column, size):
        self.board = board
        self.row = row
        self.column = column
        self.size = size
        self.calc_position(board.config.margin)
        self.highlight_color = None
        self.piece = None

    def get_square_color(self):
        return (self.row + self.column) % 2
    
    def move(self, row: int, column: int) -> None:
        self.row = row
        self.column = column
        self.calc_position(self.board.config.margin)

    def calc_moves(self, **kwds):
        self.piece.calc_moves(self.board, (self.row, self.column), **kwds)

    def calc_position(self, margin):
        self.x, self.y = self.column * self.size + margin, self.row * self.size + margin

    def get_color(self):
        r, g, b = None, None, None
        match self.highlight_color:
            case 0:
                r, g, b = 255, 0, 0, 75
            # Shift + Right click
            case 1:
                r, g, b = 0, 255, 0, 75
            # Ctrl + Right click
            case 2:
                r, g, b = 255, 165, 0, 75
            # History move
            case 3:
                r, g, b = 255, 255, 0, 75
            # Selected piece
            case 4:
                r, g, b = 0, 255, 255, 75
            # Void
            case None:
                r, g, b = 0, 0, 0, 0
        return r, g, b