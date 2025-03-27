from src.config import config
from src.utils import flip_pos
from src.constants import Colors

class Tile:
    def __init__(self, pos: tuple[int, int]):
        """
        Initializes a Tile object representing a single square on a chessboard.

        Parameters:
            pos (tuple[int, int]): A tuple representing the position of the tile 
                                   on the chessboard in (row, column) format.

        Attributes:
            pos (tuple[int, int]): The position of the tile on the chessboard.
            highlight_color (None | tuple[int, int, int, int]): The color used to highlight the tile, 
                                             if applicable. Defaults to None.
            piece (None | Piece): The chess piece currently occupying the tile, 
                                   if any. Defaults to None.
        """
        self.pos = pos
        self.calc_position()
        self.highlight_color = None
        self.piece = None

    def get_square_color(self) -> int:
        """
        Determines the color of the square based on its position.

        This method calculates the color of a chessboard square using the sum of 
        the coordinates in `self.pos`. If the sum is even, the square is white (0). 
        If the sum is odd, the square is black (1).

        Returns:
            int: The color of the square, where 0 represents white and 1 represents black.
        """
        return (sum(self.pos)) % 2

    def calc_moves(self, board, **kwds) -> list[tuple[int, int]]:
        """
        Calculate the possible moves for the piece on this tile.

        This method delegates the calculation of possible moves to the piece
        located on the tile. It uses the current board state and the position
        of the tile to determine valid moves.

        Parameters:
            board (list[list]): The current state of the chessboard, represented
                as a 2D list where each element corresponds to a tile.
            **kwds: Additional keyword arguments that may be required for specific
                piece movement logic.

        Returns:
            list[tuple[int, int]]: A list of tuples representing the valid moves
            for the piece. Each tuple contains the row and column indices of a
            potential destination tile.
        """
        return self.piece.calc_moves(board, self.pos, **kwds)

    def calc_position(self) -> None:
        """
        Calculates and updates the pixel coordinates of the tile on the board.

        This method computes the position of the tile in terms of pixel coordinates
        based on its grid position (`self.pos`) and updates the `self.coord` attribute.
        The calculation takes into account the tile size, margin, and evaluation bar width
        defined in the `config` module.
        """
        self.coord = (self.pos[1] * config.tile_size + config.margin + config.eval_bar_width, self.pos[0] * config.tile_size + config.margin)

    def flip(self) -> None:
        """
        Flips the tile's position and recalculates its coordinates.

        This method updates the tile's position by flipping it using the `flip_pos` function.
        After flipping, it recalculates the tile's position on the board by calling `calc_position`.
        """
        self.pos = flip_pos(self.pos)
        self.calc_position()

    def can_move(self, board, to: tuple[int, int]) -> bool:
        """
        Determines if a piece on the current tile can move to a specified destination tile 
        without putting its king in check.

        This method temporarily simulates the move by swapping the piece to the destination 
        tile and checks if the king of the current player is in check after the move. 
        It restores the board to its original state after the check.

        Parameters:
            board (Board): The current state of the chessboard.
            to (tuple[int, int]): The coordinates of the destination tile as a tuple (row, column).

        Returns:
            bool: True if the piece can move to the destination tile without putting its king 
                  in check, False otherwise.

        Raises:
            ValueError: If there is no piece on the current tile.
        """
        if self.piece is None:
            raise ValueError(f"No piece on the tile {self.pos}, cannot move to {to}. Board state: {str(board)}")
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
    
    def get_color(self) -> tuple[int, int, int, int]:
        """
        Determines the RGBA color of a tile based on its highlight state.

        This method uses the `highlight_color` attribute of the tile to determine
        the appropriate color and transparency level (alpha) to return. The color
        is represented as a tuple of four integers (R, G, B, A), where R, G, and B
        are the red, green, and blue components of the color, and A is the alpha
        (transparency) value.

        Returns:
            tuple[int, int, int, int]: A tuple representing the RGBA color of the tile.
        """
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
