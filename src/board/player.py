from src.config import config
from src.board.move import Move

class Player:
    def __init__(self, color: int):
        """
        Initializes a Player object with the specified color.

        This constructor sets up the player's color, initializes the positions
        of their pieces by type, and tracks the king's position. It also includes
        an attribute for AI behavior, which is set to a default value.

        Parameters:
            color (int): The color of the player. Typically, 0 represents white
                         and 1 represents black.

        Attributes:
            color (int): The color of the player.
            pieces (dict): A dictionary where keys are piece types ("P" for pawn,
                           "R" for rook, "N" for knight, "B" for bishop, "Q" for queen,
                           "K" for king) and values are lists of positions for each
                           piece type.
            king (None or tuple): The position of the king on the board. Initially set
                                  to None and should be updated when the king's position
                                  is known.
            ia (int): An integer representing whether the player is controlled by AI.
                      A value of -1 indicates no AI control.
        """
        self.color = color
        # Pieces' position depending on their type
        self.pieces = {"P": [], "R": [], "N": [], "B": [], "Q": [], "K": []}
        # King's position
        self.king = None
        self.ia = -1

    def add_piece(self, piece) -> None:
        """
        Adds a chess piece to the player's collection of pieces.

        This method appends the given chess piece to the list of pieces
        associated with its notation in the player's collection.

        Parameters:
            piece: The chess piece to be added. It is expected to have a 
                   `notation` attribute that serves as a key to categorize
                   the piece in the player's collection.
        """
        self.pieces[piece.notation].append(piece)

    def remove_piece(self, piece) -> None:
        """
        Removes a piece from the player's collection of pieces. If the piece being removed
        is the king, the player's king attribute is set to None.

        Parameters:
            piece (Piece): The piece object to be removed. It must have a `notation` attribute
                           that identifies the type of piece (e.g., 'K' for king).
        """
        self.pieces[piece.notation].remove(piece)
        if piece.notation == 'K':
            self.king = None

    def get_moves(self, board) -> list[Move]:
        """
        Generates a list of all possible moves for the player based on the current state of the board.

        This method iterates through all tiles on the board, checking if the tile contains a piece
        belonging to the player. For each piece, it calculates all valid moves, including special
        handling for pawn promotion. The resulting moves are returned as a list of `Move` objects.

        Parameters:
            board (Board): The current state of the chessboard. It provides access to the tiles,
                           pieces, and utility methods for move calculation.

        Returns:
            list[Move]: A list of all possible moves for the player, including regular moves and
                        promotion moves if applicable.
        """
        moves = []
        for tile in board.board.values():
            if board.is_empty(tile.pos):
                continue
            if tile.piece.color != self.color:
                continue
            for to_pos in tile.calc_moves(board):
                if to_pos[0] in [0, config.rows - 1] and tile.piece.notation == "P":
                    for promotion in tile.piece.promotion:
                        moves.append(board.convert_to_move(tile.pos, to_pos, promotion))
                else:
                    moves.append(board.convert_to_move(tile.pos, to_pos))
        return moves
    
    def get_legal_moves(self, board) -> list[Move]:
        """
        Retrieves a list of all legal moves for the player on the given board.

        This method filters the moves generated by `get_moves` to include only those
        that are legal according to the current state of the board.

        Parameters:
            board (Board): The current state of the chessboard.

        Returns:
            list[Move]: A list of legal moves that the player can make.
        """
        return [move for move in self.get_moves(board) if move.is_legal(board)]
    
    def is_king_check(self, board) -> bool:
        """
        Determines if the player's king is in check.

        This method checks whether the player's king is under attack by any of the opponent's possible moves.
        If the "giveaway" rule is enabled in the configuration, the method will always return False, as the 
        rule implies that checks are not considered.

        Parameters:
            board (Board): The current state of the chessboard, which includes information about all pieces 
                           and their positions.

        Returns:
            bool: True if the player's king is in check, False otherwise.
        """
        if config.rules["giveaway"]:
            return False
        return self.king in [move.to_pos for move in board.get_player(-self.color).get_moves(board)]