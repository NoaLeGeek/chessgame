import pygame

class Tile:
    def __init__(self, row, column, size, margin):
        self.row = row
        self.column = column
        self.size = size
        self.x = column*size + margin
        self.y = row*size + margin
        self.object = None
        self.highlight_color = None
    
    def draw(self, screen):
        pygame.draw.rect(screen, 'black', (self.x, self.y, self.size, self.size), 1)

    def get_color(self):
        r, g, b = None, None, None
        match self.highlight_color:
            case 0:
                r, g, b = 255, 0, 0
            # Shift + Right click
            case 1:
                r, g, b = 0, 255, 0
            # Ctrl + Right click
            case 2:
                r, g, b = 255, 165, 0
            # History move
            case 3:
                r, g, b = 255, 255, 0
            # Selected piece
            case 4:
                r, g, b = 0, 255, 255
        return r, g, b
        