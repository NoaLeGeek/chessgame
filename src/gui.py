import pygame

class RectButton:
    def __init__(self, x:int, y:int, width:int, height:int, color:str, text:str, font_name:str, text_color:str, command):
        self.width, self.height = width, height
        self.x, self.y = x-width//2, y-height//2
        self.rect = pygame.Rect(self.x, self.y, width, height)
        self.surface = pygame.Surface((width, height))
        self.surface.fill(color)
        self.label = Label(self.rect.center, text, font_name, self.rect.height, text_color)
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
        self.label.set_alpha(alpha)     
    
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
    def __init__(self, center:tuple[int, int,], text:str, font_name:str, font_size:str, color:str):
        self.text = text
        self.center = center 
        self.font = pygame.font.Font(font_name, font_size)
        self.color = color
        self.font_name = font_name
        self.surface = self.font.render(text, True, color)
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
        
    def set_alpha(self, alpha):
        self.surface.set_alpha(alpha) 


class VideoPlayer:
    def __init__(self, video_path, width, height):
        self.video_path = video_path
        self.screen_width = width
        self.screen_height = height
        self.cap = cv2.VideoCapture(video_path)

    def play(self, screen):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            self.cap = cv2.VideoCapture(self.video_path)
            ret, frame = self.cap.read()

        frame_height, frame_width = frame.shape[:2]
        aspect_ratio = frame_height / frame_width
        new_width = self.screen_width
        new_height = int(new_width * aspect_ratio)

        frame = cv2.resize(frame, (new_width, new_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

        x = (self.screen_width - new_width) // 2
        y = (self.screen_height - new_height) // 2

        screen.blit(frame, (x, y))
        pygame.display.flip()



