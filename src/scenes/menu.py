import webbrowser
from scenes.scene import Scene
from scenes.game import Game
from scenes.settings import SettingsMenu
from gui import RectButton, Label, VideoPlayer, create_rect_surface
from config import config
from constants import Fonts, Colors
from board.player import Player
from scenes.setup import SetupMenu

class MainMenu(Scene):
    def __init__(self):
        super().__init__()
        self.video_player = VideoPlayer("assets/video/chess.mp4", config.width, config.height)
        
    def create_buttons(self):
        button_width = config.width * 0.27
        button_height = config.height * 0.1
        font_size_1 = int(button_height * 0.75)
        font_size_2 = int(button_height * 0.6)

        self.buttons = {
            "play": RectButton(
                x=config.width * 0.5,
                y=config.height * 0.46,
                width=button_width,
                height=button_height,
                border_radius=int(button_height // 2),
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='PLAY',
                font_name=Fonts.GEIZER,
                font_size=font_size_1,
                text_color=Colors.DARK_GRAY.value,
                border_color=Colors.DARK_GRAY.value,
                command=lambda: self.manager.go_to(SetupMenu())
            ),
            "settings": RectButton(
                x=config.width * 0.5,
                y=config.height * 0.66,
                width=button_width,
                height=button_height,
                border_radius=int(button_height // 2),
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='SETTINGS',
                font_name=Fonts.GEIZER,
                font_size=font_size_1,
                text_color=Colors.DARK_GRAY.value,
                command=lambda: self.manager.go_to(SettingsMenu()),
                border_color=Colors.DARK_GRAY.value
            ),
            "quit": RectButton(
                x=config.width * 0.5,
                y=config.height * 0.86,
                width=button_width,
                height=button_height,
                border_radius=int(button_height // 2),
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='QUIT',
                font_name=Fonts.GEIZER,
                font_size=font_size_1,
                text_color=Colors.DARK_GRAY.value,
                command=quit,
                border_color=Colors.DARK_GRAY.value
            ),
            "rules": RectButton(
                x=config.width * 0.1,
                y=config.height * 0.95,
                width=config.width * 0.15,
                height=config.height * 0.06,
                border_radius=int(config.height * 0.06 // 2),
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='RULES',
                font_name=Fonts.GEIZER,
                font_size=font_size_2,
                text_color=Colors.DARK_GRAY.value,
                command=lambda: webbrowser.open(
                    "https://lechiquiers.com/blogs/news/comment-jouer-aux-echecs-pour-les-debutants-installation-coups-et-regles-de-base-expliques"
                ),
                border_color=Colors.DARK_GRAY.value
            ),
            "credits": RectButton(
                x=config.width * 0.9,
                y=config.height * 0.95,
                width=config.width * 0.15,
                height=config.height * 0.06,
                border_radius=int(config.height * 0.06 // 2),
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='CREDITS',
                font_name=Fonts.GEIZER,
                font_size=font_size_2,
                text_color=Colors.DARK_GRAY.value,
                command=lambda: self.manager.go_to(CreditsMenu()),
                border_color=Colors.DARK_GRAY.value
            )
        }

    def create_labels(self):
        title_background =  create_rect_surface(Colors.WHITE.value, config.width*0.6, config.height*0.22, border_radius=int(config.height*0.055), border_width = int(config.height*0.01), border_color = Colors.DARK_GRAY.value)
        self.labels = {
            "title": Label((config.width*0.5, config.height*0.185), 'CheckThisOut', Fonts.ONE_SLICE,  int(config.height*0.2), Colors.DARK_GRAY.value, title_background, (config.width*0.5, config.height*0.17))
        }
        
    def render(self, screen):
        self.video_player.play(screen)
        super().render(screen)


class CreditsMenu(Scene):
    def __init__(self):
        super().__init__()

    def create_labels(self):
        self.labels = {
            "kasparov": Label((config.width*0.5, config.height*0.5), "ISSA HAKIM", Fonts.GEIZER, int(config.height*0.25), Colors.WHITE.value)
        }

    def render(self, screen):
        super().render(screen)
    
    def handle_event(self, event):
        super().handle_event(event)