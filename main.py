import pygame
import os
import random

from Game import Game
from Board import Board
from constants import *


def get_position(x, y):
    return x // square_size, y // square_size


def main():
    pygame.init()
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((width, height))
    run = True
    game_over = False
    turn = "white"
    fps = 60
    game = Game(width, height, rows, columns, square_size, window)
    while run:
        clock.tick(fps)
        game.update_window()
        game_over = game.check_game()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE and game_over:
                    game.reset(window)
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if pygame.mouse.get_pressed()[0]:
                    location = pygame.mouse.get_pos()
                    row, column = get_position(location[0], location[1])
                    game.select(row, column)


if __name__ == "__main__":
    main()
