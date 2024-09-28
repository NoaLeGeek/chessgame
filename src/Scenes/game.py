import pygame
from Scenes.scene import Scene, SceneManager
from Board.board import Board
from utils import left_click


class Game(Scene):
    def __init__(self, manager:SceneManager, config):
        super().__init__(manager, config)
        self.board = Board(config, 9)

    def render(self, screen:pygame.Surface):
        self.board.draw(screen)

    def update(self):
        pass

    def draw_tiles(self, screen):
        for i in range(11):
            for j in range(9):
                screen.blit(self.tile_image, (j*self.config.tile_size+self.config.margin, i*self.config.tile_size+self.config.margin))
                if 0 < i < 10:
                    self.board[i - 1][j].draw(screen)
        pygame.draw.rect(screen, 'black', (self.config.margin, self.config.margin+self.config.tile_size, self.config.tile_size * 9, self.config.tile_size * 9), 2)

    def draw_pieces(self, screen):
        for row in self.board:
            for tile in row:
                if tile.occupying_piece:
                    screen.blit(tile.occupying_piece.image, (tile.x, tile.y))

    def draw_moves(self, screen):
        for move in self.selected_piece.moves:
            pygame.draw.circle(screen, 'grey', (move[1] * self.config.tile_size + self.config.tile_size // 2 + self.config.margin, move[0] * self.config.tile_size + self.config.tile_size // 2 + self.config.tile_size + self.config.margin), self.config.tile_size // 8)

    # def draw_reserves(self, screen):
    #     for i, notation in enumerate('PLNSGBR'):
    #         self.draw_reserve_piece(screen, notation, i, 1)
    #         if len(self.reserves[1][notation]) > 1:
    #             draw_text(screen, str(len(self.reserves[1][notation])), pygame.font.Font(None, self.config.tile_size // 2), 'black', (self.config.margin + self.config.tile_size + self.config.tile_size * i, self.config.margin))
    #         self.draw_reserve_piece(screen, notation, i, -1)
    #         if len(self.reserves[-1][notation]) > 1:
    #             draw_text(screen, str(len(self.reserves[-1][notation])), pygame.font.Font(None, self.config.tile_size // 2), 'black', (self.config.margin + self.config.tile_size + self.config.tile_size * i, self.config.height - self.config.tile_size - self.config.margin))

    # def draw_reserve_piece(self, screen, notation, i, position):
    #     y_pos = self.config.margin if position == 1 else self.config.height - self.config.tile_size - self.config.margin
    #     image = self.piece_images[position][notation].copy()
    #     image.set_alpha(255 if self.reserves[position][notation] else 100)
    #     screen.blit(image, (self.config.margin + self.config.tile_size + self.config.tile_size * i, y_pos))

    def draw_promotion(self, screen):
        pygame.draw.rect(screen, 'white', (self.selected_piece.column*self.config.tile_size+self.config.margin, (self.selected_piece.row+1)*self.config.tile_size+self.config.margin, self.config.tile_size, self.config.tile_size*2))
        screen.blit(self.piece_images[self.current_player]['+'+self.selected_piece.notation], (self.selected_piece.column*self.config.tile_size+self.config.margin, (self.selected_piece.row+1)*self.config.tile_size+self.config.margin))
        screen.blit(self.selected_piece.image, (self.selected_piece.column*self.config.tile_size+self.config.margin, (self.selected_piece.row+2)*self.config.tile_size+self.config.margin))

    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            if left_click():
                self.board.handle_left_click()
        elif event.type == pygame.KEYDOWN :
            if event.key == pygame.K_r :
                self.board = Board(9)
            if event.key == pygame.K_ESCAPE :
                self.manager.go_back()