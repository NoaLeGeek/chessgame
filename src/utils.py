import pygame
import os
from config import config

def load_sound(filepath: str):
    sound = pygame.mixer.Sound(filepath)
    sound.set_volume(config.volume)
    return sound 

def sign(x: int) -> int:
    return (x >= 0) - (x < 0)

def left_click() -> bool:
    return bool(pygame.mouse.get_pressed()[0])

def right_click() -> bool:
    return bool(pygame.mouse.get_pressed()[2])

def get_value(flipped: int, white_value: int, black_value: int) -> int:
    if flipped not in (-1, 1):
        raise ValueError("flipped must be -1 or 1, not " + str(flipped))
    if flipped == 1:
        return white_value
    elif flipped == -1:
        return black_value

def get_pos(coord: tuple[int, int]) -> tuple[int, int]:
    x, y = coord
    return (y - config.margin) // config.tile_size, (x - config.margin - config.eval_bar_width) // config.tile_size

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

def resize_image(image, size):
    return pygame.transform.scale(image, (size))

def generate_piece_images(flipped: int = 1):
    images = dict()
    for file in os.listdir(os.path.join('assets', 'piece', config.piece_asset)):
        filepath = os.path.join('assets', 'piece', config.piece_asset, file)
        notation = os.path.splitext(file)[0]
        image = load_image(filepath, (config.tile_size, config.tile_size))
        if config.flipped_assets and ((flipped == 1 and notation.startswith("b")) or (flipped == -1 and notation.startswith("w"))):
            image = pygame.transform.flip(image, False, True)
        images[notation] = image
    return images

def generate_board_image():
    for ext in ['jpg', 'png']:
        filepath = os.path.join('assets', 'board', f"{config.board_asset}.{ext}")
        if os.path.exists(filepath):
            return load_image(filepath, (config.tile_size * 8, config.tile_size * 8))
    raise FileNotFoundError(f"No board image found for {config.board_asset} with extensions .jpg or .png")

def generate_sounds():
    sounds = dict()
    for sound in os.listdir(os.path.join('assets', 'sound', config.sound_asset)):
        filepath = os.path.join('assets', 'sound', config.sound_asset, sound)
        name = os.path.splitext(sound)[0]
        sounds[name] = load_sound(filepath)
    custom_sounds = ['illegal', 'notify', 'tenseconds']
    sounds.update({
        name: pygame.mixer.Sound(os.path.join("assets", "sound", f"{name}.ogg"))
        for name in custom_sounds
    })
    return sounds

def play_sound(sounds: dict[str, pygame.Sound], type: str):
    """
    Play a sound of the specified type.

    Args:
        type (str): The type of sound to play, e.g., 'illegal', 'notify', etc.
        
    Raises:
        ValueError: If the specified sound type is not found in the sounds dictionary.
    """
    # Check if the sound type exists in the sounds dictionary
    if type not in sounds:
        raise ValueError(f"Sound type '{type}' not found in the sound library.")
    sounds[type].play()

def debug_print(*args):
    if config.debug:
        print(*args)
        
def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
