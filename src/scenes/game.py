import pygame
from scenes.scene import Scene
from board.board import Board
from board.piece import piece_to_notation
from utils import left_click, right_click, get_pos, debug_print, load_image
from constants import Fonts, Colors
from config import config
from gui import RectButton, Label
from board.player import Player


class Game(Scene):
    def __init__(self, current_player: Player, waiting_player: Player):
        self.current_player = current_player
        self.waiting_player = waiting_player
        self.board = Board(current_player, waiting_player, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        if (self.current_player.ia + self.waiting_player.ia) == 0 and self.current_player.color == -1:
            self.board.flip_board()
        self.evaluation_bar = pygame.Rect(config.margin, config.margin, config.eval_bar_width, config.height-config.margin*2)
        self.history_background = pygame.Rect(config.margin+config.columns*config.tile_size+config.eval_bar_width, config.margin, config.width*0.35, config.height-config.margin*2)
        self.ia_counter = 0
        super().__init__()

    def create_buttons(self):
        font_size = int(config.height*0.06)

        self.buttons = {
            'back': RectButton(
                x=config.width*0.955,
                y=config.height*0.08, 
                width=config.height*0.1,
                height=config.height*0.1,
                color=Colors.LIGHT_GRAY.value,
                hovered_color=Colors.WHITE.value,
                text='<-',
                text_color=Colors.DARK_GRAY.value,
                font_size=int(config.height*0.1),
                font_name=Fonts.GEIZER,
                command=self.manager.go_back
            ),
            "flip": RectButton(
                x=self.history_background.centerx, 
                y=config.height*0.9, 
                width=config.width*0.05, 
                height=config.width*0.05, 
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                command=self.board.flip_board, 
                image=load_image("assets/images/arrows.png",(config.width*0.05, config.width*0.05))
            ),
            'undo':RectButton(
                x=self.history_background.centerx-config.width*0.07, 
                y=config.height*0.9, 
                width=config.width*0.05, 
                height=config.width*0.05, 
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='<', 
                font_name=Fonts.GEIZER, 
                font_size=font_size,
                text_color=Colors.BLACK.value, 
                command=lambda:self.board.move_tree.go_backward(self.board)
            ) ,
            'redo':RectButton(
                x=self.history_background.centerx+config.width*0.07, 
                y=config.height*0.9, 
                width=config.width*0.05, 
                height=config.width*0.05, 
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='>', 
                font_name=Fonts.GEIZER, 
                font_size=font_size,
                text_color=Colors.BLACK.value, 
                command=lambda:self.board.move_tree.go_forward(self.board)
            ),
            'root':RectButton(
                x=self.history_background.centerx-config.width*0.14, 
                y=config.height*0.9, 
                width=config.width*0.05, 
                height=config.width*0.05, 
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='<<', 
                font_name=Fonts.GEIZER, 
                font_size=font_size,
                text_color=Colors.BLACK.value, 
                command=lambda:self.board.move_tree.go_root(self.board)
            ),
            'leaf':RectButton(
                x=self.history_background.centerx+config.width*0.14, 
                y=config.height*0.9, 
                width=config.width*0.05, 
                height=config.width*0.05, 
                color=Colors.LIGHT_GRAY.value, 
                hovered_color=Colors.WHITE.value,
                text='>>', 
                font_name=Fonts.GEIZER, 
                font_size=font_size,
                text_color=Colors.BLACK.value, 
                command=lambda:self.board.move_tree.go_leaf(self.board)
            ) 
        }

    def create_labels(self):
        self.labels = {}

    def render(self, screen:pygame.Surface):
        pygame.draw.rect(screen, Colors.DARK_GRAY.value, self.history_background)
        self.draw_eval_bar(screen)
        screen.blit(self.board.image, (config.margin + config.eval_bar_width, config.margin))
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

        for label in self.board.history:
            label.draw(screen)

        super().render(screen)
        
    def update(self):
        super().update()
        if self.board.game_over == False and self.board.current_player.ia == True:
            if self.ia_counter >= 1:

                self.board.current_player.play_move(self.board)
                self.ia_counter = 0
            else :
                self.ia_counter += 1/config.fps
        if self.board.winner and not self.labels:
            self.handle_winner()

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
                x, y = tile.pos[1] * config.tile_size + config.margin + config.eval_bar_width, tile.pos[0] * config.tile_size + config.margin
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
            screen.blit(transparent_surface, (move.to_pos[1] * config.tile_size + config.margin + config.eval_bar_width, move.to_pos[0] * config.tile_size + config.margin))

    def _draw_promotion(self, screen):
        piece = self.board.selected.piece
        pos = self.board.promotion
        # Drawing the promotion's frame
        # We normalize the rect to avoid negative width or height, this flips the rect and makes it in the right direction when the board is flipped
        # pos needs to be offset by 1 if the board is flipped
        rect = pygame.Rect((pos[1] - min(0, self.board.flipped*piece.color)) * config.tile_size + config.margin + config.eval_bar_width, (pos[0] - min(0, self.board.flipped*piece.color)) * config.tile_size + config.margin, self.board.flipped*piece.color * config.tile_size, self.board.flipped*piece.color * len(piece.promotion) * config.tile_size)
        rect.normalize()
        pygame.draw.rect(screen, Colors.WHITE.value, rect)
        # Drawing the promotion's pieces
        for i, type_piece in enumerate(piece.promotion):
            image = self.board.piece_images[("w" if piece.color == 1 else "b") + piece_to_notation(type_piece)]
            screen.blit(image, (pos[1] * config.tile_size + config.margin + config.eval_bar_width, (pos[0] + i * self.board.flipped*piece.color) * config.tile_size + config.margin))

    def handle_left_click(self, keys):
        pos = get_pos(pygame.mouse.get_pos())
        debug_print("LEFT CLICK", pos)
        if self.board.in_bounds(pos):
            if self.board.game_over == False and self.board.current_player.ia == -1:
                self.board.select(pos)

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
                self.board = Board(self.current_player if self.current_player.color == 1 else self.waiting_player, self.current_player if self.current_player.color == -1 else self.waiting_player)
            if keys[pygame.K_f]:
                self.board.flip_board()
            if keys[pygame.K_SPACE]:
                move = self.board.ia.predict(self.board)
                move.execute(self.board)
            if keys[pygame.K_LEFT]:
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    self.board.move_tree.go_root(self.board)
                else:
                    self.board.move_tree.go_backward(self.board)
            if keys[pygame.K_RIGHT]:
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    self.board.move_tree.go_leaf(self.board)
                else:
                    self.board.move_tree.go_forward(self.board)
            if keys[pygame.K_UP]:
                self.board.move_tree.go_next(self.board)
            if keys[pygame.K_DOWN]:
                self.board.move_tree.go_previous(self.board)
            if keys[pygame.K_t]:
                print(self.board.history)

    def handle_winner(self):
        if self.board.winner == 'White':
            text = 'Checkmate !\nWhite win'
        elif self.board.winner == 'Black' :
            text = 'Checkmate !\nBlack win'
        elif self.board.winner == 'Stalemate':
            text = 'Stalemate'
        elif self.board.winner == 'Draw by threefold repetition':
            text = '          Draw by\nthreefold repetition'
        elif self.board.winner == 'Draw by insufficient material':
            text = '          Draw by\ninsufficient material'
        elif self.board.winner == 'Draw by the 50-move rule':
            text = 'Draw by the 50-move rule'

        self.labels.update({
                'end': Label(
                center=((config.tile_size*8)//2+config.margin+config.eval_bar_width, config.height//2),
                text = text,
                font_name=Fonts.GEIZER,
                font_size=int(config.height*0.1),
                color=Colors.WHITE.value,
            )
        })

    def draw_eval_bar(self, screen):
        value = (self.board.score + self.board.negamax.checkmate) / (self.board.negamax.checkmate*2)
        
        if self.board.score >= 0:
            white_height = value
            black_height = 1-value
        else :
            white_height = 1-value
            black_height = value
        white_height *= self.evaluation_bar.height
        black_height *= self.evaluation_bar.height
        pygame.draw.rect(screen, Colors.WHITE.value, (self.evaluation_bar.x, self.evaluation_bar.y, self.evaluation_bar.width, white_height))
        pygame.draw.rect(screen, Colors.BLACK.value, (self.evaluation_bar.x+white_height, self.evaluation_bar.y, self.evaluation_bar.width, black_height))



