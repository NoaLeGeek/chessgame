import random

import pygame

from config import config
from utils import load_image
from scenes.game import Game
from scenes.scene import Scene
from board.player import Player
from constants import Fonts, Colors, available_rule
from gui import RectButton, Label, VideoPlayer, create_rect_surface, RadioButton
from ia.minimax import Minimax
from ia.ml.loader import load_model_from_checkpoint

class SetupMenu(Scene):
    def __init__(self):
        super().__init__()
        self.player1 = Player(1)
        self.player2 = Player(-1)
        self.frame = pygame.Rect(config.width*0.2, config.height*0.2, config.width*0.6, config.height*0.6)
    
    def create_buttons(self):
        button_width = config.width * 0.27
        button_height = config.height * 0.1
        font_size = int(button_height * 0.7)

        self.buttons = {
            "player vs player": RectButton(
                x=config.width*0.6, 
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
                x=config.width*0.6, 
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
                x=config.width*0.6, 
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
                x=config.width*0.4,
                y=config.height*0.305+i*button_height,
                radius=config.height*0.03,
                width=int(config.height*0.005),
                color=Colors.WHITE.value, 
                state=config.rules[rule],
            ) for i, rule in enumerate(available_rule)
        }

    def create_labels(self):
        self.labels = {
            rule : Label(
                center = (config.width*0.3, config.height*0.305+(i*config.height*0.1)),
                text = rule.replace('_', ' ') if rule != 'king_of_the_hill' else 'koth',
                font_name=Fonts.GEIZER,
                font_size=int(config.height*0.08),
                color = Colors.WHITE.value
            )
            for i, rule in enumerate(available_rule)
        }

    def render(self, screen):
        screen.fill(Colors.BLACK.value)
        pygame.draw.rect(screen, Colors.DARK_GRAY.value, self.frame)
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
        for rule in available_rule:
            if config.rules[rule]:
                config.rules[rule] = False
        config.rules[rule] = not config.rules[rule]
        button.state = True
        for b in self.rule_buttons.values():
            if button is not b :
                b.state = False

class PlayerVsIaMenu(Scene):
    def __init__(self, player1, player2):
        super().__init__()
        self.player1, self.player2 = player1, player2
        self.selected_color = 1
        self.frame = pygame.Rect(config.width*0.2, config.height*0.2, config.width*0.6, config.height*0.6)

    def create_buttons(self):
        self.buttons = {
             "play": RectButton(
                x=config.width*0.65, 
                y=config.height*0.7, 
                width=config.width*0.2, 
                height=config.height*0.1, 
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='check this out !',
                font_name=Fonts.GEIZER, 
                font_size=int(config.height*0.06), 
                text_color=Colors.BLACK.value, 
                command=lambda:self.manager.go_to(Game(self.player1 if self.player1.color == 1 else self.player2, self.player1 if self.player1.color == -1 else self.player2)),
             ),
            'white':RectButton(
                x=config.width*0.25,
                y = config.height*0.7,
                width=config.tile_size,
                height=config.tile_size,
                border_radius=1,
                color=Colors.WHITE.value, 
                image = load_image('assets/piece/alpha/wK.svg', (config.tile_size, config.tile_size)),
                command=lambda:self.update_color(1)
            ),
            'black':RectButton(
                x=config.width*0.35,
                y = config.height*0.7,
                width=config.tile_size,
                height=config.tile_size,
                color=Colors.BLACK.value, 
                image = load_image('assets/piece/alpha/bK.svg', (config.tile_size, config.tile_size)),
                command=lambda:self.update_color(-1)
            ),
            'random_color':RectButton(
                x=config.width*0.45,
                y = config.height*0.7,
                width=config.tile_size,
                height=config.tile_size,
                color=Colors.GRAY.value, 
                command=lambda:self.update_color('random_color')
            )
        }

        self.ia_buttons = {
            ia : RadioButton(
                x=config.width*0.51,
                y=config.height*0.305+i*config.height * 0.1,
                radius=config.height*0.03,
                width=int(config.height*0.005),
                color=Colors.RED.value if (ia == 'nn' and not config.rules['classic']) else Colors.WHITE.value,
                state=False
            )
            for i, ia in enumerate(['random_ia', 'minimax', 'nn'])
        }
        self.buttons.update(self.ia_buttons)

    def create_labels(self):
         self.labels = {
            ia : Label(
                center = (config.width*0.35, config.height*0.305+(i*config.height*0.1)),
                text = ia,
                font_name=Fonts.GEIZER,
                font_size=int(config.height*0.08),
                color = Colors.RED.value if (ia == 'neural network' and not config.rules['classic']) else Colors.WHITE.value,
            )
            for i, ia in enumerate(['random', 'minimax', 'neural network'])
        }

    def update_color(self, color):
        if color != 'random_color':
            self.player1.color = color
            self.player2.color = -color
        else :
            self.player1.color = random.choice((1, -1))
            self.player2.color = -self.player1.color
        self.selected_color = color
    
    def render(self, screen):
        screen.fill('black')
        pygame.draw.rect(screen, Colors.DARK_GRAY.value, self.frame)
        super().render(screen)
        if self.selected_color == 1 :
            pygame.draw.rect(screen, Colors.GREEN.value, self.buttons['white'].rect, 2)
        elif self.selected_color == -1 :
            pygame.draw.rect(screen, Colors.GREEN.value, self.buttons['black'].rect, 2)
        elif self.selected_color == 'random_color' :
            pygame.draw.rect(screen, Colors.GREEN.value, self.buttons['random_color'].rect, 2)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 :
                for ia, button in self.ia_buttons.items():
                    if button.is_clicked() and (ia =='nn' and config.rules['classic'] or ia != 'nn'): 
                        print(ia, config.rules['classic'])
                        self.update_ia(ia, button)

    def update_ia(self, ia, button):
        button.state = True
        for b in self.ia_buttons.values():
            if button is not b :
                b.state = False
                print(b)
        

    
        
        

