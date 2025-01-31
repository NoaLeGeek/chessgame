import pygame
from scenes.scene import Scene
from board.board import Board
from board.piece import piece_to_notation
from utils import left_click, right_click, get_pos, get_color, flip_pos, load_image
from constants import WHITE
from config import config
from gui import RectButton


class Game(Scene):
    def __init__(self):
        self.board = Board()
        self.highlighted_squares = {}
        self.game_over = False
        super().__init__()

    def create_buttons(self):
        self.buttons = {
            "quit": RectButton(config.width*0.9, config.height*0.95, config.width*0.15, config.height*0.06, int(config.height*0.06//2), 'white', 'QUIT', 'Geizer.otf', 'black', self.manager.go_back),
            "flip": RectButton(config.width*0.9, config.height*0.8, config.width*0.07, config.width*0.07, int(config.width*0.015), 'white', '', 'Geizer.otf', 'black', self.board.flip_board, image=load_image("assets/images/arrows.png", (config.width*0.07, config.width*0.07)))
        }
        

    def render(self, screen:pygame.Surface):
        super().render(screen)
        screen.blit(self.board.image, (config.margin, config.margin))
        self._draw_pieces(screen)
        self._draw_highlight(screen)
        if self.board.selected is not None:
            self._draw_moves(screen)
        if self.board.promotion is not None:
            self._draw_promotion(screen)

    def update(self):
        super().update()

    def _draw_pieces(self, screen):
        for tile in self.board.board.values():
            if tile is None:
                raise ValueError("Tile is None")
            if self.board.is_empty(tile.pos):
                continue
            if config.piece_asset == "blindfold" or (tile == self.board.selected and self.board.promotion is not None):
                continue
            if tile.piece.image is None:
                raise ValueError(f"Piece image is None for {tile.piece}")
            screen.blit(tile.piece.image, tile.coord)

    def _draw_highlight(self, screen):
        """Draws the highlighted squares on the board."""
        highlight_surface = pygame.Surface((config.tile_size, config.tile_size), pygame.SRCALPHA)
        for pos, highlight_color in self.highlighted_squares.items():
            highlight_surface.fill(get_color(highlight_color))
            x, y = pos[1] * config.tile_size + config.margin, pos[0] * config.tile_size + config.margin
            screen.blit(highlight_surface, (x, y))

    def _draw_moves(self, screen):
        if self.board.promotion is not None:
            return
        for move in self.board.selected.piece.moves:
            transparent_surface = pygame.Surface((config.tile_size, config.tile_size), pygame.SRCALPHA)
            pygame.draw.circle(transparent_surface, (0, 0, 0, 63), (config.tile_size // 2, config.tile_size // 2), config.tile_size // 8)
            screen.blit(transparent_surface, (move[1] * config.tile_size + config.margin, move[0] * config.tile_size + config.margin))

    def _draw_promotion(self, screen):
        selected = self.board.selected
        pos = self.board.promotion
        # Drawing the promotion's frame
        # We normalize the rect to avoid negative width or height, this flips the rect and makes it in the right direction when the board is flipped
        # pos needs to be offset by 1 if the board is flipped
        rect = pygame.Rect((pos[1] - min(0, self.board.flipped)) * config.tile_size + config.margin, (pos[0] - min(0, self.board.flipped)) * config.tile_size + config.margin, self.board.flipped * config.tile_size, self.board.flipped * len(selected.piece.promotion) * config.tile_size)
        rect.normalize()
        pygame.draw.rect(screen, WHITE, rect)
        # Drawing the promotion's pieces
        for i, type_piece in enumerate(selected.piece.promotion):
            image = self.board.piece_images[("w" if self.board.selected.piece.color == 1 else "b") + piece_to_notation(type_piece)]
            screen.blit(image, (pos[1] * config.tile_size + config.margin, (pos[0] + i * self.board.flipped) * config.tile_size + config.margin))

    def handle_left_click(self):
        pos = get_pos(pygame.mouse.get_pos())
        print("LEFT CLICK", pos)
        self.highlighted_squares.clear()
        if self.board.in_bounds(pos) and not self.board.is_empty(pos):
            piece = self.board.get_piece(pos)
            if piece is None:
                raise ValueError("Piece is None")
            if piece.color == self.board.turn:
                self.board.get_tile(pos).calc_moves(self.board)
        self.board.select(pos)

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
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN :
            if left_click():
                self.handle_left_click()
            elif right_click():
                self.handle_right_click()
        elif event.type == pygame.KEYDOWN :
            if event.key == pygame.K_r :
                self.board = Board()
            if event.key == pygame.K_f:
                self.board.flip_board()
                self.highlighted_squares = {flip_pos(pos): value for pos, value in self.highlighted_squares.items()}
