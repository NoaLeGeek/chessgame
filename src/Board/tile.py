import pygame
class Tile:
    def __init__(self, row, column, size, margin):
        self.row = row
        self.column = column
        self.size = size
        self.x = column*size + margin
        self.y = row*size + margin
        self.highlight_color = None

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