import webbrowser
from scenes.scene import Scene
from scenes.game import Game
from scenes.settings import SettingsMenu
from gui import RectButton, Label, VideoPlayer, create_rect_surface
from config import config
from constants import Fonts, Colors
from board.player import Player

class MainMenu(Scene):
    def __init__(self):
        super().__init__()
        self.video_player = VideoPlayer("assets/video/chess.mp4", config.width, config.height)
        
    def create_buttons(self):
        button_width = config.width * 0.27
        button_height = config.height * 0.1
        font_size = int(button_height * 0.5)

        self.buttons = {
            "play": RectButton(
                x=config.width * 0.5,
                y=config.height * 0.45,
                width=button_width,
                height=button_height,
                border_radius=int(button_height // 2),
                color=Colors.WHITE,
                text='PLAY',
                font_name=Fonts.GEIZER,
                font_size=font_size,
                text_color=Colors.BLACK,
                border_color=Colors.BLACK,
                command=lambda: self.manager.go_to(SetupMenu())
            ),
            "settings": RectButton(
                x=config.width * 0.5,
                y=config.height * 0.65,
                width=button_width,
                height=button_height,
                border_radius=int(button_height // 2),
                color=Colors.WHITE,
                text='SETTINGS',
                font_name=Fonts.GEIZER,
                font_size=font_size,
                text_color=Colors.BLACK,
                command=lambda: self.manager.go_to(SettingsMenu()),
                border_color=Colors.BLACK
            ),
            "quit": RectButton(
                x=config.width * 0.5,
                y=config.height * 0.85,
                width=button_width,
                height=button_height,
                border_radius=int(button_height // 2),
                color=Colors.WHITE,
                text='QUIT',
                font_name=Fonts.GEIZER,
                font_size=font_size,
                text_color=Colors.BLACK,
                command=quit,
                border_color=Colors.BLACK
            ),
            "rules": RectButton(
                x=config.width * 0.1,
                y=config.height * 0.95,
                width=config.width * 0.15,
                height=config.height * 0.06,
                border_radius=int(config.height * 0.06 // 2),
                color=Colors.WHITE,
                text='RULES',
                font_name=Fonts.GEIZER,
                font_size=font_size,
                text_color=Colors.BLACK,
                command=lambda: webbrowser.open(
                    "https://lechiquiers.com/blogs/news/comment-jouer-aux-echecs-pour-les-debutants-installation-coups-et-regles-de-base-expliques"
                ),
                border_color=Colors.BLACK
            ),
            "credits": RectButton(
                x=config.width * 0.9,
                y=config.height * 0.95,
                width=config.width * 0.15,
                height=config.height * 0.06,
                border_radius=int(config.height * 0.06 // 2),
                color=Colors.WHITE,
                text='CREDITS',
                font_name=Fonts.GEIZER,
                font_size=font_size,
                text_color=Colors.BLACK,
                command=lambda: self.manager.go_to(CreditsMenu()),
                border_color=Colors.BLACK
            )
        }

    def create_labels(self):
        title_background =  create_rect_surface(Colors.WHITE, config.width*0.6, config.height*0.22, border_radius=int(config.height*0.055), border_width = int(config.height*0.01), border_color = Colors.BLACK)
        self.labels = {
            "title": Label((config.width*0.5, config.height*0.185), 'CheckThisOut', Fonts.ONE_SLICE,  int(config.height*0.2), Colors.BLACK, title_background, (config.width*0.5, config.height*0.17))
        }
        

    def render(self, screen):
        self.video_player.play(screen)
        super().render(screen)


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
            "play": RectButton(
                x=config.width*0.5, 
                y=config.height*0.4, 
                width=button_width, 
                height=button_height, 
                border_radius=int(button_height//2), 
                color=Colors.WHITE, 
                text='PLAY',
                font_name=Fonts.GEIZER, 
                font_size=font_size, 
                text_color=Colors.BLACK, 
                command=lambda:self.manager.go_to(Game(self.player1, self.player2))
            ),
            "bot": RectButton(
                x=config.width*0.5, 
                y=config.height*0.6, 
                width=button_width, 
                height=button_height, 
                border_radius=int(button_height//2), 
                color=Colors.WHITE, 
                text='PLAY AGAINT A BOT', 
                font_name=Fonts.GEIZER, 
                font_size=font_size, 
                text_color=Colors.BLACK, 
                command=lambda:self.manager.go_to(Game(self.player1, self.player2))
            )
        }

    def render(self, screen):
        super().render(screen)
    
    def handle_event(self, event):
        super().handle_event(event)

class CreditsMenu(Scene):
    def __init__(self):
        super().__init__()

    def create_labels(self):
        self.labels = {
            "kasparov": Label((config.width*0.5, config.height*0.5), "ISSA HAKIM", Fonts.GEIZER, int(config.height*0.25), Colors.WHITE)
        }

    def render(self, screen):
        super().render(screen)
    
    def handle_event(self, event):
        super().handle_event(event)