import pygame
import random
import GUI

from Game import Game
from Pieces import *
from constants import *
from Menu import MAIN_MENU, CHOOSE_GAME_MODE_MENU, menus
from Config import change_background, change_board, change_piece, change_sound

def main():
    run = True
    game_over = False
    fps = 60
    game = None
    while run:
        clock.tick(fps)
        GUI.draw_background()
        match config["state"]:
            case "main_menu":
                MAIN_MENU.draw_menu()
            case "choose_game_mode":
                CHOOSE_GAME_MODE_MENU.draw_menu()
            case "game":
                game.update_window()
        pygame.display.update()
        game_over = False
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                if pygame.display.Info().current_h != config["height"]:
                    pygame.display.set_mode((pygame.display.Info().current_w, config["height"]), pygame.RESIZABLE)
                if pygame.display.Info().current_w > config["width"]:
                    pygame.display.set_mode((config["width"], pygame.display.Info().current_h), pygame.RESIZABLE)
                if pygame.display.Info().current_w < config["height"]:
                    pygame.display.set_mode((config["height"], pygame.display.Info().current_h), pygame.RESIZABLE)
                for menu in menus:
                    menu.refresh()
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.reset()
                if config["state"] == "game":
                    if event.key == pygame.K_f:
                        game.flip_board()
                        game.flip_game()
                    if event.key == pygame.K_c:
                        change_piece(game.board, random.choice(available_piece_assets))
                        change_background(random.choice(available_background_assets))
                        change_sound(random.choice(available_sound_assets))
                        change_board(random.choice(available_board_assets))
            #if game.turn == -1:
                #randomPiece = random.choice(list(filter(lambda p: len(p.get_available_moves(game.get_board().board, p.row, p.column)) != 0, game.get_color_pieces(game.turn))))
                #game.select(randomPiece.row, randomPiece.column)
                #randomMove = random.choice(randomPiece.get_available_moves(game.get_board().board, randomPiece.row, randomPiece.column))
                #game.select(randomMove[0], randomMove[1])
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                # Left click
                if pygame.mouse.get_pressed()[0]:
                    match config["state"]:
                        case "main_menu":
                            if MAIN_MENU.buttons[0].is_clicked():
                                config["state"] = "choose_game_mode"
                            if MAIN_MENU.buttons[1].is_clicked():
                                game.state = "settings"
                            if MAIN_MENU.buttons[3].is_clicked():
                                run = False
                                pygame.quit()
                        case "choose_game_mode":
                            for i in range(len(CHOOSE_GAME_MODE_MENU.buttons)):
                                if CHOOSE_GAME_MODE_MENU.buttons[i].is_clicked():
                                    config["state"] = "game"
                                    game = Game(game_modes[i])
                        case "game":
                            row, column = get_position(*pygame.mouse.get_pos())
                            if 0 <= row < len(game.board) and 0 <= column < len(game.board[row]):
                                selected_piece = game.board[row][column]
                                print("clicked on:", selected_piece if selected_piece != 0 else 0)
                                print("cRow", row, "cColumn", column)
                                if selected_piece != 0 and isinstance(selected_piece, King):
                                    print("kingmoves", selected_piece.get_available_moves(game.board, row, column, game.flipped, en_passant=game.en_passant))
                                #if game.turn == 1:
                                game.select(row, column)
                            game.highlightedSquares = {}
                # Right click
                elif pygame.mouse.get_pressed()[2]:
                    if config["state"] == "game":
                        row, column = get_position(*pygame.mouse.get_pos())
                        if 0 <= row < len(game.board) and 0 <= column < len(game.board[row]):
                            game.selected, game.valid_moves, keys = None, [], pygame.key.get_pressed()
                            highlight = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) + (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) * 2
                            if game.highlightedSquares.get((row, column)) != highlight:
                                game.highlightedSquares[(row, column)] = highlight
                            else:
                                game.highlightedSquares.pop((row, column), None)


if __name__ == "__main__":
    main()