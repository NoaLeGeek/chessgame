import os
import pygame
import json
from math import floor
import time


def get_position(x, y):
    return (y - margin) // square_size, (x - margin) // square_size


def draw_text(frame, text, color, size, center):
    text_surface = pygame.font.SysFont("comicsansms", size).render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = center
    frame.blit(text_surface, text_rect)


def flip_coords(*args, **kwds):
    coords = [((7 - 2 * arg) * kwds["flipped"] + 7) // 2 for arg in args] if kwds else tuple([7 - arg for arg in args])
    return coords[0] if len(coords) == 1 else coords


def generate_images(asset: str):
    images = []
    for piece in piece_constants:
        image = pygame.image.load(os.path.join("assets", ("white" if piece.startswith("w") else "black") + "Pieces", asset, piece + ".png"))
        size = (square_size * 7/8, square_size * 7/8)
        if asset in ["lichess"]:
            size = (square_size * (6 - int(piece.endswith("P"))) / 8, square_size * 3 / 4)
        if asset.startswith("3d"):
            size = (square_size, image.get_height() * square_size / image.get_width())
        if asset in ["fancy"]:
            size = (square_size * 3 / 4, square_size * 3 / 4)
        images.append(pygame.transform.scale(image, size))
    return images


pygame.init()
pygame.display.set_caption("Chesspy")
pygame.mixer.init()
#TODO config volume
pygame.mixer.music.set_volume(0.2)
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
        case "selected_board_asset":
            selected_board_asset = config[key] if config[key] else "green"
        case "selected_piece_asset":
            selected_piece_asset = config[key] if config[key] else "chesscom"
        case "selected_background_asset":
            selected_background_asset = config[key] if config[key] else "standard"
        case "selected_sound_asset":
            selected_sound_asset = config[key] if config[key] else "default"
        case "width":
            width = config[key] if config[key] else pygame.display.Info().current_w
        case "height":
            height = config[key] if config[key] else pygame.display.Info().current_h - 23 - taskbar_height
clock = pygame.time.Clock()
# Piece images are stored in the following order: pawn, knight, bishop, rook, queen, king. White pieces come first.
piece_constants = [color + type for color in ["w", "b"] for type in ["P", "N", "B", "R", "Q", "K"]]
window = pygame.display.set_mode((height, height), pygame.RESIZABLE)
square_size = floor((height - 2 * margin) / columns)
available_board_assets = ["green", "checkers", "8_bit", "dark_wood", "glass", "brown", "icy_sea", "newspaper", "walnut", "sky", "lolz", "stone", "bases", "marble", "purple", "translucent", "metal", "tournament", "dash", "burled_wood", "blue", "bubblegum", "graffiti", "light", "neon", "orange", "overlay", "parchment", "red", "sand", "tan"]
board_assets = {selected_board_asset: pygame.transform.scale(pygame.image.load(os.path.join("assets", "boards", selected_board_asset + ".png")), (square_size*8, square_size*8))}
available_piece_assets = ["blindfold", "lichess", "chesscom", "fancy", "warrior", "wood", "game_room", "glass", "gothic", "classic", "metal", "bases", "neo_wood", "icy_sea", "club", "ocean", "newspaper", "space", "cases", "condal", "8_bit", "marble", "book", "alpha", "bubblegum", "dash", "graffiti", "light", "lolz", "luca", "maya", "modern", "nature", "neon", "sky", "tigers", "tournament", "vintage", "3d_wood", "3d_staunton", "3d_plastic", "3d_chesskid"]
piece_assets = {selected_piece_asset: generate_images(selected_piece_asset)} if selected_piece_asset != "blindfold" else {}
available_background_assets = ["standard", "game_room", "classic", "light", "wood", "glass", "tournament", "staunton", "newspaper", "tigers", "nature", "sky", "cosmos", "ocean", "metal", "gothic", "marble", "neon", "graffiti", "bubblegum", "lolz", "8_bit", "bases", "blues", "dash", "icy_sea", "walnut"]
background_assets = {selected_background_asset: pygame.transform.scale(pygame.image.load(os.path.join("assets", "backgrounds", selected_background_asset + ".png")), (width, height))}
available_sound_assets = ["beat", "default", "lolz", "marble", "metal", "nature", "newspaper", "silly", "space"]
sound_assets = {sound: pygame.mixer.Sound(os.path.join("assets", "sounds", sound + ".ogg")) for sound in ["illegal", "notify", "tenseconds"]}
sound_assets.update({selected_sound_asset: [pygame.mixer.Sound(os.path.join("assets", "sounds", selected_sound_asset, sound + ".ogg")) for sound in ["capture", "castle", "game-start", "game-end", "move-check", "move-opponent", "move-self", "premove", "promote"]]})