import pygame
from config import config

class Scene():
    def __init__(self, manager, buttons=[], labels=[]):
        self.manager = manager
        self.buttons = buttons
        self.labels = labels
        
    def render(self, screen:pygame.Surface):
        for button in self.buttons:
            button.draw(screen)
        for label in self.labels:
            label.draw(screen)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()

        for button in self.buttons :
            button.update(mouse_pos)
      
    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            if pygame.mouse.get_pressed()[0]:
                for button in self.buttons :
                    button.handle_click()


class SceneManager:
    def __init__(self, background):
        self.background = background
        self.in_transition = False
        self.is_fading_out = False
        self.transition_overlay = pygame.Surface((config.width, config.height))
        self.transition_overlay.set_alpha(0)
        self.alpha_value = 0
        self.next_action = None
        self.scenes = []
        self.transition_speed = 500
        
    def set(self, scene):
        self.scenes = [scene]

    def go_to(self, scene):
        self.next_action = lambda: self.scenes.append(scene)
        self.start_transition()

    def go_back(self):
        self.next_action = lambda: self.scenes.pop()
        self.start_transition()

    def start_transition(self):
        self.in_transition = True
        self.is_fading_out = True

    def render(self, screen):
        screen.blit(self.background, (0, 0))
        self.scenes[-1].render(screen)
        if self.in_transition:
            screen.blit(self.transition_overlay, (0, 0))

    def update(self, dt):
        if self.in_transition:
            self.alpha_value += dt*self.transition_speed if self.is_fading_out else -dt*self.transition_speed
            self.transition_overlay.set_alpha(self.alpha_value)
            if self.alpha_value >= 255 and self.is_fading_out:
                self.alpha_value = 255
                self.next_action()
                self.is_fading_out = False
            elif self.alpha_value <= 0:
                self.alpha_value = 0
                self.in_transition = False
        else:
            self.scenes[-1].update()

    def handle_event(self, event):
        if not self.in_transition:
            self.scenes[-1].handle_event(event)
