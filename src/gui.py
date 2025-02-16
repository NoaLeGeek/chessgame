import pygame
import cv2

from constants import Colors

def create_rect_surface(color: Colors, width: int, height: int, border_radius: int, alpha: int = 255) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, color.value, (0, 0, width, height), border_radius=border_radius)
        if alpha is not None:
            surface.set_alpha(alpha)
        return surface

class RectButton:
    def __init__(self, x: int, y: int, width: int, height: int, border_radius: int, color: Colors, text: str, font_name: str, text_color: Colors, command, image: pygame.Surface = None):
        self.width, self.height = width, height
        self.x, self.y = x - width // 2, y - height // 2
        self.rect = pygame.Rect(self.x, self.y, width, height)
        self.color = color
        self.border_radius = border_radius
        self.surface = create_rect_surface(color, width, height, border_radius)
        self.filter = create_rect_surface(Colors.BLACK, width, height, border_radius, alpha=50)
        self.label = Label(self.rect.center, text, font_name, self.rect.height, text_color)
        self.command = command
        self.is_hovered = False
        self.image = image
        if image: 
            self.image_pos = (self.rect.centerx-image.get_width()//2, self.rect.centery-image.get_height()//2)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.surface, (self.x, self.y))
        self.label.draw(screen)
        if self.image:
            screen.blit(self.image, self.image_pos)
        if not self.is_hovered:
            screen.blit(self.filter, (self.x, self.y))

    def update(self, mouse_pos: tuple[int, int]):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_click(self):
        if self.is_clicked():
            self.command()
    
    def is_clicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def update_text(self, new_text: str):
        self.label.update_text(new_text)

    def update_color(self, color: str):
        self.color = color 
        self.surface = create_rect_surface(color, self.width, self.height, self.border_radius)
    



class Label:
    def __init__(self, center: tuple[int, int], text: str, font_name: str, font_size: int, color: Colors, background: pygame.Surface = None, background_pos = None):
        self.text = text
        self.center = center
        self.font_path = f"assets/font/{font_name}"
        self.font = pygame.font.Font(self.font_path, font_size)
        self.color = color
        self.surface = self._create_surface()
        self.rect = self.surface.get_rect(center=center)
        self.background = background
        if background_pos: 
            self.background_pos = (background_pos[0]-background.get_width()//2, background_pos[1]-background.get_height()//2)

    def draw(self, screen: pygame.Surface):
        if self.background:
            screen.blit(self.background, self.background_pos)
        screen.blit(self.surface, self.rect)

    def update_text(self, new_text: str):
        self.text = new_text
        self.surface = self._create_surface()
        self.rect = self.surface.get_rect(center=self.center)

    def _create_surface(self) -> pygame.Surface:
        return self.font.render(self.text, True, self.color.value)

class VideoPlayer:
    def __init__(self, video_path, width, height):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        _, frame = self.cap.read()
        self.frame_width = width
        self.frame_height = int(width*(frame.shape[0]/frame.shape[1]))

    def play(self, screen):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            self.cap = cv2.VideoCapture(self.video_path)
            ret, frame = self.cap.read()
            
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

        screen.blit(frame, (0, 0))

