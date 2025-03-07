from scenes.scene import Scene
from scenes.game import Game
from gui import RectButton, Label, VideoPlayer, create_rect_surface
from config import config
from constants import Fonts, Colors
from board.player import Player
from utils import load_image

class SetupMenu(Scene):
    def __init__(self):
        super().__init__()
        self.player1 = Player(1)
        self.player2 = Player(-1)
    
    def create_buttons(self):
        button_width = config.width * 0.27
        button_height = config.height * 0.1
        font_size = int(button_height * 0.5)

        self.buttons = {
            "player vs player": RectButton(
                x=config.width*0.5, 
                y=config.height*0.3, 
                width=button_width, 
                height=button_height, 
                border_radius=int(button_height//2), 
                color=Colors.WHITE, 
                text='PLAYER VS PLAYER',
                font_name=Fonts.GEIZER, 
                font_size=font_size, 
                text_color=Colors.BLACK, 
                command=lambda:self.manager.go_to(Game(self.player1, self.player2))
            ),
            "player vs ia": RectButton(
                x=config.width*0.5, 
                y=config.height*0.5, 
                width=button_width, 
                height=button_height, 
                border_radius=int(button_height//2), 
                color=Colors.WHITE, 
                text='PLAYER VS IA', 
                font_name=Fonts.GEIZER, 
                font_size=font_size, 
                text_color=Colors.BLACK, 
                command=lambda:self.manager.go_to(PlayerVsIaMenu(self.player1, self.player2))
            ),
            "ia vs ia": RectButton(
                x=config.width*0.5, 
                y=config.height*0.7, 
                width=button_width, 
                height=button_height, 
                border_radius=int(button_height//2), 
                color=Colors.WHITE, 
                text='IA VS IA', 
                font_name=Fonts.GEIZER, 
                font_size=font_size, 
                text_color=Colors.BLACK, 
                command=lambda:self.manager.go_to(Game(self.player1, self.player2))
            )
        }

        rule_buttons = {
            rule: RectButton(
                x=config.width*0.18,
                y=config.height*0.355+i*button_height,
                width=button_width,
                height=button_height,
                border_radius=0,
                color=Colors.WHITE, 
                text=rule, 
                font_name=Fonts.GEIZER, 
                font_size=font_size, 
                text_color=Colors.BLACK, 
                command=lambda:None
            ) for i, rule in enumerate(['chess960', 'giveaway', '3+ checks', 'king of the hill'])
        }

        self.buttons.update(rule_buttons)

    def render(self, screen):
        super().render(screen)
    
    def handle_event(self, event):
        super().handle_event(event)

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
                color=Colors.WHITE, 
                text='', 
                font_name=Fonts.GEIZER, 
                font_size=0, 
                text_color=Colors.BLACK, 
                image = load_image('assets/piece/alpha/wK.svg', (config.tile_size, config.tile_size)),
                command=lambda:None
            ),
            'black':RectButton(
                x=config.width*0.5,
                y = config.height*0.7,
                width=config.tile_size,
                height=config.tile_size,
                border_radius=1,
                color=Colors.WHITE, 
                text='', 
                font_name=Fonts.GEIZER, 
                font_size=0, 
                text_color=Colors.BLACK, 
                image = load_image('assets/piece/alpha/bK.svg', (config.tile_size, config.tile_size)),
                command=lambda:None
            )
        }
