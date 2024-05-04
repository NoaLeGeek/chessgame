import pygame
import GUI

from Game import Game
from Pieces import *
from constants import *
from random import choice
from Menu import MAIN_MENU, GAMEMODE_MENU, menus
from Config import change_background, change_board, change_piece, change_sound

def main():
    run = True
    fps = 60
    game = None
    bot_color = 0
    while run:
        clock.tick(fps)
        GUI.draw_background()
        match config["state"]:
            case "main_menu":
                MAIN_MENU.draw_menu()
            case "gamemode":
                GAMEMODE_MENU.draw_menu()
            case "opponent":
                #OPPONENT_MENU.draw_menu()
                pass
            case "game":
                game.update_window()
        pygame.display.update()
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
                        game.flip_game()
                    if event.key == pygame.K_c:
                        change_piece(game.board, choice(available_piece_assets))
                        change_background(choice(available_background_assets))
                        change_sound(choice(available_sound_assets))
                        change_board(choice(available_board_assets))
            if config["state"] == "game" and game.turn == bot_color:
                if not game.promotion:
                    randomPiece = choice(list(filter(lambda p: len(p.get_available_moves(game.board, p.row, p.column, game.flipped, en_passant = game.en_passant)) != 0, game.get_color_pieces(game.turn))))
                    game.select(randomPiece.row, randomPiece.column)
                    randomMove = choice(randomPiece.get_available_moves(game.board, randomPiece.row, randomPiece.column, game.flipped, en_passant = game.en_passant))
                    game.select(randomMove[0], randomMove[1])
                else:
                    pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Left click
                if pygame.mouse.get_pressed()[0]:
                    match config["state"]:
                        case "main_menu":
                            if MAIN_MENU.buttons[0].is_clicked():
                                config["state"] = "gamemode"
                            if MAIN_MENU.buttons[1].is_clicked():
                                config["state"] = "settings"
                            if MAIN_MENU.buttons[3].is_clicked():
                                run = False
                                pygame.quit()
                        case "gamemode":
                            for i in range(len(GAMEMODE_MENU.buttons)):
                                if GAMEMODE_MENU.buttons[i].is_clicked():
                                    config["state"] = "game"
                                    game = Game(gamemodes[i])
                                    bot_color = -1
                                    if bot_color == 1:
                                        game.flip_game()
                        case "opponent":
                            #if OPPONENT_MENU.buttons[1].is_clicked():
                                config["state"] = "game"
                                game.opponent = "randomIA"
                                
                        case "game":
                            if not game.game_over and not (game.opponent == "randomIA" and game.turn == bot_color):
                                row, column = get_position(*pygame.mouse.get_pos())
                                if 0 <= row < len(game.board) and 0 <= column < len(game.board[row]):
                                    selected_piece = game.board[row][column]
                                    print("clicked on:", selected_piece if selected_piece != 0 else 0)
                                    print("cRow", row, "cColumn", column)
                                    if selected_piece != 0 and isinstance(selected_piece, King):
                                        print("kingmoves", selected_piece.get_available_moves(game.board, row, column, game.flipped, en_passant=game.en_passant))
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