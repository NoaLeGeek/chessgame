import pygame

from src.scenes.scene import SceneManager
from src.config import config
from src.scenes.menu import MainMenu
from src.constants import Colors

def main():
    pygame.init()
    pygame.display.set_caption("CheckThisOut")
    pygame.mixer.init()
    config.set_dimensions(*pygame.display.get_desktop_sizes()[0])
    pygame.mixer.music.set_volume(config.volume)
    screen = pygame.display.set_mode((config.width, config.height))
    clock = pygame.time.Clock()
    manager = SceneManager()
    manager.set(MainMenu())
    run = True
    while run:
        screen.fill(Colors.BLACK.value)
        manager.render(screen)
        manager.update(clock.get_time()/1000)
        pygame.display.update()
        clock.tick(config.fps)
        for event in pygame.event.get():
            manager.handle_event(event)
            if event.type == pygame.QUIT:
                run = False
    pygame.quit()

if __name__ == '__main__':
    main() 