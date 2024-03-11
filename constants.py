import os
import pygame
import random
from win32api import GetMonitorInfo, MonitorFromPoint


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


taskbar_height = GetMonitorInfo(MonitorFromPoint((0,0))).get("Monitor")[3] - GetMonitorInfo(MonitorFromPoint((0,0))).get("Work")[3]
pygame.init()
clock = pygame.time.Clock()
width, height = pygame.display.Info().current_w, pygame.display.Info().current_h - 23 - taskbar_height
window = pygame.display.set_mode((height, height), pygame.RESIZABLE)
rows, columns = 8, 8
margin = 5
square_size = height // columns
tile_assets = {tile_asset: pygame.transform.scale(pygame.image.load(os.path.join("assets", "boards", tile_asset + ".png")), (height, height)) for tile_asset in ["green", "checkers", "8_bit", "dark_wood", "glass", "brown", "icy_sea", "newspaper", "walnut", "sky", "lolz", "stone", "bases", "marble", "purple", "translucent", "metal", "tournament", "dash", "burled_wood", "blue", "bubblegum", "graffiti", "light", "neon", "orange", "overlay", "parchment", "red", "sand", "tan"]}
# Piece images are stored in the following order: pawn, knight, bishop, rook, queen, king. White pieces come first.
piece_constants = [color + type for color in ["w", "b"] for type in ["P", "N", "B", "R", "Q", "K"]]
piece_assets = {piece_asset: generate_images(piece_asset) for piece_asset in ["lichess", "chesscom", "fancy", "warrior", "wood", "game_room", "glass", "gothic", "classic", "metal", "bases", "neo_wood", "icy_sea", "club", "ocean", "newspaper", "space", "cases", "condal", "8_bit", "marble", "book", "alpha", "bubblegum", "dash", "graffiti", "light", "lolz", "luca", "maya", "modern", "nature", "neon", "sky", "tigers", "tournament", "vintage", "3d_wood", "3d_staunton", "3d_plastic", "3d_chesskid"]}
selected_tile_asset = "checkers"
selected_asset = "lichess"

