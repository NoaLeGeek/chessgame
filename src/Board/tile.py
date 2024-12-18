import pygame
class Tile:
    def __init__(self, board, pos: tuple[int, int], size):
        self.board = board
        self.pos = pos
        self.size = size
        self.calc_position(board.config.margin)
        self.highlight_color = None
        self.piece = None

    def get_square_color(self):
        return (sum(self.pos)) % 2
    
    def move(self, pos: tuple[int, int]) -> None:
        self.pos = pos
        self.calc_position(self.board.config.margin)

    def calc_moves(self, **kwds):
        self.piece.calc_moves(self.board, self.pos, **kwds)

    def calc_position(self, margin):
        self.coord = (self.pos[1] * self.size + margin, self.pos[0] * self.size + margin)

    def can_move(self, to: tuple[int, int]) -> bool:
        row, column = to
        if self.board.config.rules["giveaway"] == True:
            return True
        if (self.row, self.column) == (row, column):
            return True
        piece_row, piece_column = self.row, self.column
        # When called, (row, column) is empty, is occupied by a object with no hitbox or is occupied by a opponent piece
        # Save the destination square object
        save_tile = self.board.get_tile(row, column)
        self_tile = self.board.get_tile(self.row, self.column)
        # Swap the piece with the destination square
        self.board.board[(row, column)] = self.board.board[(self.row, self.column)]
        del self.board.board[(self.row, self.column)]
        self.row, self.column = row, column
        # Check if the king is in check after the move
        can_move = not self.board.is_in_check()
        # Restore the initial state of the board
        self.board.board[(piece_row, piece_column)] = self_tile
        self.board.board[(row, column)] = save_tile
        # Delete the key if the tile was empty
        if save_tile is None:
            del self.board.board[(row, column)]
        self.row, self.column = piece_row, piece_column
        return can_move

    def get_color(self):
        r, g, b = None, None, None
        match self.highlight_color:
            case 0:
                r, g, b = 255, 0, 0, 75
            # Shift + Right click
            case 1:
                r, g, b = 0, 255, 0, 75
            # Ctrl + Right click
            case 2:
                r, g, b = 255, 165, 0, 75
            # History move
            case 3:
                r, g, b = 255, 255, 0, 75
            # Selected piece
            case 4:
                r, g, b = 0, 255, 255, 75
            # Void
            case None:
                r, g, b = 0, 0, 0, 0
        return r, g, b