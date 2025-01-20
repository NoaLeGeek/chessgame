import pygame
from scenes.scene import SceneManager
from config import config
from scenes.menu import MainMenu
from utils import generate_background_image

def main():
    pygame.init()
    pygame.display.set_caption("Chessgame")
    pygame.mixer.init()
    config.set_dimensions(*pygame.display.get_desktop_sizes()[0])
    pygame.mixer.music.set_volume(config.volume)
    screen = pygame.display.set_mode((config.width, config.height))
    clock = pygame.time.Clock()
    manager = SceneManager(generate_background_image())
    manager.set(MainMenu(manager))
    run = True
    while run:
        manager.render(screen)
        manager.update(clock.get_time()/1000)
        pygame.display.update()  
        clock.tick(config.fps)
        for event in pygame.event.get():
            manager.handle_event(event)
            if event.type == pygame.KEYDOWN :
                if event.key == pygame.K_ESCAPE :
                    manager.go_back()
            elif event.type == pygame.QUIT :
                run = False
    pygame.quit()

if __name__ == '__main__':
    main()