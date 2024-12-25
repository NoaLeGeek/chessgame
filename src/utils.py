import pygame
import os
from config import config

def load_sound(filepath: str):
    return pygame.mixer.Sound(filepath)

def sign(x: int) -> int:
    return (x >= 0) - (x < 0)

def left_click() -> bool:
    return bool(pygame.mouse.get_pressed()[0])

def right_click() -> bool:
    return bool(pygame.mouse.get_pressed()[2])

def get_value(flipped: bool, white_value: int, black_value: int) -> int:
    return white_value if flipped == 1 else black_value

def get_position(x: int, y: int) -> tuple[int, int]:
    return (y - config.margin) // config.tile_size, (x - config.margin) // config.tile_size

def flip_coords(*args, **kwds) -> tuple[int, int] | int:
    coords = [get_value(kwds["flipped"], arg, 7 - arg) for arg in args] if kwds else tuple([7 - arg for arg in args])
    return coords[0] if len(coords) == 1 else coords

def load_image(path: str, size: tuple[int, int] = None):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, size) if size else image

#TODO changer new_assets to assets
def generate_piece_images():
    # TODO paramètres : activer le fait que les noirs soit retournés de 180°, flipped_assets
    images = dict()
    for file in os.listdir(os.path.join('new_assets', 'piece', config.piece_asset)):
        filepath = os.path.join('new_assets', 'piece', config.piece_asset, file)
        notation = os.path.splitext(file)[0]
        images[notation] = load_image(filepath, (config.tile_size, config.tile_size))
        # pygame.transform.rotate(image, 180)
    return images

def generate_board_image():
    filepath = os.path.join('new_assets', 'board', config.board_asset + '.jpg')
    return load_image(filepath, (config.tile_size * 8, config.tile_size * 8))

def generate_background_image():
    filepath = os.path.join('new_assets', 'background', config.background_asset + '.png')
    return load_image(filepath, (config.width, config.height))

# TODO voler les sons de lichess
def generate_sounds():
    sounds = dict()
    for sound in os.listdir(os.path.join('new_assets', 'sound', config.sound_asset)):
        filepath = os.path.join('new_assets', 'sound', config.sound_asset, sound)
        name = os.path.splitext(sound)[0]
        sounds[name] = load_sound(filepath)
    return sounds