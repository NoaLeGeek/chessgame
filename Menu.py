import pygame
from constants import draw_text, square_size

class Menu:
    def __init__(self, buttons = [], labels = []) -> None:
        self.buttons = buttons
        self.labels = labels

    def draw_menu(self, frame):
        for button in self.buttons:
            button.draw(frame)
        for label in self.labels:
            label.draw(frame)

class Button:
    def __init__(self, c_x: float, c_y: float, c_width: float, c_height: float, color: tuple[int, int, int], text: str, text_color: tuple[int, int, int], c_text_size: float, font: str = "CourierNew") -> None:
        self.c_x = c_x
        self.c_y = c_y
        self.c_width = c_width
        self.c_height = c_height
        self.rect = pygame.Rect(round(pygame.display.Info().current_w * (c_x - 0.5 * c_width)), round(pygame.display.Info().current_h * (c_y - 0.5 * c_height)), round(self.c_width * pygame.display.Info().current_w), round(self.c_height * pygame.display.Info().current_h))
        self.color = color
        self.label = Label(c_x, c_y, text, text_color, c_text_size, font)

    def is_clicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def refresh(self):
        self.rect = pygame.Rect(round(pygame.display.Info().current_w * (self.c_x - 0.5 * self.c_width)), round(pygame.display.Info().current_h * (self.c_y - 0.5 * self.c_height)), round(self.c_width * pygame.display.Info().current_w), round(self.c_height * pygame.display.Info().current_h))
        self.label.c_x = self.c_x
        self.label.c_y = self.c_y
        self.label.refresh()

    def draw(self, frame): 
        if self.c_x <= 0 or self.c_y <= 0:
            raise ValueError("Button position not set")
        pygame.draw.rect(frame, self.color, self.rect)
        self.label.draw(frame)

class Label:
    def __init__(self, c_x: float, c_y: float, text: str, color: tuple[int, int, int], c_size: float, font: str = "CourierNew") -> None:
        self.c_x = c_x
        self.c_y = c_y
        self.text = text
        self.color = color
        self.c_size = c_size
        self.font = font

    def refresh(self):
        self.x = self.c_x * pygame.display.Info().current_w
        self.y = self.c_y * pygame.display.Info().current_h

    def draw(self, frame):
        draw_text(frame, self.text, self.color, round(self.c_size * pygame.display.Info().current_h), (self.c_x * pygame.display.Info().current_w, self.c_y * pygame.display.Info().current_h), self.font)

MAIN_MENU = Menu([Button(1/2, 1/2, 8/13, 2/13, (92, 64, 51), "PLAY", (255, 255, 255), 1/13),
                  Button(1/2 - 2/13, 1/2 + 2/13, 4/13, 2/13, (92, 64, 51), "SETTINGS", (255, 255, 255), 1/26),
                  Button(1/2 + 2/13, 1/2 + 2/13, 4/13, 2/13, (92, 64, 51), "CREDITS", (255, 255, 255), 1/26),
                  Button(1/2, 1/2 + 4/13, 8/13, 2/13, (255, 0, 0), "QUIT", (255, 255, 255), 1/13)],
                  [Label(1/2, 3/16, "Chesspy", (255, 255, 255), 2/13)])