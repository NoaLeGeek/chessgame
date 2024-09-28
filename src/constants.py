import pygame
import os

BROWN = (92, 64, 51)
WHITE = (255, 255, 255)

illegal_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "illegal.ogg"))
notify_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "notify.ogg"))
tenseconds_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "tenseconds.ogg"))

# The different gamemodes available in the game
gamemodes = ["Classic", "KOTH", "+3 Checks", "Giveaway", "Chess960"]