import webbrowser
from scenes.scene import Scene
from scenes.game import Game
from scenes.settings import SettingsMenu
from gui import RectButton, Label, VideoPlayer, create_rect_surface
from config import config

class MainMenu(Scene):
    def __init__(self):
        super().__init__()
        self.video_player = VideoPlayer("assets/video/chess.mp4", config.width, config.height)
        
    def create_buttons(self):
        self.buttons = {
            "play": RectButton(config.width*0.5, config.height*0.45, config.width*0.27, config.height*0.1, int(config.height*0.1//2), 'white', 'PLAY', 'Geizer.otf', 'black', lambda:self.manager.go_to(Game())),
            "settings": RectButton(config.width*0.5, config.height*0.65, config.width*0.27, config.height*0.1, int(config.height*0.1//2), 'white', 'SETTINGS', 'Geizer.otf', 'black', lambda:self.manager.go_to(SettingsMenu())),
            "quit": RectButton(config.width*0.5, config.height*0.85, config.width*0.27, config.height*0.1, int(config.height*0.1//2), 'white', 'QUIT', 'Geizer.otf', 'black', quit),
            "rules": RectButton(config.width*0.1, config.height*0.95, config.width*0.15, config.height*0.06, int(config.height*0.06//2), 'white', 'RULES', 'Geizer.otf', 'black', lambda:webbrowser.open("https://lechiquiers.com/blogs/news/comment-jouer-aux-echecs-pour-les-debutants-installation-coups-et-regles-de-base-expliques")),
            "credits": RectButton(config.width*0.9, config.height*0.95, config.width*0.15, config.height*0.06, int(config.height*0.06//2), 'white', 'CREDITS', 'Geizer.otf', 'black', None)
        }
    
    def create_labels(self):
        self.labels = {
            "title": Label((config.width*0.5, config.height*0.185), 'CheckThisOut', "One Slice.otf",  int(config.height*0.2), 'black', create_rect_surface("white", config.width*0.6, config.height*0.22, border_radius=int(config.height*0.055)), (config.width*0.5, config.height*0.17))
        }

    def render(self, screen):
        self.video_player.play(screen)
        super().render(screen)



