import pygame

from constants import window, gamemodes, config, BROWN, WHITE, square_size
from GUI import draw_text
from math import ceil

class Label:
    def __init__(self, c_x: float, c_y: float, text: str, color: tuple[int, int, int], c_size: float, font: str = "ocraextended") -> None:
        # c_x, c_y, c_size are coefficient multipliers of the screen resolution
        self.c_x = c_x
        self.c_y = c_y
        self.text = text
        self.color = color
        self.c_size = c_size
        self.font = font

    def refresh(self) -> None:
        """
        Refreshes the position of the label based on the current screen resolution.

        Returns:
            None
        """
        self.x = self.c_x * pygame.display.Info().current_w
        self.y = self.c_y * pygame.display.Info().current_h

    def draw(self) -> None:
        """
        Draws the label on the screen.

        Parameters:
        - None

        Returns:
        - None
        """
        draw_text(self.text, self.color, round(self.c_size * pygame.display.Info().current_h), (self.c_x * pygame.display.Info().current_w, self.c_y * pygame.display.Info().current_h), self.font)

class Button:
    def __init__(self, c_x: float, c_y: float, c_width: float, c_height: float, color: tuple[int, int, int], text: str, text_color: tuple[int, int, int], c_text_size: float, font: str = "ocraextended") -> None:
        # c_x, c_y, c_width, c_height, c_size are coefficient multipliers of the screen resolution
        self.c_x = c_x
        self.c_y = c_y
        self.c_width = c_width
        self.c_height = c_height
        self.rect = pygame.Rect(ceil(pygame.display.Info().current_w * (c_x - 0.5 * c_width)), ceil(pygame.display.Info().current_h * (c_y - 0.5 * c_height)), ceil(self.c_width * pygame.display.Info().current_w), ceil(self.c_height * pygame.display.Info().current_h))
        self.color = color
        self.label = Label(c_x, c_y, text, text_color, c_text_size, font)

    def is_clicked(self) -> bool:
        """
        Check if the button is clicked.

        Returns:
            bool: True if the button is clicked, False otherwise.
        """
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def refresh(self) -> None:
        """
        Refreshes the menu by updating the position and size of the rectangle and refreshing the label.
        """
        self.rect = pygame.Rect(ceil(pygame.display.Info().current_w * (self.c_x - 0.5 * self.c_width)), ceil(pygame.display.Info().current_h * (self.c_y - 0.5 * self.c_height)), ceil(self.c_width * pygame.display.Info().current_w), ceil(self.c_height * pygame.display.Info().current_h))
        self.label.c_x = self.c_x
        self.label.c_y = self.c_y
        self.label.refresh()

    def draw(self) -> None: 
        """
        Draws the button on the screen.

        Raises:
            ValueError: If the button position is not set.
        """
        if self.c_x <= 0 or self.c_y <= 0:
            raise ValueError("Button position not set")
        pygame.draw.rect(window, self.color, self.rect)
        self.label.draw()

    def draw_frame(self) -> None:
        """
        Draws a frame around the button.

        Parameters:
        - None

        Returns:
        - None
        """
        pygame.draw.lines(window, WHITE, True, [(ceil(pygame.display.Info().current_w * (self.c_x - 0.5 * self.c_width)), ceil(pygame.display.Info().current_h * (self.c_y - 0.5 * self.c_height))),
                                                (ceil(pygame.display.Info().current_w * (self.c_x + 0.5 * self.c_width)), ceil(pygame.display.Info().current_h * (self.c_y - 0.5 * self.c_height))),
                                                (ceil(pygame.display.Info().current_w * (self.c_x + 0.5 * self.c_width)), ceil(pygame.display.Info().current_h * (self.c_y + 0.5 * self.c_height))),
                                                (ceil(pygame.display.Info().current_w * (self.c_x - 0.5 * self.c_width)), ceil(pygame.display.Info().current_h * (self.c_y + 0.5 * self.c_height)))], round(square_size / 15))

class Menu:
    def __init__(self, buttons: list[Button] = [], labels: list[Label] = []) -> None:
        self.buttons = buttons
        self.labels = labels

    def draw_menu(self) -> None:
        """
        Draws the menu by iterating over the buttons and labels and calling their draw methods.
        """
        for button in self.buttons:
            button.draw()
        for label in self.labels:
            label.draw()

    def refresh(self) -> None:
        """
        Refreshes the menu by calling the refresh method on each button and label.
        """
        for button in self.buttons:
            button.refresh()
        for label in self.labels:
            label.refresh()

# Initialize the buttons and labels

# Back button is used in the settings and gamemode menus
BACK_BUTTON = Button(1.25*(config["margin"] / pygame.display.Info().current_w), 1.25*(config["margin"] / pygame.display.Info().current_h), 1.5*(config["margin"] / pygame.display.Info().current_w), 1.5*(config["margin"] / pygame.display.Info().current_h), (255, 0, 0), "X", WHITE, 3/52)

# Fen and move labels are used in the game state
FEN_LABEL = Label((config["margin"])/pygame.display.Info().current_w + 4/10, 1 - (config["margin"] * 0.5)/pygame.display.Info().current_h, "", WHITE, 1/52)
MOVE_LABEL = Label((config["margin"])/pygame.display.Info().current_w + 9/10, 1 - (config["margin"] * 0.5)/pygame.display.Info().current_h, "", WHITE, 1/52)

MAIN_MENU = Menu([Button(1/2, 1/2, 8/13, 2/13, BROWN, "PLAY", WHITE, 1/13),
                  Button(1/2, 1/2 + 2/13, 8/13, 2/13, BROWN, "SETTINGS", WHITE, 1/13),
                  Button(1/2, 1/2 + 4/13, 8/13, 2/13, (255, 0, 0), "QUIT", WHITE, 1/13)],
                  [Label(1/2, 3/16, "Chesspy", WHITE, 2/13)])
GAMEMODE_MENU = Menu([Button((0.5*i+1)*(config["margin"] / pygame.display.Info().current_w) + (2*i+1)*(1 - (2+0.5*(len(gamemodes)-1))*(config["margin"] / pygame.display.Info().current_w))/(2*len(gamemodes)), 1/2, (1 - (2+0.5*(len(gamemodes)-1))*(config["margin"] / pygame.display.Info().current_w))/len(gamemodes), (1-5*(config["margin"] / pygame.display.Info().current_h)), BROWN, gamemodes[i], WHITE, 3/104) for i in range(len(gamemodes))] +
                     [BACK_BUTTON])
SETTINGS_MENU = Menu([Button(1/2, 13/52, 4/13, 1/13, BROWN, config["selected_piece_asset"], WHITE, 1/26),
                      Button(1/2, 8/13, 4/13, 1/13, BROWN, config["selected_board_asset"], WHITE, 1/26),
                      Button(1/2, 10/13, 4/13, 1/13, BROWN, config["selected_sound_asset"], WHITE, 1/26),
                      Button(1/2, 12/13, 4/13, 1/13, BROWN, config["selected_background_asset"], WHITE, 1/26),
                      BACK_BUTTON])

# List of menus
menus = [MAIN_MENU, GAMEMODE_MENU, SETTINGS_MENU]