import pygame

from src.config import config
from src.utils import singleton

class Scene:
    """
    Base class for a scene in the game.
    Manages buttons, labels, and rendering.
    """
    def __init__(self):
        """
        Initializes the scene and its manager.
        """
        self.manager = SceneManager()
        self.create_labels()
        self.create_buttons()
        
    def create_buttons(self):
        """
        Initializes the dictionary to store buttons.
        """
        self.buttons = {}

    def create_labels(self):
        """
        Initializes the dictionary to store labels.
        """
        self.labels = {}
        
    def render(self, screen: pygame.Surface):
        """
        Renders all buttons and labels on the screen.
        
        Args:
            screen (pygame.Surface): The surface to render elements on.
        """
        for button in self.buttons.values():
            button.draw(screen)
        for label in self.labels.values():
            label.draw(screen)

    def update(self):
        """
        Updates all buttons based on the mouse position.
        """
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons.values():
            button.update(mouse_pos)
      
    def handle_event(self, event: pygame.event.Event):
        """
        Handles input events, such as mouse clicks.
        
        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                for button in self.buttons.values():
                    button.handle_click()

@singleton
class SceneManager:
    """
    Manages scene transitions and rendering in the game.
    """
    def __init__(self):
        """
        Initializes the scene manager with transition settings.
        """
        self.in_transition = False
        self.is_fading_out = False
        self.transition_overlay = pygame.Surface((config.width, config.height))
        self.transition_overlay.set_alpha(0)
        self.alpha_value = 0
        self.next_action = None
        self.scenes = []
        self.transition_speed = 500
        
    def set(self, scene):
        """
        Sets the current scene.
        
        Args:
            scene (Scene): The scene to set as active.
        """
        self.scenes = [scene]

    def go_to(self, scene):
        """
        Transitions to a new scene.
        
        Args:
            scene (Scene): The scene to transition to.
        """
        self.next_action = lambda: self.scenes.append(scene)
        self.start_transition()

    def go_back(self):
        """
        Transitions back to the previous scene.
        """
        self.next_action = lambda: self.scenes.pop()
        self.start_transition()

    def start_transition(self):
        """
        Initiates the transition effect.
        """
        self.in_transition = True
        self.is_fading_out = True

    def render(self, screen: pygame.Surface):
        """
        Renders the current scene and transition overlay if active.
        
        Args:
            screen (pygame.Surface): The surface to render on.
        """
        self.scenes[-1].render(screen)
        if self.in_transition:
            screen.blit(self.transition_overlay, (0, 0))

    def update(self, dt: float):
        """
        Updates the scene transition effects.
        
        Args:
            dt (float): Delta time to control transition speed.
        """
        if self.in_transition:
            self.alpha_value += dt * self.transition_speed if self.is_fading_out else -dt * self.transition_speed
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

    def handle_event(self, event: pygame.event.Event):
        """
        Handles events for the current scene if no transition is active.
        
        Args:
            event (pygame.event.Event): The event to handle.
        """
        if not self.in_transition:
            self.scenes[-1].handle_event(event)
