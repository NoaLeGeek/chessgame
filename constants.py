import os
import pygame
import json

from math import floor

def get_position(x: int, y: int):
    return (y - config["margin"]) // square_size, (x - config["margin"]) // square_size

def flip_coords(*args, **kwds):
    coords = [get_value(kwds["flipped"], arg, 7 - arg) for arg in args] if kwds else tuple([7 - arg for arg in args])
    return coords[0] if len(coords) == 1 else coords

def sign(x: int):
    return (x >= 0) - (x < 0)

def get_value(flipped: bool, white_value: int, black_value: int):
    return (white_value * (flipped + 1) + black_value * (1 - flipped)) // 2

def generate_images(asset: str):
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

def generate_sounds(asset: str):
    return {(asset, sound): pygame.mixer.Sound(os.path.join("assets", "sounds", asset, sound + ".ogg")) for sound in types_sound_asset}

def generate_board(asset: str):
    return pygame.transform.scale(pygame.image.load(os.path.join("assets", "boards", asset + ".png")), (square_size*8, square_size*8))

pygame.init()
pygame.display.set_caption("Chesspy")
pygame.mixer.init()
#TODO config volume
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
game_modes = ["classic", "koth", "+3_checks", "giveaway", "960"]
window = pygame.display.set_mode((config["height"],) * 2, pygame.RESIZABLE)
square_size = floor((config["height"] - 2 * config["margin"]) / config["columns"])

available_board_assets = ["green", "checkers", "8_bit", "dark_wood", "glass", "brown", "icy_sea", "newspaper", "walnut", "sky", "lolz", "stone", "bases", "marble", "purple", "translucent", "metal", "tournament", "dash", "burled_wood", "blue", "bubblegum", "graffiti", "light", "neon", "orange", "overlay", "parchment", "red", "sand", "tan"]
board_assets = {config["selected_board_asset"]: generate_board(config["selected_board_asset"])}

available_piece_assets = ["blindfold", "lichess", "chesscom", "fancy", "warrior", "wood", "game_room", "glass", "gothic", "classic", "metal", "bases", "neo_wood", "icy_sea", "club", "ocean", "newspaper", "space", "cases", "condal", "8_bit", "marble", "book", "alpha", "bubblegum", "dash", "graffiti", "light", "lolz", "luca", "maya", "modern", "nature", "neon", "sky", "tigers", "tournament", "vintage", "3d_wood", "3d_staunton", "3d_plastic", "3d_chesskid"]
piece_assets = {config["selected_piece_asset"]: generate_images(config["selected_piece_asset"])} if config["selected_piece_asset"] != "blindfold" else {}

available_background_assets = ["standard", "game_room", "classic", "light", "wood", "glass", "tournament", "staunton", "newspaper", "tigers", "nature", "sky", "cosmos", "ocean", "metal", "gothic", "marble", "neon", "graffiti", "bubblegum", "lolz", "8_bit", "bases", "blues", "dash", "icy_sea", "walnut"]
background_assets = {config["selected_background_asset"]: pygame.transform.scale(pygame.image.load(os.path.join("assets", "backgrounds", config["selected_background_asset"] + ".png")), (config["width"], config["height"]))}

available_sound_assets = ["beat", "default", "lolz", "marble", "metal", "nature", "newspaper", "silly", "space"]
types_sound_asset = ["capture", "castle", "game-start", "game-end", "move-check", "move-opponent", "move-self", "premove", "promote"]
sound_assets = {("all", sound): pygame.mixer.Sound(os.path.join("assets", "sounds", sound + ".ogg")) for sound in ["illegal", "notify", "tenseconds"]}
sound_assets.update(generate_sounds(config["selected_sound_asset"]))