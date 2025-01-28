import pygame
from scenes.scene import Scene
from config import config
from gui import Label


class SettingsMenu(Scene):
    def __init__(self):
        super().__init__()
        self.volume_bar = VolumeBar()
    
    def render(self, screen):
        screen.fill("black")
        super().render(screen)
        self.volume_bar.draw(screen)

    def update(self):
        super().update()
        self.volume_bar.update()


import pygame

class VolumeBar:
    def __init__(self):
        self.rect = pygame.Rect(config.width * 0.5, config.height * 0.5, config.width * 0.2, config.height * 0.07)
        self.circle_pos = [self.rect.x + self.rect.width * config.volume, self.rect.centery]
        self.circle_radius = self.rect.height * 0.5
        self.line_start = (self.rect.x, self.rect.y + self.rect.height // 2)
        self.line_end = (self.rect.x + self.rect.width, self.rect.y + self.rect.height // 2)


    def draw(self, screen):
        pygame.draw.line(screen, "white", self.line_start, self.line_end, self.rect.height // 4)
        pygame.draw.circle(screen, "white", self.circle_pos, self.circle_radius)

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.circle_pos[0] = mouse_pos[0]
                # Mettre à jour le volume basé sur la position de la souris
                config.volume = (mouse_pos[0] - self.rect.x) / self.rect.width
                print(config.volume)
