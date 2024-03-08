import random
import constants
import pygame
import os

from Game import Game
from Pieces import *


def get_position(x, y):
    return y // constants.square_size, x // constants.square_size

def main():
    run = True
    game_over = False
    fps = 60
    game = Game(constants.width, constants.height, constants.rows, constants.columns, constants.window)
    while run:
        constants.clock.tick(fps)
        game.update_window()
        game_over = game.check_game()
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                if pygame.display.Info().current_h != constants.height:
                    pygame.display.set_mode((pygame.display.Info().current_w, constants.height), pygame.RESIZABLE)
                if pygame.display.Info().current_w > constants.width:
                    pygame.display.set_mode((constants.width, pygame.display.Info().current_h), pygame.RESIZABLE)
                if pygame.display.Info().current_w < constants.height:
                    pygame.display.set_mode((constants.height, pygame.display.Info().current_h), pygame.RESIZABLE)
            if game_over or event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.reset(constants.window)
            #if game.turn == -1:
                #randomPiece = random.choice(list(filter(lambda p: len(p.get_available_moves(game.get_board().board, p.row, p.column)) != 0, game.get_color_pieces(game.turn))))
                #game.select(randomPiece.row, randomPiece.column)
                #randomMove = random.choice(randomPiece.get_available_moves(game.get_board().board, randomPiece.row, randomPiece.column))
                #game.select(randomMove[0], randomMove[1])
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                # Left click
                if pygame.mouse.get_pressed()[0]:
                    location = pygame.mouse.get_pos()
                    row, column = get_position(location[0], location[1])
                    selected_piece = game.get_board().board[row][column]
                    print("clicked on:", selected_piece if selected_piece != 0 else 0)
                    print("cRow", row, "cColumn", column)
                    if selected_piece != 0:
                        pass
                        # print("avaible moves:", selected_piece.get_available_moves(game.get_board().board, row, column))
                    #if game.turn == 1:
                    game.select(row, column)
                    game.highlightedSquares = {}
                # Right click
                elif pygame.mouse.get_pressed()[2]:
                    row, column = get_position(*pygame.mouse.get_pos())
                    game.selected, game.valid_moves, keys = None, [], pygame.key.get_pressed()
                    highlight = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) + (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) * 2
                    if game.highlightedSquares.get((row, column)) != highlight:
                        game.highlightedSquares[(row, column)] = highlight
                    else:
                        game.highlightedSquares.pop((row, column), None)
                    #print(constants.selected_asset)
                    #constants.selected_asset = random.choice(["lichess", "simple", "fancy", "medieval", "warrior", "default"])
                    # TODO when user will change skin, this will be useful, you have to recenter the pieces
                    #for i in range(8):
                        #for j in range(8):
                            #piece = game.get_board().board[i][j]
                            #if piece != 0:
                                #piece.image = constants.piece_assets[constants.selected_asset][test[type(piece)] + (0 if piece.color == 1 else 6)]


if __name__ == "__main__":
    main()