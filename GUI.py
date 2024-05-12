import pygame

from constants import window, config, square_size, board_assets, piece_assets, background_assets, WHITE, get_value
from Pieces import Piece, Queen, Knight, Rook, Bishop

def draw_text(text: str, color: tuple[int, int, int], size: int, center: tuple[int, int], font: str) -> None:
    """
    Draws text on the game window.

    Args:
        text (str): The text to be displayed.
        color (tuple[int, int, int]): The RGB color value of the text.
        size (int): The font size of the text.
        center (tuple[int, int]): The coordinates of the center point of the text.
        font (str): The name of the font to be used.

    Returns:
        None
    """
    text_surface = pygame.font.SysFont(font, size).render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = center
    window.blit(text_surface, text_rect)

def draw_board(flipped: int) -> None:
    """
    Draws the chessboard on the window.

    Parameters:
    - flipped (int): Indicates whether the board is flipped or not. 
                     0 represents not flipped, 180 represents flipped.

    Returns:
    None
    """
    window.blit(pygame.transform.rotate(board_assets[config["selected_board_asset"]], get_value(flipped, 0, 180)), (config["margin"], config["margin"]))

def draw_piece(piece) -> None:
    """
    Draw a chess piece on the game window.

    Args:
        piece: The chess piece object to be drawn.

    Returns:
        None
    """
    window.blit(piece.image, (piece.x, piece.y))

def draw_pieces(board, promotion=None, debug: bool = False) -> None:
    """
    Draw the chess pieces on the game board.

    Args:
        board (list): The current state of the chess board.
        promotion (tuple, optional): The piece to be promoted and its position. Defaults to None.
        debug (bool, optional): Flag to enable debug mode. Defaults to False.
    """
    for row in range(len(board)):
        for column in range(len(board[row])):
            if debug:
                window.blit(pygame.font.SysFont("monospace", 15).render(f"({column},{row})", 1, (0, 0, 0)), (row*square_size+35, column*square_size+60))
            piece =  board[row][column]
            if piece == 0 or (promotion and promotion[0] == piece):
                continue
            draw_piece(piece)

def draw_moves(moves) -> None:
    """
    Draws circles on the chessboard to indicate possible moves.

    Args:
        moves (list): A list of positions (row, column) where circles should be drawn.

    Returns:
        None
    """
    for pos in moves:
        row, column = pos[0], pos[1]
        transparent_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        pygame.draw.circle(transparent_surface, (0, 0, 0, 63), (square_size // 2, square_size // 2), square_size // 8)
        window.blit(transparent_surface, (column * square_size + config["margin"], row * square_size + config["margin"]))

def draw_promotion(promotion, offset, flipped) -> None:
    """
    Draw the promotion interface on the chessboard.

    Args:
        promotion (Piece): The piece to be promoted.
        offset (int): The offset value for the column.
        flipped (int): The flipped value for the board orientation.

    Returns:
        None
    """
    x = promotion.color * flipped
    # Draw the promotion rectangle
    pygame.draw.rect(window, WHITE, ((promotion.column + offset) * square_size + config["margin"], get_value(x, 0, 4) * square_size + config["margin"], square_size, 4*square_size))
    # Draw the X rectangle
    pygame.draw.rect(window, (241, 241, 241), ((promotion.column + offset) * square_size + config["margin"], get_value(x, 4, 14/4) * square_size + config["margin"], square_size, .5*square_size))
    # Draw the X
    center_x, center_y = (promotion.column + offset + 1/2) * square_size + config["margin"], get_value(x, 17/4, 15/4) * square_size + config["margin"]
    pygame.draw.line(window, (139, 137, 135), (center_x - square_size / 8, center_y - square_size / 8), (center_x + square_size / 8, center_y + square_size / 8), round(square_size / 15))
    pygame.draw.line(window, (139, 137, 135), (center_x + square_size / 8, center_y - square_size / 8), (center_x - square_size / 8, center_y + square_size / 8), round(square_size / 15))
    if config["selected_piece_asset"] == "blindfold":
        return
    for i in range(5):
        if i < 4:
            render = [Queen, Knight, Rook, Bishop][i](promotion.color, get_value(x, 0, 7) + x * i, promotion.column + offset)
            render.image = piece_assets[config["selected_piece_asset"]][Piece.piece_to_index(render) + get_value(render.color, 0, 6)]
            window.blit(render.image, (render.x, render.y))
                  
def draw_highlightedSquares(highlightedSquares) -> None:
    """
    Draws highlighted squares on the chessboard.

    Args:
        highlightedSquares (dict): A dictionary containing the coordinates of the highlighted squares and their corresponding highlight type.

    Returns:
        None
    """
    for ((row, column), highlight) in highlightedSquares.items():
        match highlight:
            # Right click
            case 0:
                r, g, b = 255, 0, 0
            # Shift + Right click
            case 1:
                r, g, b = 0, 255, 0
            # Ctrl + Right click
            case 2:
                r, g, b = 255, 165, 0
            # History move
            case 3:
                r, g, b = 255, 255, 0
            # Selected piece
            case 4:
                r, g, b = 0, 255, 255
            case _:
                continue
        transparent_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        transparent_surface.fill((r, g, b, 75))
        window.blit(transparent_surface, (column * square_size + config["margin"], row * square_size + config["margin"]))

def draw_background() -> None:
    """
    Draws the background of the game window.
    """
    window.blit(background_assets[config["selected_background_asset"]], (0, 0))

def draw_settings() -> None:
    """
    Draws the settings on the game window.

    This function draws the selected piece assets and the selected board asset on the game window.
    The piece assets are positioned in a grid-like pattern, while the board asset is centered at the top of the window.

    Parameters:
    None

    Returns:
    None
    """
    if config["selected_piece_asset"] != "blindfold":
        for i, asset in enumerate(piece_assets[config["selected_piece_asset"]]):
            window.blit(asset, ((i % 6) * (square_size * 3/4) + (pygame.display.Info().current_w/2 - 3*(square_size * 3/4)), (i // 6) * (square_size * 3/4) + config["margin"]/4))
    board_asset = pygame.transform.scale(board_assets[config["selected_board_asset"]], (square_size*2, square_size*2))
    window.blit(board_asset, (pygame.display.Info().current_w/2 - square_size, 4*pygame.display.Info().current_h/13))