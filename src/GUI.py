import pygame

class RectButton:
    def __init__(self, x:int, y:int, width:int, height:int, color:str, text:str, font:str, text_color:str, command):
        self.rect = pygame.Rect(x-width//2, y-height//2, width, height)
        self.label = Label(self.rect.center, text, pygame.font.Font(font, self.rect.height), text_color)
        self.color = color
        self.command = command

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        self.label.draw(screen)

    def update(self, new_text):
        self.label.update_text(new_text)

    def handle_click(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.command()


class ImageButton:
    def __init__(self, center:tuple[int, int], image:pygame.Surface, command):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.command = command

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def handle_click(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.command()


class Label:
    def __init__(self, center:tuple[int, int,], text:str, font:pygame.font.Font, color:str):
        self.text = text
        self.center = center 
        self.font = font 
        self.color = color
        self.surface = font.render(text, True, color)
        self.rect = self.surface.get_rect(center=center)

    def draw(self,  screen:pygame.Surface):
        screen.blit(self.surface, self.rect)

    def update_text(self, new_text):
        self.surface = self.font.render(new_text, True, self.color)
        self.rect = self.surface.get_rect(center = self.center)
