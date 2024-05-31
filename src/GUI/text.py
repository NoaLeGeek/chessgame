import pygame

def draw_text(screen:pygame.Surface, text:str, font:pygame.font.Font, color:str, topleft:tuple[int, int]=None, center:tuple[int, int]=None):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if topleft :
        text_rect.topleft = topleft
    else :
        text_rect.center = center
    screen.blit(text_surface, text_rect)


class Label:
    def __init__(self, center:tuple[int, int,], text:str, font:pygame.font.Font, color:str):
        self.text = text
        self.center = center 
        self.font = font 
        self.color = color

    def draw(self, screen):
        draw_text(screen, self.text, self.font, self.color, center = self.center)