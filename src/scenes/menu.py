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
        self.buttons = {
            "play": RectButton(config.width*0.5, config.height*0.45, config.width*0.27, config.height*0.1, int(config.height*0.1//2), Colors.WHITE, 'PLAY', Fonts.GEIZER, Colors.BLACK, lambda:self.manager.go_to(SetupMenu()), border_color=Colors.BLACK),
            "settings": RectButton(config.width*0.5, config.height*0.65, config.width*0.27, config.height*0.1, int(config.height*0.1//2), Colors.WHITE, 'SETTINGS', Fonts.GEIZER, Colors.BLACK, lambda:self.manager.go_to(SettingsMenu()), border_color=Colors.BLACK),
            "quit": RectButton(config.width*0.5, config.height*0.85, config.width*0.27, config.height*0.1, int(config.height*0.1//2), Colors.WHITE, 'QUIT', Fonts.GEIZER, Colors.BLACK, quit, border_color=Colors.BLACK),
            "rules": RectButton(config.width*0.1, config.height*0.95, config.width*0.15, config.height*0.06, int(config.height*0.06//2), Colors.WHITE, 'RULES', Fonts.GEIZER, Colors.BLACK, lambda:webbrowser.open("https://lechiquiers.com/blogs/news/comment-jouer-aux-echecs-pour-les-debutants-installation-coups-et-regles-de-base-expliques"), border_color=Colors.BLACK),
            "credits": RectButton(config.width*0.9, config.height*0.95, config.width*0.15, config.height*0.06, int(config.height*0.06//2), Colors.WHITE, 'CREDITS', Fonts.GEIZER, Colors.BLACK, lambda:self.manager.go_to(CreditsMenu()), border_color=Colors.BLACK)
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
        self.buttons = {
            "play": RectButton(config.width*0.5, config.height*0.45, config.width*0.27, config.height*0.1, int(config.height*0.1//2), Colors.WHITE, 'PLAY', Fonts.GEIZER, Colors.BLACK, lambda:self.manager.go_to(Game(self.player1, self.player2))),
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