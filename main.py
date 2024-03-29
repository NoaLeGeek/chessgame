import constants
import pygame
import random

from Game import Game
from Pieces import *

def get_position(x, y):
    return (y - margin) // constants.square_size, (x - margin) // constants.square_size

def main():
    run = True
    game_over = False
    fps = 60
    game = Game(constants.width, constants.height, constants.rows, constants.columns, constants.window)
    while run:
        constants.clock.tick(fps)
        game.update_window()
        game_over = False
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
                if event.key == pygame.K_f:
                    game.board.flip_board()
                    game.selected, game.valid_moves = None, []
                    game.highlightedSquares = {(7 - row, 7 - column): value for ((row, column), value) in game.highlightedSquares.items()}
                if event.key == pygame.K_c:
                    game.board.change_asset(random.choice(["lichess", "chesscom", "fancy", "warrior", "wood", "game_room", "glass", "gothic", "classic", "metal", "bases", "neo_wood", "icy_sea", "club", "ocean", "newspaper", "space", "cases", "condal", "8_bit", "marble", "book", "alpha", "bubblegum", "dash", "graffiti", "light", "lolz", "luca", "maya", "modern", "nature", "neon", "sky", "tigers", "tournament", "vintage", "3d_wood", "3d_staunton", "3d_plastic", "3d_chesskid"]))
                    game.board.change_background(random.choice(["standard", "game_room", "classic", "light", "wood", "glass", "tournament", "staunton", "newspaper", "tigers", "nature", "sky", "cosmos", "ocean", "metal", "gothic", "marble", "neon", "graffiti", "bubblegum", "lolz", "8_bit", "bases", "blues", "dash", "icy_sea", "walnut"]))
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
                    if selected_piece != 0 and isinstance(selected_piece, Pawn):
                        print(selected_piece.en_passant)
                        # print("avaible moves:", selected_piece.get_available_moves(game.get_board().board, row, column))
                    #if game.turn == 1:
                    if 0 <= row < constants.rows and 0 <= column < constants.columns:
                        game.select(row, column)
                    game.highlightedSquares = {}
                # Right click
                elif pygame.mouse.get_pressed()[2]:
                    row, column = get_position(*pygame.mouse.get_pos())
                    if 0 <= row < constants.rows and 0 <= column < constants.columns: 
                        game.selected, game.valid_moves, keys = None, [], pygame.key.get_pressed()
                        highlight = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) + (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) * 2
                        if game.highlightedSquares.get((row, column)) != highlight:
                            game.highlightedSquares[(row, column)] = highlight
                        else:
                            game.highlightedSquares.pop((row, column), None)
                    #constants.selected_asset = random.choice(["lichess", "chesscom", "fancy", "medieval", "warrior", "default", "wood", "game_room", "glass", "gothic", "classic", "metal", "bases", "neo_wood", "icy_sea", "club", "ocean", "newspaper", "space", "cases", "condal", "3d_chesskid", "8_bit", "marble", "book", "alpha", "bubblegum", "dash", "graffiti", "light", "lolz", "luca", "maya", "modern", "nature", "neon", "sky", "tigers", "tournament", "vintage", "3d_wood", "3d_staunton", "3d_plastic"])


if __name__ == "__main__":
    main()