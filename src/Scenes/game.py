import pygame
from Scenes.scene import Scene, SceneManager
from Board.board import Board
from utils import left_click
from Board.piece import Piece
from constants import WHITE


class Game(Scene):
    def __init__(self, manager:SceneManager, config):
        super().__init__(manager, config)
        self.board = Board(config, config.columns)
        self.game_over = False

    def render(self, screen:pygame.Surface):
        screen.blit(self.board.image, (self.config.margin, self.config.margin))
        self.draw_objects(screen)
        self.draw_highlight(screen)
        if self.board.selected:
            self.draw_moves(screen)
        if self.board.promotion:
            self.draw_promotion(screen)

    def update(self):
        pass

    def draw_objects(self, screen):
        for tile in self.board.board.values():
            assert tile is not None, "Tile is None"
            if self.board.debug:
                screen.blit(pygame.font.SysFont("monospace", 15).render(f"({tile.column},{tile.row})", 1, (0, 0, 0)), (tile.row*self.config.tile_size+35, tile.column*self.config.tile_size+60))
            if self.config.piece_asset != "blindfold":
                assert tile.object.image, "Object has no image"
                screen.blit(tile.object.image, (tile.x, tile.y))

    def draw_highlight(self, screen):
        for row in range(self.config.rows):
            for column in range(self.config.columns):
                if self.board.is_empty(row, column):
                    continue
                tile = self.board.get_tile(row, column)
                if tile.highlight_color is not None:
                    transparent_surface = pygame.Surface((self.config.tile_size, self.config.tile_size), pygame.SRCALPHA)
                    transparent_surface.fill(*tile.get_color())
                    screen.blit(transparent_surface, (column * self.config.tile_size + self.config.margin, row * self.config.tile_size + self.config.margin))

    def draw_moves(self, screen):
        for move in self.board.selected.moves:
            row, column = move[0], move[1]
            transparent_surface = pygame.Surface((self.config.tile_size, self.config.tile_size), pygame.SRCALPHA)
            pygame.draw.circle(transparent_surface, (0, 0, 0, 63), (self.config.tile_size // 2, self.config.tile_size // 2), self.config.tile_size // 8)
            screen.blit(transparent_surface, (column * self.config.tile_size + self.config.margin, row * self.config.tile_size + self.config.margin))

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
        pygame.draw.rect(screen, WHITE, (self.promote * self.config.tile_size + self.config.margin, get_value(x, 0, 4) * self.config.tile_size + self.config.margin, self.config.tile_size, 4*self.config.tile_size))
        screen.blit(self.piece_images[self.turn]['+'+self.selected.notation], (self.selected.column*self.config.tile_size+self.config.margin, (self.selected.row+1)*self.config.tile_size+self.config.margin))
        screen.blit(self.selected.image, (self.selected.column*self.config.tile_size+self.config.margin, (self.selected.row+2)*self.config.tile_size+self.config.margin))

    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            if left_click():
                self.board.handle_left_click()
        elif event.type == pygame.KEYDOWN :
            if event.key == pygame.K_r :
                self.board = Board(self.config.rows)
            if event.key == pygame.K_ESCAPE :
                self.manager.go_back()