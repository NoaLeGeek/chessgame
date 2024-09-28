import pygame
from Scenes.scene import SceneManager
from config import Config
from Scenes.menu import MainMenu
from utils import generate_background_image

def main():
    pygame.init()
    pygame.display.set_caption("Chesspy")
    pygame.mixer.init()
    config = Config()
    config.set_dimensions(*pygame.display.get_desktop_sizes()[0])
    pygame.mixer.music.set_volume(config.volume)
    screen = pygame.display.set_mode((config.width, config.height))
    clock = pygame.time.Clock()
    manager = SceneManager(generate_background_image(config.background_asset, (config.width, config.height)))
    manager.set(MainMenu(manager, config))
    run = True
    while run:
        # TODO render background
        screen.fill('lightblue')
        manager.render(screen)
        manager.update()
        pygame.display.update()
        clock.tick(config.fps)
        for event in pygame.event.get():
            manager.handle_event(event)
            if event.type == pygame.QUIT :
                run = False
    pygame.quit()



if __name__ == '__main__':
    main()