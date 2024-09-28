import pygame
import sys
import os

from math import floor
from json import load

def sign(x: int) -> int:
    return (x >= 0) - (x < 0)

def left_click() -> bool:
    return bool(pygame.mouse.get_pressed()[0])

def right_click() -> bool:
    return bool(pygame.mouse.get_pressed()[2])

def generate_pieces(asset: str) -> list[pygame.Surface]:
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
    return {(asset, sound): pygame.mixer.Sound(os.path.join("assets", "sounds", asset, sound + ".ogg")) for sound in types_sound_asset}

def generate_board(asset: str) -> pygame.Surface:
    return pygame.transform.scale(pygame.image.load(os.path.join("assets", "boards", asset + ".png")), (square_size*8, square_size*8))

BROWN = (92, 64, 51)
WHITE = (255, 255, 255)

pygame.init()
pygame.display.set_caption("Chesspy")
clock = pygame.time.Clock()

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