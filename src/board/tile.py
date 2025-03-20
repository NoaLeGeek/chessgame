from constants import Colors
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
        self.coord = (self.pos[1] * config.tile_size + config.margin + config.eval_bar_width, self.pos[0] * config.tile_size + config.margin)

    def flip(self):
        self.pos = flip_pos(self.pos)
        self.calc_position()

    def can_move(self, board, to: tuple[int, int]) -> bool:
        if self.piece is None:
            raise ValueError(f"No piece on the tile {self.pos}, cannot move to {to}")
        if self.pos == to:
            return True
        # When called, to is empty or occupied by a opponent piece
        # Save the destination square object
        save_piece = board.get_piece(to)
        self_piece = self.piece
        # Swap the piece with the destination square
        if self.piece.notation == "K":
            board.get_player(self.piece.color).king = to
        board.get_tile(to).piece = self.piece
        self.piece = None
        # Check if the king is in check after the move
        can_move = not board.current_player.is_king_check(board)
        # Restore the initial state of the board
        self.piece = self_piece
        board.get_tile(to).piece = save_piece
        if self.piece.notation == "K":
            board.get_player(self.piece.color).king = self.pos
        return can_move
    
    def get_color(self):
        color, a = None, None
        match self.highlight_color:
            # Right click
            case 0:
                color, a = Colors.RED.value, 75
            # Shift + Right click
            case 1:
                color, a = Colors.GREEN.value, 75
            # Ctrl + Right click
            case 2:
                color, a = Colors.ORANGE.value, 75
            # History move
            case 3:
                color, a = Colors.YELLOW.value, 75
            # Selected piece
            case 4:
                color, a = Colors.CYAN.value, 75
        return *color, a
