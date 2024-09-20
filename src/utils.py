from Board.pieces import *
import pygame
import os

# TODO créer une fonction qui load un filepath

def notation_to_piece(notation:str):
    return {'P':Pawn, 'K':King, 'R':Rook, 'B':Bishop, 'N':Knight, 'Q':Queen}[notation]

def get_position(x: int, y: int, margin) -> tuple[int, int]:
    return (y - margin) // square_size, (x - margin) // square_size

def flip_coords(*args, **kwds) -> tuple[int, int] | int:
    coords = [get_value(kwds["flipped"], arg, 7 - arg) for arg in args] if kwds else tuple([7 - arg for arg in args])
    return coords[0] if len(coords) == 1 else coords

def load_image(path:str, size:tuple[int, int]):
    return pygame.transform.scale(pygame.image.load(path), size)

def generate_piece_images(asset:str, tile_size:int):
    images = {1:{}, -1:{}}
    for file in os.listdir(os.path.join('assets', 'pieces', asset)):
        path = os.path.join('assets', 'pieces', asset, file)
        notation = os.path.splitext(file)[0]
        images[-1][notation] = load_image(path, (tile_size, tile_size))
        images[1][notation] = pygame.transform.rotate(load_image(path, (tile_size, tile_size)), 180)
    return images

