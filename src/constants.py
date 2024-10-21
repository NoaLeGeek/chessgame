import pygame
import os

BROWN = (92, 64, 51)
WHITE = (255, 255, 255)

# The different gamemodes available in the game
gamemodes = ["Classic", "KOTH", "+3 Checks", "Giveaway", "Chess960"]

knight_directions = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
bishop_directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
rook_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
queen_directions = bishop_directions + rook_directions