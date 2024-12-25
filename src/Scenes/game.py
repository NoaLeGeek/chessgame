import pygame
from Scenes.scene import Scene, SceneManager
from Board.board import Board
from utils import left_click
from Board.piece import Piece
from constants import WHITE
from config import config


class Game(Scene):
    def __init__(self, manager:SceneManager):
        super().__init__(manager)
        self.board = Board()
        self.game_over = False

    def render(self, screen:pygame.Surface):
        screen.blit(self.board.image, (config.margin, config.margin))
        self.draw_pieces(screen)
        self.draw_highlight(screen)
        if self.board.selected:
            self.draw_moves(screen)
        if self.board.promotion:
            self.draw_promotion(screen)

    def update(self):
        pass

    def draw_pieces(self, screen):
        #print("selected", self.board.selected, ((self.board.selected.row, self.board.selected.column) if self.board.selected else None))
        for tile in self.board.board.values():
            assert tile is not None, "Tile is None"
            if config.piece_asset != "blindfold":
                assert tile.piece.image, "Piece has no image"
                screen.blit(tile.piece.image, tile.coord)

    def draw_highlight(self, screen):
        for tile in self.board.board.values():
            if tile.highlight_color is not None:
                transparent_surface = pygame.Surface((config.tile_size, config.tile_size), pygame.SRCALPHA)
                transparent_surface.fill(*tile.get_color())
                screen.blit(transparent_surface, (tile.pos[1] * config.tile_size + config.margin, tile.pos[0] * config.tile_size + config.margin))

    def draw_moves(self, screen):
        #print("actual moves", [move.to for move in self.board.selected.piece.moves])
        for move in self.board.selected.piece.moves:
            transparent_surface = pygame.Surface((config.tile_size, config.tile_size), pygame.SRCALPHA)
            pygame.draw.circle(transparent_surface, (0, 0, 0, 63), (config.tile_size // 2, config.tile_size // 2), config.tile_size // 8)
            screen.blit(transparent_surface, (move[1] * config.tile_size + config.margin, move[0] * config.tile_size + config.margin))

    def draw_promotion(self, screen):
        pygame.draw.rect(screen, WHITE, (self.promote * config.tile_size + config.margin, get_value(x, 0, 4) * config.tile_size + config.margin, config.tile_size, 4*config.tile_size))
        screen.blit(self.piece_images[self.turn]['+'+self.selected.notation], (self.selected.column*config.tile_size+config.margin, (self.selected.row+1)*config.tile_size+config.margin))
        screen.blit(self.selected.image, (self.selected.column*config.tile_size+config.margin, (self.selected.row+2)*config.tile_size+config.margin))

    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            if left_click():
                self.board.handle_left_click()
        elif event.type == pygame.KEYDOWN :
            if event.key == pygame.K_r :
                self.board = Board(config.rows)
            if event.key == pygame.K_ESCAPE :
                self.manager.go_back()