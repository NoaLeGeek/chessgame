import pygame
from constants import draw_text

class Menu:
    def __init__(self, buttons = [], labels = []) -> None:
        self.buttons = buttons
        self.labels = labels

    def draw_menu(self, frame):
        for button in self.buttons:
            button.draw(frame, 30)
        for label in self.labels:
            draw_text(frame, label.text, (255, 255, 255), 30, (label.x, label.y))

class Button:
    def __init__(self, x, y, width, height, color, text) -> None:
        self.x = x
        self.y = y
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x + width // 2, y + height // 2)
        self.width = width
        self.height = height
        self.color = color
        self.label = Label(x + width // 2, y + height // 2, text)

    def is_clicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, frame, size): 
        pygame.draw.rect(frame, self.color, self.rect)
        self.label.draw(frame, size)

class Label:
    def __init__(self, x, y, text) -> None:
        self.x = x
        self.y = y
        self.text = text

    def draw(self, frame, size):
        draw_text(frame, self.text, (255, 255, 255), size, (self.x, self.y))

MAIN_MENU = Menu([Button(200, 600, 200, 100, "blue", "PLAY"),
                  Button(200, 700, 100, 100, "blue", "SETTINGS"),
                  Button(450, 600, 100, 100, "blue", "CREDITS"),
                  Button(200, 800, 200, 100, "red", "QUIT")], [Label(200, 100, "Chesspy")])