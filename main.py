import pygame
import os
import random

from Board import Board
from constants import *

clock = pygame.time.Clock()
window = pygame.display.set_mode((width, height))


def get_position(x, y):
    return x // square_size, y // square_size


def main():
    pygame.init()
    run = True
    fps = 60
    while run:
        clock.tick(fps)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    location = pygame.mouse.get_pos()
                    window.blit(pieces[list(pieces.keys())[random.randint(0, len(pieces) - 1)]],
                                (location[0] - square_size / 2, location[1] - square_size / 2))
                    row, col = get_position(location[0], location[1])


if __name__ == "__main__":
    main()
