import pygame
from config import config

class Scene():
    def __init__(self, manager, buttons=[], labels=[]):
        self.manager = manager
        self.buttons = buttons
        self.labels = labels
        self.enter()
        self.in_exit = False
        self.in_enter = False
        
        
    def render(self, screen:pygame.Surface):
        for button in self.buttons:
            button.draw(screen)
        for label in self.labels:
            label.draw(screen)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.in_enter :
            self.alpha += 3
            self.in_enter = self.alpha < 255

        for button in self.buttons :
            button.update(mouse_pos)
            if self.in_enter or self.in_exit :
                button.set_alpha(self.alpha)

                
        for label in self.labels :
            if self.in_enter or self.in_exit :
                label.set_alpha(self.alpha)
        
    
    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            if pygame.mouse.get_pressed()[0]:
                for button in self.buttons :
                    button.handle_click()

    def enter(self):
        if not self.in_enter :
            self.in_enter = True
            self.alpha = 0
            for button in self.buttons :
                button.set_alpha(0)
   
    def exit(self):
        self.in_exit = False

    

class SceneManager:
    def __init__(self, background):
        self.background = background

    def set(self, scene:Scene):
        self.scenes = [scene]
    
    def go_to(self, scene:Scene):
        self.scenes.append(scene)
        self.scenes[-1].enter()
    
    def go_back(self):
        self.scenes.pop()
        self.scenes[-1].enter()
        
    def render(self, screen:pygame.Surface):
        screen.blit(self.background, (0, 0))
        self.scenes[-1].render(screen)
    
    def update(self):
        self.scenes[-1].update()
    
    def handle_event(self, event:pygame.event.Event):
        self.scenes[-1].handle_event(event)
