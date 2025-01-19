import pygame
import cv2

class RectButton:
    def __init__(self, x: int, y: int, width: int, height: int, color: str, text: str, font_name: str, text_color: str, command):
        self.width, self.height = width, height
        self.x, self.y = x - width // 2, y - height // 2
        self.rect = pygame.Rect(self.x, self.y, width, height)
        self.color = color
        self.surface = self._create_surface(color, width, height, border_radius=int(height // 2))
        self.filter = self._create_surface("black", width, height, border_radius=int(height // 2), alpha=50)
        self.label = Label(self.rect.center, text, font_name, self.rect.height // 2, text_color)
        self.command = command
        self.is_hovered = False
        self.set_alpha(0)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.surface, (self.x, self.y))
        self.label.draw(screen)
        if not self.is_hovered:
            screen.blit(self.filter, (self.x, self.y))

    def update(self, mouse_pos: tuple[int, int]):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_click(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.command()

    def set_alpha(self, alpha: int):
        self.surface.set_alpha(alpha)
        self.label.set_alpha(alpha)

    def update_text(self, new_text: str):
        self.label.update_text(new_text)

    def reset(self):
        self.set_alpha(0)

    @staticmethod
    def _create_surface(color: str, width: int, height: int, border_radius: int, alpha: int = None) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, width, height), border_radius=border_radius)
        if alpha is not None:
            surface.set_alpha(alpha)
        return surface


class ImageButton:
    def __init__(self, center: tuple[int, int], image: pygame.Surface, command):
        self.image = image
        self.rect = self.image.get_rect(center=center)
        self.command = command

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def handle_click(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.command()


class Label:
    def __init__(self, center: tuple[int, int], text: str, font_name: str, font_size: int, color: str):
        self.text = text
        self.center = center
        self.font_path = f"assets/font/{font_name}.ttf"
        self.font = pygame.font.Font(self.font_path, font_size)
        self.color = color
        self.surface = self._create_surface()
        self.rect = self.surface.get_rect(center=center)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.surface, self.rect)

    def update_text(self, new_text: str):
        self.text = new_text
        self.surface = self._create_surface()
        self.rect = self.surface.get_rect(center=self.center)

    def set_alpha(self, alpha: int):
        self.surface.set_alpha(alpha)

    def _create_surface(self) -> pygame.Surface:
        return self.font.render(self.text, True, self.color)


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

