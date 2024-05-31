import pygame
from Scenes.scene import Scene, SceneManager
from Board.board import Board


class Game(Scene):
    def __init__(self, manager:SceneManager, config):
        super().__init__(manager, config)
        self.board = Board(config, 9)

    def render(self, screen:pygame.Surface):
        self.board.draw(screen)

    def update(self):
        pass

    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            if pygame.mouse.get_pressed()[0]:
                self.board.handle_left_click()
        elif event.type == pygame.KEYDOWN :
            if event.key == pygame.K_r :
                self.board = Board(9)
            if event.key == pygame.K_ESCAPE :
                self.manager.go_back()


        
    
