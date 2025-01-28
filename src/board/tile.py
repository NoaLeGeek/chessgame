import pygame
from config import config
from utils import flip_pos

class Tile:
    def __init__(self, pos: tuple[int, int]):
        self.pos = pos
        self.calc_position()
        self.highlight_color = None
        self.piece = None

    def get_square_color(self):
        return (sum(self.pos)) % 2

    def calc_moves(self, board, **kwds):
        return self.piece.calc_moves(board, self.pos, **kwds)

    def calc_position(self):
        self.coord = (self.pos[1] * config.tile_size + config.margin, self.pos[0] * config.tile_size + config.margin)

    def flip(self):
        self.pos = flip_pos(self.pos)
        self.calc_position()

    def can_move(self, board, to: tuple[int, int]) -> bool:
        if self.pos == to:
            return True
        piece_pos = self.pos
        # When called, to is empty, is occupied by a object with no hitbox or is occupied by a opponent piece
        # Save the destination square object
        save_tile = board.get_tile(to)
        self_tile = self
        # Swap the piece with the destination square
        board.board[to] = board.board[self.pos]
        board.board[self.pos] = Tile(self.pos)
        self.pos = to
        if self.piece.notation == "K":
            board.kings[self.piece.color] = to
        # Check if the king is in check after the move
        can_move = not board.is_king_checked(self.piece.color)
        # Restore the initial state of the board
        board.board[piece_pos] = self_tile
        board.board[to] = save_tile
        # Empty the tile if it was empty
        if save_tile is None:
            board.board[to].piece = None
        self.pos = piece_pos
        if self.piece.notation == "K":
            board.kings[self.piece.color] = piece_pos
        return can_move
