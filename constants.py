import os
import pygame
import json

from math import floor

def get_position(x: int, y: int) -> tuple[int, int]:
    """
    Converts pixel coordinates to board coordinates.

    Args:
        x (int): The x-coordinate in pixels.
        y (int): The y-coordinate in pixels.

    Returns:
        tuple: A tuple containing the row and column indices on the chessboard.
    """
    return (y - config["margin"]) // square_size, (x - config["margin"]) // square_size

def flip_coords(*args, **kwds) -> tuple[int, int] | int:
    """
    Flips the given coordinates based on the 'flipped' keyword argument.

    Args:
        *args: The coordinates to be flipped.
        **kwds: Optional keyword arguments.
            - flipped (bool): If True, the coordinates will be flipped. If False, the coordinates will not be flipped.
        If no keyword arguments are provided, the coordinates will be flipped.

    Returns:
        tuple or int: The flipped coordinates. If only one coordinate is provided, an int is returned. Otherwise, a tuple is returned.
    """
    coords = [get_value(kwds["flipped"], arg, 7 - arg) for arg in args] if kwds else tuple([7 - arg for arg in args])
    return coords[0] if len(coords) == 1 else coords

def sign(x: int) -> int:
    """
    Returns the sign of a number.

    Args:
        x (int): The number to determine the sign of.

    Returns:
        int: -1 for x ∈ ]-∞;0[, 1 if x ∈ [0;+∞[.
    """
    return (x >= 0) - (x < 0)

def get_value(flipped: bool, white_value: int, black_value: int) -> int:
    """
    Returns the value based on the flipped flag.

    Parameters:
    flipped (bool): A flag indicating if the board is flipped.
    white_value (int): The value to return if the board is not flipped.
    black_value (int): The value to return if the board is flipped.

    Returns:
    int: The value based on the flipped flag.
    """
    return white_value if flipped == 1 else black_value

def left_click() -> bool:
    """
    Check if the left mouse button is currently being clicked.

    Returns:
        bool: True if the left mouse button is being clicked, False otherwise.
    """
    return bool(pygame.mouse.get_pressed()[0])

def right_click() -> bool:
    """
    Check if the right mouse button is currently being clicked.

    Returns:
        bool: True if the right mouse button is being clicked, False otherwise.
    """
    return bool(pygame.mouse.get_pressed()[2])

def generate_pieces(asset: str) -> list[pygame.Surface]:
    """
    Generate a list of images for chess pieces based on the given asset.

    Parameters:
    asset (str): The asset type for the chess pieces.

    Returns:
    list: A list of pygame.Surface objects representing the chess piece images.
    """
    images = []
    for piece in piece_constants:
        image = pygame.image.load(os.path.join("assets", ("white" if piece.startswith("w") else "black") + "Pieces", asset, piece + ".png"))
        size = (square_size * 7/8, square_size * 7/8)
        if asset in ["lichess"]:
            size = (square_size * 3 / 4, square_size * 3 / 4)
            if piece.endswith("P"):
                size = (square_size * 5 / 8, square_size * 3 / 4)
        if asset.startswith("3d"):
            size = (square_size, image.get_height() * square_size / image.get_width())
        if asset in ["fancy"]:
            size = (square_size * 3 / 4, square_size * 3 / 4)
        images.append(pygame.transform.scale(image, size))
    return images

def generate_sounds(asset: str) -> dict:
    """
    Generate a dictionary of sounds for a given asset.

    Args:
        asset (str): The name of the asset.

    Returns:
        dict: A dictionary containing the sounds for the asset.
    """
    return {(asset, sound): pygame.mixer.Sound(os.path.join("assets", "sounds", asset, sound + ".ogg")) for sound in types_sound_asset}

def generate_board(asset: str) -> pygame.Surface:
    """
    Generate a chessboard image based on the specified asset.

    Parameters:
    asset (str): The name of the asset to use for the chessboard.

    Returns:
    pygame.Surface: The generated chessboard image.

    """
    return pygame.transform.scale(pygame.image.load(os.path.join("assets", "boards", asset + ".png")), (square_size*8, square_size*8))

BROWN = (92, 64, 51)
WHITE = (255, 255, 255)

pygame.init()
pygame.display.set_caption("Chesspy")
pygame.mixer.init()
pygame.mixer.music.set_volume(0.2)
clock = pygame.time.Clock()

config = {"volume": 0.2,
          "taskbar_height": 48,
          "rows": 8,
          "columns": 8,
          "margin": 32,
          "selected_board_asset": "green",
          "selected_piece_asset": "chesscom",
          "selected_background_asset": "standard",
          "selected_sound_asset": "default",
          "state": "main_menu",
          "width": pygame.display.Info().current_w,
          "height": pygame.display.Info().current_h - 23 - 48}
# Load the configuration from the config.json file
with open("config.json", "r") as file:
        data = json.load(file)
        # Chess without 8x8 board is not supported actually
        if data["rows"] != 8 or data["columns"] != 8 or data["rows"] != data["columns"]:
            raise ValueError("Rows and columns must be 8 and equal to each other.")
        for key in data.keys():
            if key in config.keys():
                config[key] = data[key]

# Piece images are stored in the following order: pawn, knight, bishop, rook, queen, king. White pieces come first.
piece_constants = [color + type for color in ["w", "b"] for type in ["P", "N", "B", "R", "Q", "K"]]
# The different gamemodes available in the game
gamemodes = ["Classic", "KOTH", "+3 Checks", "Giveaway", "Chess960"]
window = pygame.display.set_mode((config["height"],) * 2, pygame.RESIZABLE)
square_size = floor((config["height"] - 2 * config["margin"]) / config["columns"])

# The different assets available for the game
available_board_assets = ["green", "checkers", "8_bit", "dark_wood", "glass", "brown", "icy_sea", "newspaper", "walnut", "sky", "lolz", "stone", "bases", "marble", "purple", "translucent", "metal", "tournament", "dash", "burled_wood", "blue", "bubblegum", "graffiti", "light", "neon", "orange", "overlay", "parchment", "red", "sand", "tan"]
board_assets = {config["selected_board_asset"]: generate_board(config["selected_board_asset"])}

# The different assets available for the chess pieces
available_piece_assets = ["blindfold", "lichess", "chesscom", "fancy", "warrior", "wood", "game_room", "glass", "gothic", "classic", "metal", "bases", "neo_wood", "icy_sea", "club", "ocean", "newspaper", "space", "cases", "condal", "8_bit", "marble", "book", "alpha", "bubblegum", "dash", "graffiti", "light", "lolz", "luca", "maya", "modern", "nature", "neon", "sky", "tigers", "tournament", "vintage", "3d_wood", "3d_staunton", "3d_plastic", "3d_chesskid"]
piece_assets = {config["selected_piece_asset"]: generate_pieces(config["selected_piece_asset"])} if config["selected_piece_asset"] != "blindfold" else {}

# The different assets available for the background
available_background_assets = ["standard", "game_room", "classic", "light", "wood", "glass", "tournament", "staunton", "newspaper", "tigers", "nature", "sky", "cosmos", "ocean", "metal", "gothic", "marble", "neon", "graffiti", "bubblegum", "lolz", "8_bit", "bases", "blues", "dash", "icy_sea", "walnut"]
background_assets = {config["selected_background_asset"]: pygame.transform.scale(pygame.image.load(os.path.join("assets", "backgrounds", config["selected_background_asset"] + ".png")), (config["width"], config["height"]))}

# The different assets available for the sounds
available_sound_assets = ["beat", "default", "lolz", "marble", "metal", "nature", "newspaper", "silly", "space"]
types_sound_asset = ["capture", "castle", "game-start", "game-end", "move-check", "move-opponent", "move-self", "premove", "promote"]
sound_assets = {("all", sound): pygame.mixer.Sound(os.path.join("assets", "sounds", sound + ".ogg")) for sound in ["illegal", "notify", "tenseconds"]}
sound_assets.update(generate_sounds(config["selected_sound_asset"]))