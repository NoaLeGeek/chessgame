import pygame
import config

from GameWish import Game
from GUI import draw_background, draw_settings
from constants import *
from Menu import MAIN_MENU, GAMEMODE_MENU, menus, SETTINGS_MENU, FEN_LABEL, MOVE_LABEL
from config import change_background, change_board, change_piece, change_sound, config_index, refresh_parameters

def main():
    run = True
    fps = 60
    game = None
    while run:
        clock.tick(fps)

        # Drawing related code
        draw_background()
        match config["state"]:
            case "main_menu":
                MAIN_MENU.draw_menu()
            case "gamemode":
                GAMEMODE_MENU.draw_menu()
            case "settings":
                SETTINGS_MENU.draw_menu()
                if config.selected_config:
                    button_index = None
                    for i, config_type in enumerate(["piece_asset", "board_asset", "sound_asset", "background_asset"]):
                        if config.selected_config == config_type:
                            button_index = i
                            break
                    SETTINGS_MENU.buttons[button_index].draw_frame()
                draw_settings()
            case "game":
                game.update_window()
                FEN_LABEL.draw()
                MOVE_LABEL.draw()
        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            match event.type:
                # Resize the window
                case pygame.VIDEORESIZE:
                    for menu in menus:
                        menu.refresh()
                # Quit the game
                case pygame.QUIT:
                    run = False  
                    pygame.quit()
                # Keyboard input
                case pygame.KEYDOWN:
                    match config["state"]:
                        case "settings":
                            if config.selected_config:
                                length = None
                                match config.selected_config:
                                    case "board_asset":
                                        length = len(available_board_assets)
                                    case "piece_asset":
                                        length = len(available_piece_assets)
                                    case "background_asset":
                                        length = len(available_background_assets)
                                    case "sound_asset":
                                        length = len(available_sound_assets)
                                if event.key == pygame.K_LEFT:
                                    config_index[config.selected_config] = (length - 1 if config_index[config.selected_config] - 1 < 0 else config_index[config.selected_config] - 1)
                                elif event.key == pygame.K_RIGHT:
                                    config_index[config.selected_config] = (config_index[config.selected_config] + 1) % length
                                match config.selected_config:
                                    case "board_asset":
                                        change_board(available_board_assets[config_index[config.selected_config]])
                                    case "piece_asset":
                                        change_piece(game.board if game else None, available_piece_assets[config_index[config.selected_config]])
                                    case "background_asset":
                                        change_background(available_background_assets[config_index[config.selected_config]])
                                    case "sound_asset":
                                        change_sound(available_sound_assets[config_index[config.selected_config]])
                                refresh_parameters()
                        case "game":
                            if event.key == pygame.K_SPACE:
                                game = Game(game.gamemode)
                                FEN_LABEL.text = game.generate_fen()
                                MOVE_LABEL.text = ""
                            if event.key == pygame.K_f:
                                game.flip_game()
                # Mouse input
                case pygame.MOUSEBUTTONDOWN:
                    if left_click():
                        match config["state"]:
                            case "main_menu":
                                if MAIN_MENU.buttons[0].is_clicked():
                                    config["state"] = "gamemode"
                                if MAIN_MENU.buttons[1].is_clicked():
                                    config["state"] = "settings"
                                if MAIN_MENU.buttons[2].is_clicked():
                                    run = False
                                    pygame.quit()
                            case "gamemode":
                                if GAMEMODE_MENU.buttons[-1].is_clicked():
                                    config["state"] = "main_menu"
                                else:
                                    for i in range(len(GAMEMODE_MENU.buttons)):
                                        if GAMEMODE_MENU.buttons[i].is_clicked():
                                            config["state"] = "game"
                                            game = Game(gamemodes[i])
                            case "settings":
                                if SETTINGS_MENU.buttons[-1].is_clicked():
                                    config["state"] = "main_menu"
                                else:
                                    for i, config_type in enumerate(["piece_asset", "board_asset", "sound_asset", "background_asset"]):
                                        if SETTINGS_MENU.buttons[i].is_clicked():
                                            config.selected_config = config_type
                            case "game":
                                if not game.game_over:
                                    row, column = get_pos(*pygame.mouse.get_pos())
                                    if 0 <= row < len(game.board) and 0 <= column < len(game.board[row]):
                                        game.select(row, column)
                                game.highlightedSquares = {}
                    elif right_click():
                        if config["state"] == "game":
                            row, column = get_pos(*pygame.mouse.get_pos())
                            if 0 <= row < len(game.board) and 0 <= column < len(game.board[row]):
                                game.selected, game.legal_moves, keys = None, [], pygame.key.get_pressed()
                                highlight = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) + (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) * 2
                                if game.highlightedSquares.get((row, column)) != highlight:
                                    game.highlightedSquares[(row, column)] = highlight
                                else:
                                    game.highlightedSquares.pop((row, column), None)


if __name__ == "__main__":
    main()