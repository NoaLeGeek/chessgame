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

    def get_position(self):
        return (9-self.x, self.y+1)
    
    def draw(self, screen):
        pygame.draw.rect(screen, 'black', (self.x, self.y, self.size, self.size), 1)

