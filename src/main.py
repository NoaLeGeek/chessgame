import pygame
from Scenes.scene import SceneManager
from config import Config
from Scenes.menu import MainMenu

def main():
    pygame.init()
    pygame.display.set_caption("Chesspy")
    pygame.mixer.init()
    config = Config()
    pygame.mixer.music.set_volume(config.volume)
    screen = pygame.display.set_mode((config.width, config.height))
    clock = pygame.time.Clock()
    manager = SceneManager()
    manager.set(MainMenu(manager, config))
    run = True
    while run :
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