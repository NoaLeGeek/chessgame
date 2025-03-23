import random

import pygame

from config import config
from utils import load_image
from scenes.game import Game
from scenes.scene import Scene
from board.player import Player
from constants import Fonts, Colors, available_rule
from gui import RectButton, Label, VideoPlayer, create_rect_surface, RadioButton
from ia.negamax import NegamaxAI, RandomAI
from ia.ml.loader import load_model_from_checkpoint

def str_to_ia(ia:str, color, depth=None):
    if 'random' in ia:
        ia = 'random'
    elif 'negamax' in ia:
        ia = 'negamax'
    elif 'neural_network' in ia:
        ia == 'neural_network'
    return {'random':RandomAI(color), 'negamax':NegamaxAI(color, depth), 'neural_network':None}[ia]

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
                command=lambda:self.manager.go_to(PlayerVsIaMenu())
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
                command=lambda:self.manager.go_to(IaVsIaMenu())
            ),
            'back': RectButton(
                x=config.width*0.955,
                y=config.height*0.08, 
                width=config.height*0.1,
                height=config.height*0.1,
                color=Colors.LIGHT_GRAY.value,
                hovered_color=Colors.WHITE.value,
                text='<-',
                text_color=Colors.DARK_GRAY.value,
                font_size=int(config.height*0.1),
                font_name=Fonts.GEIZER,
                command=self.manager.go_back
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
        for r in available_rule:
            if config.rules[r]:
                config.rules[r] = False
        config.rules[rule] = not config.rules[rule]
        button.state = True
        for b in self.rule_buttons.values():
            if button is not b :
                b.state = False

class PlayerVsIaMenu(Scene):
    def __init__(self):
        self.player1 = Player(1)
        self.player2 = RandomAI(-1)
        self.selected_color = 1
        self.frame = pygame.Rect(config.width*0.2, config.height*0.2, config.width*0.6, config.height*0.6)
        self.depth = 2
        super().__init__()

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
                command=self.start_game
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
            ),
             'decrease_depth': RectButton(
                x=config.width*0.67,
                y=config.height*0.305+config.height*0.1, 
                width=config.height*0.1,
                height=config.height*0.1,
                color=Colors.DARK_GRAY.value,
                text='<',
                text_color=Colors.GRAY.value if not config.rules['classic'] and not config.rules['chess960'] else Colors.WHITE.value,
                font_size=int(config.height*0.1),
                font_name=Fonts.GEIZER,
                command=lambda:self.update_depth(-1) if config.rules['classic'] or config.rules['chess960'] else lambda:None
             ),
            'increase_depth': RectButton(
                x=config.width*0.745,
                y=config.height*0.305+config.height*0.1, 
                width=config.height*0.1,
                height=config.height*0.1,
                color=Colors.DARK_GRAY.value,
                text='>',
                text_color=Colors.GRAY.value if not config.rules['classic'] and not config.rules['chess960'] else Colors.WHITE.value,
                font_size=int(config.height*0.1),
                font_name=Fonts.GEIZER,
                command=lambda:self.update_depth(1) if config.rules['classic'] or config.rules['chess960'] else lambda:None
            ),
            'back': RectButton(
                x=config.width*0.955,
                y=config.height*0.08, 
                width=config.height*0.1,
                height=config.height*0.1,
                color=Colors.LIGHT_GRAY.value,
                hovered_color=Colors.WHITE.value,
                text='<-',
                text_color=Colors.DARK_GRAY.value,
                font_size=int(config.height*0.1),
                font_name=Fonts.GEIZER,
                command=self.manager.go_back
            )
        }

        self.ia_buttons = {
            ia : RadioButton(
                x=config.width*0.51,
                y=config.height*0.305+i*config.height * 0.1,
                radius=config.height*0.03,
                width=int(config.height*0.005),
                color=Colors.GRAY.value if (ia in ['neural_network', 'negamax'] and not config.rules['classic'] and not config.rules['chess960']) else Colors.WHITE.value,
                state=False if ia != 'random_ia' else True
            )
            for i, ia in enumerate(['random_ia', 'negamax', 'neural_network'])
        }
        self.buttons.update(self.ia_buttons)

    def create_labels(self):
        self.labels = {
            'depth': Label(
                center=(config.width*0.63, config.height*0.305+config.height*0.1),
                text = f'depth         {self.depth}',
                font_name=Fonts.GEIZER,
                font_size=int(config.height*0.07),
                color = Colors.GRAY.value if (not config.rules['classic'] and not config.rules['chess960']) else Colors.WHITE.value,
            )
        }
        self.ia_labels = {
            ia : Label(
                center = (config.width*0.35, config.height*0.305+(i*config.height*0.1)),
                text = ia,
                font_name=Fonts.GEIZER,
                font_size=int(config.height*0.08),
                color = Colors.GRAY.value if (ia in ['neural_network', 'negamax']  and not config.rules['classic'] and not config.rules['chess960']) else Colors.WHITE.value,
            )
            for i, ia in enumerate(['random', 'negamax', 'neural_network'])
        }
        self.labels.update(self.ia_labels)

    def update_color(self, color):
        if color != 'random_color':
            self.player1.color = color
            self.player2.color = -color       
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
                    if button.is_clicked() and not (ia in ['neural_network', 'negamax'] and not config.rules['classic'] and not config.rules['chess960']): 
                        self.update_ia(ia, button)

    def update_ia(self, ia, button):
        button.state = True
        self.player2 = str_to_ia(ia, self.player2.color, self.depth)
        for b in self.ia_buttons.values():
            if button is not b :
                b.state = False

    def update_depth(self, n):
        self.depth = (self.depth+n)
        if self.depth > 5 :
            self.depth = 1
        elif self.depth < 1:
            self.depth = 5

        self.labels['depth'].update_text(f'depth         {self.depth}')

    def start_game(self):
        if self.selected_color == 'random_color':
            self.player1.color = random.choice((1, -1))
            self.player2.color = -self.player1.color
        self.manager.go_to(Game(self.player1 if self.player1.color == 1 else self.player2, self.player1 if self.player1.color == -1 else self.player2))

class IaVsIaMenu(Scene):
    def __init__(self):
        self.player1 = RandomAI(1) 
        self.player2 = RandomAI(-1)
        self.frame = pygame.Rect(config.width*0.15, config.height*0.15, config.width*0.7, config.height*0.7)
        self.white_king = load_image('assets/piece/alpha/wK.svg', (config.tile_size, config.tile_size))
        self.white_rect = pygame.Rect(config.width*0.45-config.tile_size//2, config.height*0.17, config.tile_size, config.tile_size)
        self.black_king = load_image('assets/piece/alpha/bK.svg', (config.tile_size, config.tile_size))
        self.black_rect = pygame.Rect(config.width*0.66-config.tile_size//2, config.height*0.17, config.tile_size, config.tile_size)
        self.depth = {1: 1, 2: 1}
        super().__init__()

    def create_buttons(self):
        self.buttons = {
            'back': RectButton(
                x=config.width*0.955,
                y=config.height*0.08, 
                width=config.height*0.1,
                height=config.height*0.1,
                color=Colors.LIGHT_GRAY.value,
                hovered_color=Colors.WHITE.value,
                text='<-',
                text_color=Colors.DARK_GRAY.value,
                font_size=int(config.height*0.),
                font_name=Fonts.GEIZER,
                command=self.manager.go_back
            ),
            'decrease_depth1': RectButton(
                x=config.width*0.56,
                y=config.height*0.355+config.height*0.1, 
                width=config.height*0.07,
                height=config.height*0.07,
                color=Colors.DARK_GRAY.value,
                text='<',
                text_color=Colors.GRAY.value if not config.rules['classic'] and not config.rules['chess960'] else Colors.WHITE.value,
                font_size=int(config.height*0.07),
                font_name=Fonts.GEIZER,
                command=lambda:self.update_depth(-1, 1) if config.rules['classic'] or config.rules['chess960'] else lambda:None
             ),
            'increase_depth1': RectButton(
                x=config.width*0.62,
                y=config.height*0.355+config.height*0.1, 
                width=config.height*0.07,
                height=config.height*0.07,
                color=Colors.DARK_GRAY.value,
                text='>',
                text_color=Colors.GRAY.value if not config.rules['classic'] and not config.rules['chess960'] else Colors.WHITE.value,
                font_size=int(config.height*0.07),
                font_name=Fonts.GEIZER,
                command=lambda:self.update_depth(1, 1) if config.rules['classic'] or config.rules['chess960'] else lambda:None
            ),
            'decrease_depth2': RectButton(
                x=config.width*0.77,
                y=config.height*0.355+config.height*0.1, 
                width=config.height*0.07,
                height=config.height*0.07,
                color=Colors.DARK_GRAY.value,
                text='<',
                text_color=Colors.GRAY.value if not config.rules['classic'] and not config.rules['chess960'] else Colors.WHITE.value,
                font_size=int(config.height*0.07),
                font_name=Fonts.GEIZER,
                command=lambda:self.update_depth(-1, 2) if config.rules['classic'] or config.rules['chess960'] else lambda:None
             ),
            'increase_depth2': RectButton(
                x=config.width*0.83,
                y=config.height*0.355+config.height*0.1, 
                width=config.height*0.07,
                height=config.height*0.07,
                color=Colors.DARK_GRAY.value,
                text='>',
                text_color=Colors.GRAY.value if not config.rules['classic'] and not config.rules['chess960'] else Colors.WHITE.value,
                font_size=int(config.height*0.07),
                font_name=Fonts.GEIZER,
                command=lambda:self.update_depth(1, 2) if config.rules['classic'] or config.rules['chess960'] else lambda:None
            ),
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
                    command=lambda:self.manager.go_to(Game(self.player1, self.player2))
            )
        }    
        self.white_buttons = {
            ia+'1' : RadioButton(
                x=config.width*0.45,
                y=config.height*0.35+i*config.height * 0.1,
                radius=config.height*0.03,
                width=int(config.height*0.005),
                color=Colors.GRAY.value if (ia in ['neural_network', 'negamax']  and not config.rules['classic'] and not config.rules['chess960']) else Colors.WHITE.value,
                state=False if ia != 'random_ia' else True
            )
            for i, ia in enumerate(['random_ia', 'negamax', 'neural_network'])
        }
        self.black_buttons = {
            ia+'2' : RadioButton(
                x=config.width*0.66,
                y=config.height*0.35+i*config.height * 0.1,
                radius=config.height*0.03,
                width=int(config.height*0.005),
                color=Colors.GRAY.value if (ia in ['neural_network', 'negamax'] and not config.rules['classic'] and not config.rules['chess960']) else Colors.WHITE.value,
                state=False if ia != 'random_ia' else True
            )
            for i, ia in enumerate(['random_ia', 'negamax', 'neural_network'])
        }
        self.buttons.update(self.white_buttons)
        self.buttons.update(self.black_buttons)

    def create_labels(self):
        self.labels = {
            'depth1': Label(
                center=(config.width*0.54, config.height*0.355+config.height*0.1),
                text = f'depth      {self.depth[1]}',
                font_name=Fonts.GEIZER,
                font_size=int(config.height*0.05),
                color = Colors.GRAY.value if (not config.rules['classic'] and not config.rules['chess960']) else Colors.WHITE.value,
            ),
            'depth2': Label(
                center=(config.width*0.75, config.height*0.355+config.height*0.1),
                text = f'depth      {self.depth[2]}',
                font_name=Fonts.GEIZER,
                font_size=int(config.height*0.05),
                color = Colors.GRAY.value if (not config.rules['classic'] and not config.rules['chess960']) else Colors.WHITE.value,
            )
        }
        ia_labels = {
            ia : Label(
                center = (config.width*0.29, config.height*0.35+(i*config.height*0.1)),
                text = ia,
                font_name=Fonts.GEIZER,
                font_size=int(config.height*0.08),
                color = Colors.GRAY.value if (ia in ['neural network', 'negamax'] and not config.rules['classic'] and not config.rules['chess960']) else Colors.WHITE.value,
            )
            for i, ia in enumerate(['random', 'negamax', 'neural network'])
        }
        self.labels.update(ia_labels)

    def render(self, screen):
        pygame.draw.rect(screen, Colors.DARK_GRAY.value, self.frame)
        pygame.draw.rect(screen, Colors.WHITE.value, self.white_rect)
        pygame.draw.rect(screen, Colors.BLACK.value, self.black_rect)
        screen.blit(self.white_king, self.white_rect)
        screen.blit(self.black_king, self.black_rect)
        super().render(screen)
    
    def update_depth(self, n, num):
        self.depth[num] = (self.depth[num]+n)
        if self.depth[num]  > 5 :
            self.depth[num] = 1
        elif self.depth[num] < 1:
            self.depth[num] = 5

        self.labels['depth'+str(num)].update_text(f'depth      {self.depth[num]}')
    
    def update_ia(self, num, ia, button, button_dict):
        button.state = True
        if num == 1:
            self.player1 = str_to_ia(ia, 1, self.depth[1])
        else :
            self.player2 = str_to_ia(ia, -1, self.depth[2])
        for b in button_dict.values():
            if button is not b :
                b.state = False

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 :
                for ia, button in self.white_buttons.items():
                    if button.is_clicked() and not (ia in ['neural_network', 'negamax'] and not config.rules['classic'] and not config.rules['chess960']): 
                        self.update_ia(1, ia, button, self.white_buttons)
                for ia, button in self.black_buttons.items():
                    if button.is_clicked() and not (ia in ['neural_network', 'negamax'] and not config.rules['classic'] and not config.rules['chess960']): 
                        self.update_ia(2, ia, button, self.black_buttons)