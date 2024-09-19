import pygame
from Scenes.scene import Scene
from Scenes.game import Game
from Scenes.settings import SettingsMenu
from gui import RectButton

class MainMenu(Scene):
    def __init__(self, manager, config):
        super().__init__(manager, config,
                        buttons = [
                            RectButton(config.width*0.5, config.height*0.25, config.width*0.5, config.height*0.15, 'white', 'play', None, 'black', lambda:manager.go_to(Game(self.manager, self.config))),
                            RectButton(config.width*0.5, config.height*0.5, config.width*0.5, config.height*0.15, 'white', 'settings', None, 'black', lambda:manager.go_to(SettingsMenu(self.manager, self.config))),
                            RectButton(config.width*0.5, config.height*0.75, config.width*0.5, config.height*0.15, 'white', 'quit', None, 'black', quit)
                        ])
        
    def render(self, screen):
        super().render(screen)
