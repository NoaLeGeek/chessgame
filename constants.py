import os
import pygame
from win32api import GetMonitorInfo, MonitorFromPoint


def generate_images(asset: str):
    return [pygame.transform.scale(pygame.image.load(os.path.join("assets", ("white" if piece.startswith("w") else "black") + "Pieces", asset, piece + ".png")), (square_size * 5 / 8, square_size * 3 / 4) if piece.endswith("P") and asset in ["lichess"] else (square_size * 3 / 4, square_size * 3 / 4)) for piece in piece_constants]


taskbar_height = GetMonitorInfo(MonitorFromPoint((0,0))).get("Monitor")[3] - GetMonitorInfo(MonitorFromPoint((0,0))).get("Work")[3]
pygame.init()
clock = pygame.time.Clock()
width, height = pygame.display.Info().current_w, pygame.display.Info().current_h - 23 - taskbar_height
window = pygame.display.set_mode((height, height), pygame.RESIZABLE)
rows, columns = 8, 8
square_size = height // columns
tile_assets = {"brown": ((237, 214, 176), (184, 135, 98)),
               "green": ((233, 237, 204), (119, 153, 84)),
               "sky": ((240, 241, 240), (196, 216, 228)),
               "8-bit": ((243, 243, 244), (106, 155, 65)),
               "purple": ((240, 241, 240), (132, 118, 186)),
               "blue": ((234, 233, 210), (75, 115, 153)),
               "bubblegum": ((254, 255, 254), (251, 217, 225)),
               "checkers": ((199, 76, 81), (48, 48, 48)),
               "light": ((216, 217, 216), (168, 169, 168)),
               "orange": ((250, 228, 174), (209, 136, 21)),
               "red": ((245, 219, 195), (187, 87, 70)),
               "tan": ((237, 203, 165), (216, 164, 109))}
# Piece images are stored in the following order: pawn, knight, bishop, rook, queen, king. White pieces come first.
piece_constants = ["wP", "wN", "wB", "wR", "wQ", "wK", "bP", "bN", "bB", "bR", "bQ", "bK"]
# TODO maybe a function to generate images because that's repeating
piece_assets = {piece_asset: generate_images(piece_asset) for piece_asset in ["lichess", "chesscom", "simple", "fancy", "medieval", "warrior", "default"]}
selected_tile_asset = "brown"
selected_asset = "chesscom"
