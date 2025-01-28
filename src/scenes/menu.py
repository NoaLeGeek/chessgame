from scenes.scene import Scene
from scenes.game import Game
from scenes.settings import SettingsMenu
from gui import RectButton, Label, VideoPlayer
from config import config

class MainMenu(Scene):
    def __init__(self, manager):
        super().__init__(manager,
                        buttons = [
                            RectButton(config.width*0.5, config.height*0.4, config.width*0.27, config.height*0.1, 'white', 'PLAY', 'LilitaOne', 'black', lambda:manager.go_to(Game(self.manager))),
                            RectButton(config.width*0.5, config.height*0.6, config.width*0.27, config.height*0.1, 'white', 'SETTINGS', 'LilitaOne', 'black', lambda:manager.go_to(SettingsMenu(self.manager))),
                            RectButton(config.width*0.5, config.height*0.8, config.width*0.27, config.height*0.1, 'white', 'QUIT', 'LilitaOne', 'black', quit),
                            RectButton(config.width*0.9, config.height*0.95, config.width*0.15, config.height*0.06, 'white', 'CREDITS', 'LilitaOne', 'black', None)
                        ],
                        labels = [
                            Label((config.width*0.5, config.height*0.17), 'CheckThisOut', "Pacifico",  config.height//5, 'black')
                        ]
                        )
        self.video_player = VideoPlayer("assets/video/chess.mp4", config.width, config.height)
        
    def render(self, screen):
        self.video_player.play(screen)
        super().render(screen)
