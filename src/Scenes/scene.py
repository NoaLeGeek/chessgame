import pygame
from config import Config

class Scene():
    def __init__(self, manager, config:Config, buttons=[], labels=[]):
        self.manager = manager
        self.config = config
        self.buttons = buttons
        self.labels = labels
        
    def render(self, screen:pygame.Surface):
        for button in self.buttons:
            button.draw(screen)
        for label in self.labels:
            label.draw(screen)

    def update(self):
        pass
    
    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            if pygame.mouse.get_pressed()[0]:
                for button in self.buttons :
                    button.handle_click()
    

class SceneManager:
    def __init__(self, background):
        self.background = background

    def set(self, scene:Scene):
        self.scenes = [scene]
    
    def go_to(self, scene:Scene):
        self.scenes.append(scene)
    
    def go_back(self):
        self.scenes.pop()
        
    def render(self, screen:pygame.Surface):
        screen.blit(self.background, (0, 0))
        self.scenes[-1].render(screen)
    
    def update(self):
        self.scenes[-1].update()
    
    def handle_event(self, event:pygame.event.Event):
        self.scenes[-1].handle_event(event)