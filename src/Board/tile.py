import pygame

class Tile:
    def __init__(self, row, column, size):
        self.row = row
        self.column = column
        self.size = size
        self.x = column*size + size//2
        self.y = row*size + size + size//2
        self.object = None
        self.highlight_color = None

    def get_position(self):
        return (9-self.x, self.y+1)
    
    def draw(self, screen):
        pygame.draw.rect(screen, 'black', (self.x, self.y, self.size, self.size), 1)

