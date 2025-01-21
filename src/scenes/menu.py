from scenes.scene import Scene
from scenes.game import Game
from scenes.settings import SettingsMenu
from gui import RectButton
from config import config

class MainMenu(Scene):
    def __init__(self, manager):
        super().__init__(manager,
                        buttons = [
                            RectButton(config.width*0.5, config.height*0.25, config.width*0.5, config.height*0.15, 'white', 'Play', None, 'black', lambda:manager.go_to(Game(self.manager))),
                            RectButton(config.width*0.5, config.height*0.5, config.width*0.5, config.height*0.15, 'white', 'settings', None, 'black', lambda:manager.go_to(SettingsMenu(self.manager))),
                            RectButton(config.width*0.5, config.height*0.75, config.width*0.5, config.height*0.15, 'white', 'quit', None, 'black', quit)
                        ])
        
    def render(self, screen):
        super().render(screen)
