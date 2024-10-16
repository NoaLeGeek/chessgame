import pygame
import os

def load_image(filepath: str, width: int, height: int):
    return pygame.transform.scale(pygame.image.load(filepath), (width, height))

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

def get_position(x: int, y: int, margin, square_size) -> tuple[int, int]:
    return (y - margin) // square_size, (x - margin) // square_size

def flip_coords(*args, **kwds) -> tuple[int, int] | int:
    coords = [get_value(kwds["flipped"], arg, 7 - arg) for arg in args] if kwds else tuple([7 - arg for arg in args])
    return coords[0] if len(coords) == 1 else coords

def load_image(path:str, size:tuple[int, int]):
    return pygame.transform.scale(pygame.image.load(path), size)

#TODO changer new_assets to assets
def generate_piece_images(asset:str, tile_size:int):
    # TODO paramètres : activer le fait que les noirs soit retournés de 180°, flipped_assets
    images = dict()
    for file in os.listdir(os.path.join('new_assets', 'piece', asset)):
        filepath = os.path.join('new_assets', 'piece', asset, file)
        notation = os.path.splitext(file)[0]
        images[notation] = load_image(filepath, (tile_size, tile_size))
        # pygame.transform.rotate(image, 180)
    return images

def generate_board_image(asset:str, tile_size:int):
    filepath = os.path.join('new_assets', 'board', asset + '.jpg')
    return load_image(filepath, (tile_size * 8, tile_size * 8))

def generate_background_image(asset:str, size:tuple[int, int]):
    filepath = os.path.join('new_assets', 'background', asset + '.png')
    return load_image(filepath, size)

# TODO voler les sons de lichess
def generate_sounds(asset:str):
    sounds = dict()
    for sound in os.listdir(os.path.join('new_assets', 'sound', asset)):
        filepath = os.path.join('new_assets', 'sound', asset, sound)
        name = os.path.splitext(sound)[0]
        sounds[name] = load_sound(filepath)
    return sounds

def play_sound(sounds, type: str):
    sounds[type].play()