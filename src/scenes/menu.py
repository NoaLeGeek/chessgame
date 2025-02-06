import webbrowser
from scenes.scene import Scene
from scenes.game import Game
from scenes.settings import SettingsMenu
from gui import RectButton, Label, VideoPlayer, create_rect_surface
from config import config
from constants import Fonts
from board.player import Player

class MainMenu(Scene):
    def __init__(self):
        super().__init__()
        self.video_player = VideoPlayer("assets/video/chess.mp4", config.width, config.height)
        
    def create_buttons(self):
        self.buttons = {
            "play": RectButton(config.width*0.5, config.height*0.45, config.width*0.27, config.height*0.1, int(config.height*0.1//2), 'white', 'PLAY', Fonts.GEIZER, 'black', lambda:self.manager.go_to(SetupMenu())),
            "settings": RectButton(config.width*0.5, config.height*0.65, config.width*0.27, config.height*0.1, int(config.height*0.1//2), 'white', 'SETTINGS', Fonts.GEIZER, 'black', lambda:self.manager.go_to(SettingsMenu())),
            "quit": RectButton(config.width*0.5, config.height*0.85, config.width*0.27, config.height*0.1, int(config.height*0.1//2), 'white', 'QUIT', Fonts.GEIZER, 'black', quit),
            "rules": RectButton(config.width*0.1, config.height*0.95, config.width*0.15, config.height*0.06, int(config.height*0.06//2), 'white', 'RULES', Fonts.GEIZER, 'black', lambda:webbrowser.open("https://lechiquiers.com/blogs/news/comment-jouer-aux-echecs-pour-les-debutants-installation-coups-et-regles-de-base-expliques")),
            "credits": RectButton(config.width*0.9, config.height*0.95, config.width*0.15, config.height*0.06, int(config.height*0.06//2), 'white', 'CREDITS', Fonts.GEIZER, 'black', lambda:self.manager.go_to(CreditsMenu()))
        }
    
    def create_labels(self):
        self.labels = {
            "title": Label((config.width*0.5, config.height*0.185), 'CheckThisOut', Fonts.ONE_SLICE,  int(config.height*0.2), 'black', create_rect_surface("white", config.width*0.6, config.height*0.22, border_radius=int(config.height*0.055)), (config.width*0.5, config.height*0.17))
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
        self.buttons = {
            "play": RectButton(config.width*0.5, config.height*0.45, config.width*0.27, config.height*0.1, int(config.height*0.1//2), 'white', 'PLAY', Fonts.GEIZER, 'black', lambda:self.manager.go_to(Game(self.player1, self.player2))),
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
            "kasparov": Label((config.width*0.5, config.height*0.5), "ISSA HAKIM", Fonts.GEIZER, int(config.height*0.25), "white")
        }

    def render(self, screen):
        super().render(screen)
    
    def handle_event(self, event):
        super().handle_event(event)