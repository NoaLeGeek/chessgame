import pygame
from config import config

class Tile:
    def __init__(self, pos: tuple[int, int]):
        self.pos = pos
        self.calc_position()
        self.highlight_color = None
        self.piece = None

    def get_square_color(self):
        return (sum(self.pos)) % 2
    
    def move(self, pos: tuple[int, int]) -> None:
        self.pos = pos
        self.calc_position()

    def calc_moves(self, board, **kwds):
        self.piece.calc_moves(board, self.pos, **kwds)

    def calc_position(self):
        self.coord = (self.pos[1] * config.tile_size + config.margin, self.pos[0] * config.tile_size + config.margin)

    def can_move(self, board, to: tuple[int, int]) -> bool:
        if config.rules["giveaway"] == True:
            return True
        if self.pos == to:
            return True
        piece_pos = self.pos
        # When called, to is empty, is occupied by a object with no hitbox or is occupied by a opponent piece
        # Save the destination square object
        save_tile = board.get_tile(to)
        self_tile = board.get_tile(self.pos)
        # Swap the piece with the destination square
        board.board[to] = board.board[self.pos]
        del board.board[self.pos]
        self.pos = to
        if self.piece.notation == "K":
            board.kings[self.piece.color] = to
        # Check if the king is in check after the move
        can_move = not board.is_king_checked()
        # Restore the initial state of the board
        board.board[piece_pos] = self_tile
        board.board[to] = save_tile
        # Delete the key if the tile was empty
        if save_tile is None:
            del board.board[to]
        self.pos = piece_pos
        if self.piece.notation == "K":
            board.kings[self.piece.color] = piece_pos
        return can_move