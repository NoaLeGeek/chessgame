import pygame
from scene import Scene
from game import Game
from GUI.button import RectButton


class Menu(Scene):
    def __init__(self, manager, config, buttons=[], labels=[]):
        super().__init__(manager, config)
        self.buttons = buttons
        self.labels = labels
    
    def render(self, screen):
        for button in self.buttons :
            button.draw(screen)
        for label in self.labels :
            label.draw(screen)
    
    def update(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            if pygame.mouse.get_pressed()[0]:
                for button in self.buttons :
                    button.handle_click()


    
class MainMenu(Menu):
    def __init__(self, manager, config):
        super().__init__(manager, config,
                        buttons = [
                            RectButton(config.width*0.5, config.height*0.25, config.width*0.5, config.height*0.15, 'white', 'play', None, 'black', lambda:manager.go_to(Game(self.manager, self.config))),
                            RectButton(config.width*0.5, config.height*0.5, config.width*0.5, config.height*0.15, 'white', 'settings', None, 'black', lambda:manager.go_to(SettingsMenu(self.manager, self.config))),
                            RectButton(config.width*0.5, config.height*0.75, config.width*0.5, config.height*0.15, 'white', 'quit', None, 'black', quit)
                        ])