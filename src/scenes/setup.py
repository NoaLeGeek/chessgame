import pygame

from config import config
from utils import load_image
from scenes.game import Game
from scenes.scene import Scene
from board.player import Player
from ia.minimax import RandomIA
from constants import Fonts, Colors, available_rule
from gui import RectButton, Label, VideoPlayer, create_rect_surface, RadioButton

class SetupMenu(Scene):
    def __init__(self):
        super().__init__()
        self.player1 = RandomIA(1)
        self.player2 = Player(-1)
    
    def create_buttons(self):
        button_width = config.width * 0.27
        button_height = config.height * 0.1
        font_size = int(button_height * 0.7)

        self.buttons = {
            "player vs player": RectButton(
                x=config.width*0.5, 
                y=config.height*0.3, 
                width=button_width, 
                height=button_height, 
                border_radius=int(button_height//2), 
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='PLAYER VS PLAYER',
                font_name=Fonts.GEIZER, 
                font_size=font_size, 
                text_color=Colors.BLACK.value, 
                command=lambda:self.manager.go_to(Game(self.player1, self.player2))
            ),
            "player vs ia": RectButton(
                x=config.width*0.5, 
                y=config.height*0.5, 
                width=button_width, 
                height=button_height, 
                border_radius=int(button_height//2), 
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value, 
                text='PLAYER VS IA', 
                font_name=Fonts.GEIZER, 
                font_size=font_size, 
                text_color=Colors.BLACK.value, 
                command=lambda:self.manager.go_to(PlayerVsIaMenu(self.player1, self.player2))
            ),
            "ia vs ia": RectButton(
                x=config.width*0.5, 
                y=config.height*0.7, 
                width=button_width, 
                height=button_height, 
                border_radius=int(button_height//2), 
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='IA VS IA', 
                font_name=Fonts.GEIZER, 
                font_size=font_size, 
                text_color=Colors.BLACK.value, 
                command=lambda:self.manager.go_to(Game(self.player1, self.player2))
            )
        }

        self.rule_buttons = {
            rule: RadioButton(
                x=config.width*0.18,
                y=config.height*0.355+i*button_height,
                radius=config.height*0.03,
                width=int(config.height*0.005),
                color=Colors.WHITE.value, 
                state=config.rules[rule],
            ) for i, rule in enumerate(available_rule)
        }


    def render(self, screen):
        screen.fill(Colors.BLACK.value)
        super().render(screen)
        for button in self.rule_buttons.values():
            button.draw(screen)
    
    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 :
                for rule, button in self.rule_buttons.items():
                    if button.is_clicked():
                        self.update_rule(rule, button)

    def update_rule(self, rule, button):
        config.rules[rule] = not config.rules[rule]
        button.state = True
        for b in self.rule_buttons.values():
            if button is not b :
                b.state = False


class PlayerVsIaMenu(Scene):
    def __init__(self, player1, player2):
        super().__init__()

    def create_buttons(self):
        self.buttons = {
            'white':RectButton(
                x=config.width*0.3,
                y = config.height*0.7,
                width=config.tile_size,
                height=config.tile_size,
                border_radius=1,
                color=Colors.WHITE.value, 
                image = load_image('assets/piece/alpha/wK.svg', (config.tile_size, config.tile_size)),
            ),
            'black':RectButton(
                x=config.width*0.5,
                y = config.height*0.7,
                width=config.tile_size,
                height=config.tile_size,
                color=Colors.BLACK.value, 
                image = load_image('assets/piece/alpha/bK.svg', (config.tile_size, config.tile_size)),
            ),
            'random':RectButton(
                x=config.width*0.7,
                y = config.height*0.7,
                width=config.tile_size,
                height=config.tile_size,
                color=Colors.GRAY.value, 

            )
        }
