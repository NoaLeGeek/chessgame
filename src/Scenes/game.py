import pygame
from Scenes.scene import Scene, SceneManager
from Board.board import Board
from utils import left_click, right_click, get_pos, get_color, flip_pos
from constants import WHITE
from config import config


class Game(Scene):
    def __init__(self, manager:SceneManager):
        super().__init__(manager)
        castling_fen = "r3k2r/p2ppp1p/1Q5B/8/8/1q5b/P2PPP1P/R3K2R w KQkq - 0 1"
        self.board = Board(castling_fen)
        self.highlighted_squares = {}
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
        for tile in self.board.board.values():
            assert tile is not None, "Tile is None"
            if config.piece_asset != "blindfold":
                assert tile.piece.image, "Piece has no image"
                screen.blit(tile.piece.image, tile.coord)

    def draw_highlight(self, screen):
        for pos, highlight_color in self.highlighted_squares.items():
            transparent_surface = pygame.Surface((config.tile_size, config.tile_size), pygame.SRCALPHA)
            transparent_surface.fill(get_color(highlight_color))
            screen.blit(transparent_surface, (pos[1] * config.tile_size + config.margin, pos[0] * config.tile_size + config.margin))

    def draw_moves(self, screen):
        for move in self.board.selected.piece.moves:
            transparent_surface = pygame.Surface((config.tile_size, config.tile_size), pygame.SRCALPHA)
            pygame.draw.circle(transparent_surface, (0, 0, 0, 63), (config.tile_size // 2, config.tile_size // 2), config.tile_size // 8)
            screen.blit(transparent_surface, (move[1] * config.tile_size + config.margin, move[0] * config.tile_size + config.margin))

    def draw_promotion(self, screen):
        pygame.draw.rect(screen, WHITE, (self.promote * config.tile_size + config.margin, get_value(x, 0, 4) * config.tile_size + config.margin, config.tile_size, 4*config.tile_size))
        screen.blit(self.piece_images[self.turn]['+'+self.selected.notation], (self.selected.column*config.tile_size+config.margin, (self.selected.row+1)*config.tile_size+config.margin))
        screen.blit(self.selected.image, (self.selected.column*config.tile_size+config.margin, (self.selected.row+2)*config.tile_size+config.margin))

    def handle_left_click(self):
        pos = get_pos(pygame.mouse.get_pos())
        print("LEFT CLICK", pos)
        self.highlighted_squares = {}
        if self.board.in_bounds(pos) and not self.board.is_empty(pos) and self.board.get_piece(pos).color == self.board.turn:
            self.board.get_tile(pos).calc_moves(self.board)
        self.board.select_piece(pos)

    def handle_right_click(self):
        pos = get_pos(pygame.mouse.get_pos())
        print("RIGHT CLICK", pos)
        if self.board.in_bounds(pos):
            self.selected = None
            keys = pygame.key.get_pressed()
            highlight = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) + (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) * 2
            if self.highlighted_squares.get(pos) != highlight:
                self.highlighted_squares[pos] = highlight
            else:
                self.highlighted_squares.pop(pos, None)

    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            if left_click():
                self.handle_left_click()
            elif right_click():
                self.handle_right_click()
        elif event.type == pygame.KEYDOWN :
            if event.key == pygame.K_r :
                self.board = Board()
            if event.key == pygame.K_ESCAPE :
                self.manager.go_back()
            if event.key == pygame.K_f:
                self.board.flip_board()
                self.highlighted_squares = {flip_pos(pos): value for pos, value in self.highlighted_squares.items()}
