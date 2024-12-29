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

def get_value(flipped: int, white_value: int, black_value: int) -> int:
    assert flipped in (-1, 1), "flipped must be -1 or 1, not " + str(flipped)
    if flipped == 1:
        return white_value
    elif flipped == -1:
        return black_value

def get_pos(coord: tuple[int, int]) -> tuple[int, int]:
    x, y = coord
    return (y - config.margin) // config.tile_size, (x - config.margin) // config.tile_size

def flip_pos(pos: tuple[int, int] | int, flipped: int = -1) -> tuple[int, int] | int:
    # No flip if flipped = 1
    # Flip if flipped = -1
    if isinstance(pos, int):
        pos = (pos,)
    flipped_pos = [get_value(flipped, arg, 7 - arg) for arg in pos]
    if len(flipped_pos) == 1:
        return flipped_pos[0]
    return tuple(flipped_pos)

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

def get_color(highlight_color):
    r, g, b, a = None, None, None, None
    match highlight_color:
        # Right click
        case 0:
            r, g, b, a = 255, 0, 0, 75
        # Shift + Right click
        case 1:
            r, g, b, a = 0, 255, 0, 75
        # Ctrl + Right click
        case 2:
            r, g, b, a = 255, 165, 0, 75
        # History move
        case 3:
            r, g, b, a = 255, 255, 0, 75
        # Selected piece
        case 4:
            r, g, b, a = 0, 255, 255, 75
        # Void
        case None:
            r, g, b, a = 0, 0, 0, 0
    return r, g, b, a