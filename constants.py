import os
import pygame
import json
from math import floor


def generate_images(asset: str):
    images = []
    for piece in piece_constants:
        image = pygame.image.load(os.path.join("assets", ("white" if piece.startswith("w") else "black") + "Pieces", asset, piece + ".png"))
        size = (square_size * 7/8, square_size * 7/8)
        if asset in ["lichess"]:
            size = ((square_size * 5 / 8, square_size * 3 / 4) if piece.endswith("P") else (square_size * 3 / 4, square_size * 3 / 4))
        if asset in ["3d_chesskid", "3d_plastic", "3d_staunton", "3d_wood"]:
            size = (square_size, image.get_height() * square_size / image.get_width())
        if asset in ["fancy"]:
            size = (square_size * 3 / 4, square_size * 3 / 4)
        images.append(pygame.transform.scale(image, size))
    return images


pygame.init()
with open("config.json", "r") as file:
    config = json.load(file)
# Chess without 8x8 board is not supported actually
if config["rows"] != 8 or config["columns"] != 8 or config["rows"] != config["columns"]:
    raise ValueError("Rows and columns must be 8 and equal to each other.")
for key in list(config.keys()):
    match key:
        case "taskbar_height":
            taskbar_height = config[key] if config[key] else 48
        case "rows":
            rows = config[key] if config[key] else 8
        case "columns":
            columns = config[key] if config[key] else 8
        case "margin":
            margin = config[key] if config[key] else 16
        case "board_asset":
            board_asset = config[key] if config[key] else "green"
        case "pieces_asset":
            pieces_asset = config[key] if config[key] else "chesscom"
        case "background_asset":
            background_asset = config[key] if config[key] else "standard"
        case "width":
            width = config[key] if config[key] else pygame.display.Info().current_w
        case "height":
            height = config[key] if config[key] else pygame.display.Info().current_h - 23 - taskbar_height
clock = pygame.time.Clock()
# Piece images are stored in the following order: pawn, knight, bishop, rook, queen, king. White pieces come first.
piece_constants = [color + type for color in ["w", "b"] for type in ["P", "N", "B", "R", "Q", "K"]]
window = pygame.display.set_mode((height, height), pygame.RESIZABLE)
square_size = floor((height - 2*margin) / columns)
# ["green", "checkers", "8_bit", "dark_wood", "glass", "brown", "icy_sea", "newspaper", "walnut", "sky", "lolz", "stone", "bases", "marble", "purple", "translucent", "metal", "tournament", "dash", "burled_wood", "blue", "bubblegum", "graffiti", "light", "neon", "orange", "overlay", "parchment", "red", "sand", "tan"]
board_assets = {board_asset: pygame.transform.scale(pygame.image.load(os.path.join("assets", "boards", board_asset + ".png")), (square_size*8, square_size*8))}
# ["lichess", "chesscom", "fancy", "warrior", "wood", "game_room", "glass", "gothic", "classic", "metal", "bases", "neo_wood", "icy_sea", "club", "ocean", "newspaper", "space", "cases", "condal", "8_bit", "marble", "book", "alpha", "bubblegum", "dash", "graffiti", "light", "lolz", "luca", "maya", "modern", "nature", "neon", "sky", "tigers", "tournament", "vintage", "3d_wood", "3d_staunton", "3d_plastic", "3d_chesskid"]
piece_assets = {pieces_asset: generate_images(pieces_asset)}
# ["standard", "game_room", "classic", "light", "wood", "glass", "tournament", "staunton", "newspaper", "tigers", "nature", "sky", "cosmos", "ocean", "metal", "gothic", "marble", "neon", "graffiti", "bubblegum", "lolz", "8_bit", "bases", "blues", "dash", "icy_sea", "walnut"]
background_assets = {background_asset: pygame.transform.scale(pygame.image.load(os.path.join("assets", "backgrounds", background_asset + ".png")), (width, height))}

