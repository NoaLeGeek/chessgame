import pygame
from scenes.scene import Scene
from board.board import Board
from board.piece import piece_to_notation
from utils import left_click, right_click, get_pos, flip_pos, debug_print, load_image
from constants import Fonts, castling_king_column, Colors
from config import config
from gui import RectButton
from board.player import Player


class Game(Scene):
    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.board = Board(player1, player2, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        super().__init__()

    def create_buttons(self):
        self.buttons = {
            "quit": RectButton(config.width*0.9, config.height*0.95, config.width*0.15, config.height*0.06, int(config.height*0.06//2), Colors.WHITE, 'QUIT', Fonts.GEIZER, Colors.BLACK, self.manager.go_back),
            "flip": RectButton(config.width*0.9, config.height*0.8, config.width*0.07, config.width*0.07, int(config.width*0.015), Colors.WHITE, '', Fonts.GEIZER, Colors.BLACK, self.board.flip_board, image=load_image("assets/images/arrows.png", (config.width*0.07, config.width*0.07)))
        }
        
    def render(self, screen:pygame.Surface):
        super().render(screen)
        screen.blit(self.board.image, (config.margin, config.margin))
        # Highlight
        self._draw_highlight(screen)
        # Pieces
        self._draw_pieces(screen)
        # Moves
        if self.board.selected is not None:
            self._draw_moves(screen)
        # Promotion
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
        for tile in self.board.board.values():
            if tile.highlight_color is not None:
                highlight_surface.fill(tile.get_color())
                x, y = tile.pos[1] * config.tile_size + config.margin, tile.pos[0] * config.tile_size + config.margin
                screen.blit(highlight_surface, (x, y))

    def _draw_moves(self, screen):
        if self.board.promotion is not None:
            return
        for move in self.board.selected.piece.moves:
            transparent_surface = pygame.Surface((config.tile_size, config.tile_size), pygame.SRCALPHA)
            # Capture move
            if move.capture == True:
                pygame.draw.circle(transparent_surface, (0, 0, 0, 63), (config.tile_size // 2, config.tile_size // 2), config.tile_size // 2, config.tile_size // 12)
            # Normal move
            else:
                pygame.draw.circle(transparent_surface, (0, 0, 0, 63), (config.tile_size // 2, config.tile_size // 2), config.tile_size // 8)
            screen.blit(transparent_surface, (move.to_pos[1] * config.tile_size + config.margin, move.to_pos[0] * config.tile_size + config.margin))

    def _draw_promotion(self, screen):
        piece = self.board.selected.piece
        pos = self.board.promotion
        # Drawing the promotion's frame
        # We normalize the rect to avoid negative width or height, this flips the rect and makes it in the right direction when the board is flipped
        # pos needs to be offset by 1 if the board is flipped
        rect = pygame.Rect((pos[1] - min(0, self.board.flipped*piece.color)) * config.tile_size + config.margin, (pos[0] - min(0, self.board.flipped*piece.color)) * config.tile_size + config.margin, self.board.flipped*piece.color * config.tile_size, self.board.flipped*piece.color * len(piece.promotion) * config.tile_size)
        rect.normalize()
        pygame.draw.rect(screen, Colors.WHITE, rect)
        # Drawing the promotion's pieces
        for i, type_piece in enumerate(piece.promotion):
            image = self.board.piece_images[("w" if piece.color == 1 else "b") + piece_to_notation(type_piece)]
            screen.blit(image, (pos[1] * config.tile_size + config.margin, (pos[0] + i * self.board.flipped*piece.color) * config.tile_size + config.margin))

    def handle_left_click(self, keys):
        pos = get_pos(pygame.mouse.get_pos())
        debug_print("LEFT CLICK", pos)
        if self.board.in_bounds(pos):
            self.board.clear_highlights()
            if self.board.game_over == False:
                if not self.board.is_empty(pos) and self.board.get_piece(pos).color == self.board.turn:
                    self.board.get_tile(pos).calc_moves(self.board)
                self.board.select(pos)
            if self.board.move_logs:
                last_move = self.board.get_last_move()
                to_pos = last_move.to_pos if not last_move.castling else (last_move.to_pos[0], flip_pos(castling_king_column[(1 if last_move.to_pos[1] > last_move.from_pos[1] else -1)*self.board.flipped], flipped=self.board.flipped))
                self.board.highlight_tile(3, last_move.from_pos, to_pos)
            if self.board.selected is not None and self.board.selected.piece is not None:
                self.board.highlight_tile(4, self.board.selected.pos)

    def handle_right_click(self, keys):
        pos = get_pos(pygame.mouse.get_pos())
        debug_print("RIGHT CLICK", pos)
        if self.board.in_bounds(pos):
            if self.board.selected is not None:
                self.board.selected.highlight_color = None
                self.board.selected = None
            highlight_color = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) + (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) * 2
            self.board.highlight_tile(highlight_color, pos)

    def handle_event(self, event:pygame.event.Event):
        super().handle_event(event)
        keys = pygame.key.get_pressed()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if left_click():
                self.handle_left_click(keys)
            elif right_click():
                self.handle_right_click(keys)
        elif event.type == pygame.KEYDOWN:
            if keys[pygame.K_r]:
                self.board = Board(self.player1, self.player2)
            if keys[pygame.K_f]:
                self.board.flip_board()
            if keys[pygame.K_SPACE]:
                move = self.board.ia.predict(self.board)
                move.execute()
            if keys[pygame.K_LEFT]:
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    self.board.move_tree.go_root()
                else:
                    self.board.move_tree.go_backward()
            if keys[pygame.K_RIGHT]:
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    self.board.move_tree.go_leaf()
                else:
                    self.board.move_tree.go_forward()
            if keys[pygame.K_UP]:
                self.board.move_tree.go_next()
            if keys[pygame.K_DOWN]:
                self.board.move_tree.go_previous()
