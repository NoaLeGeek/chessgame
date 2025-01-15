from scenes.scene import Scene
from scenes.game import Game
from scenes.settings import SettingsMenu
from gui import RectButton, Label
from config import config

class MainMenu(Scene):
    def __init__(self, manager):
        super().__init__(manager,
                        buttons = [
                            RectButton(config.width*0.5, config.height*0.4, config.width*0.3, config.height*0.15, 'white', 'Play', None, 'black', lambda:manager.go_to(Game(self.manager))),
                            RectButton(config.width*0.5, config.height*0.6, config.width*0.3, config.height*0.15, 'white', 'settings', None, 'black', lambda:manager.go_to(SettingsMenu(self.manager))),
                            RectButton(config.width*0.5, config.height*0.8, config.width*0.3, config.height*0.15, 'white', 'quit', None, 'black', quit)
                        ],
                        labels = [
                            Label((config.width*0.5, config.height*0.17), 'CheckThisOut', None,  200, 'black')
                        ]
                        )
        
    def render(self, screen):
        super().render(screen)
