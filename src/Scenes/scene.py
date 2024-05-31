import pygame
from config import Config

class Scene:
    def __init__(self, manager, config:Config):
        self.manager = manager
        self.config = config
        
    def render(self, screen:pygame.Surface):
        raise NotImplementedError
    
    def update(self):
        raise NotImplementedError
    
    def handle_event(self, event:pygame.event.Event):
        raise NotImplementedError
    

class SceneManager:
    def set(self, scene:Scene):
        self.scenes = [scene]
    
    def go_to(self, scene:Scene):
        self.scenes.append(scene)
    
    def go_back(self):
        self.scenes.pop()
        
    def render(self, screen:pygame.Surface):
        self.scenes[-1].render(screen)
    
    def update(self):
        self.scenes[-1].update()
    
    def handle_event(self, event:pygame.event.Event):
        self.scenes[-1].handle_event(event)


