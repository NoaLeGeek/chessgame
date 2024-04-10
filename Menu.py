import pygame
from constants import draw_text

class Menu:
    def __init__(self, game) -> None:
        self.game = game
        self.buttons = []
        self.texts = []

class Button:
    def __init__(self, width, height, color, text) -> None:
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (width // 2, height // 2)
        self.width = width
        self.height = height
        self.color = color
        self.text = text

    def is_clicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, frame, size): 
        pygame.draw.rect(frame, self.color, self.rect)
        draw_text(frame, self.text, (255, 255, 255), size, self.rect.center)