import pygame

class RectButton:
    def __init__(self, x:int, y:int, width:int, height:int, color:str, text:str, font:str, text_color:str, command):
        self.width, self.height = width, height
        self.x, self.y = x-width//2, y-height//2
        self.rect = pygame.Rect(self.x, self.y, width, height)
        self.surface = pygame.Surface((width, height))
        self.surface.fill(color)
        self.label = Label(self.rect.center, text, pygame.font.Font(font, self.rect.height), text_color, font)
        self.color = color
        self.command = command
        self.set_alpha(0)

    def draw(self, screen):
        screen.blit(self.surface, (self.x, self.y))
        self.label.draw(screen)

    def update(self, mouse_pos):
        is_collision = self.rect.collidepoint(mouse_pos)
        if is_collision and self.rect.width < self.width + 10 :
            self.update_size(self.rect.width+2, self.rect.height+2, self.rect.x-1, self.rect.y-1)    
        elif not is_collision and self.rect.width > self.width :
            self.update_size(self.rect.width-2, self.rect.height-2, self.rect.x+1, self.rect.y+1)

    def set_alpha(self, alpha):
        self.surface.set_alpha(alpha)
        self.label.surface.set_alpha(alpha)     
    
    def update_size(self, new_width, new_height, new_x, new_y):
        self.rect.width, self.rect.height = new_width, new_height
        self.rect.x, self.rect.y = new_x, new_y
        self.x, self.y = new_x, new_y
        self.surface = pygame.Surface((new_width, new_height))
        self.surface.fill(self.color)
        self.label.update_size(self.rect.height, self.rect.center)

    def update_text(self, new_text):
        self.label.update_text(new_text)

    def handle_click(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.command()
    
    def reset(self):
        self.alpha = 0
        self.surface.set_alpha(0)
        self.label.surface.set_alpha(0)


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
    def __init__(self, center:tuple[int, int,], text:str, font:pygame.font.Font, color:str, font_name:str):
        self.text = text
        self.center = center 
        self.font = font 
        self.color = color
        self.font_name = font_name
        self.surface = font.render(text, True, color)
        self.rect = self.surface.get_rect(center=center)
        self.surface.set_alpha(0)
        

    def draw(self,  screen:pygame.Surface):
        screen.blit(self.surface, self.rect)

    def update_text(self, new_text):
        self.surface = self.font.render(new_text, True, self.color) 
        self.rect = self.surface.get_rect(center = self.center)
        self.text = new_text
    
    def update_size(self, size, new_center):
        self.surface = pygame.font.Font(self.font_name, size).render(self.text, True, self.color) 
        self.rect = self.surface.get_rect(center = new_center)
        self.center = new_center

