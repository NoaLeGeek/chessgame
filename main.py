from constants import *
import pygame
import random
import Menu

from Game import Game
from Pieces import *
        
def main():
    run = True
    game_over = False
    fps = 60
    game = Game(width, height, rows, columns, window)
    while run:
        clock.tick(fps)
        game.update_window()
        game_over = False
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                if pygame.display.Info().current_h != height:
                    pygame.display.set_mode((pygame.display.Info().current_w, height), pygame.RESIZABLE)
                if pygame.display.Info().current_w > width:
                    pygame.display.set_mode((width, pygame.display.Info().current_h), pygame.RESIZABLE)
                if pygame.display.Info().current_w < height:
                    pygame.display.set_mode((height, pygame.display.Info().current_h), pygame.RESIZABLE)
                for button in Menu.MAIN_MENU.buttons:
                    button.refresh()
                for label in Menu.MAIN_MENU.labels:
                    label.refresh()
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.reset(window)
                if event.key == pygame.K_f and game.state == "game":
                    game.board.flip_board()
                    game.flip_game()
                if event.key == pygame.K_c:
                    game.board.change_piece(random.choice(available_piece_assets))
                    game.board.change_background(random.choice(available_background_assets))
                    game.board.change_sound(random.choice(available_sound_assets))
                    game.board.change_board(random.choice(available_board_assets))
            #if game.turn == -1:
                #randomPiece = random.choice(list(filter(lambda p: len(p.get_available_moves(game.get_board().board, p.row, p.column)) != 0, game.get_color_pieces(game.turn))))
                #game.select(randomPiece.row, randomPiece.column)
                #randomMove = random.choice(randomPiece.get_available_moves(game.get_board().board, randomPiece.row, randomPiece.column))
                #game.select(randomMove[0], randomMove[1])
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                # Left click
                if pygame.mouse.get_pressed()[0]:
                    if game.state == "main_menu":
                        if Menu.MAIN_MENU.buttons[0].is_clicked():
                            game.state = "game"
                            game.create_board()
                        if Menu.MAIN_MENU.buttons[1].is_clicked():
                            game.state = "settings"
                        if Menu.MAIN_MENU.buttons[3].is_clicked():
                            run = False
                            pygame.quit()
                    elif game.state == "game":
                        row, column = get_position(*pygame.mouse.get_pos())
                        if 0 <= row < rows and 0 <= column < columns:
                            selected_piece = game.board.board[row][column]
                            print("clicked on:", selected_piece if selected_piece != 0 else 0)
                            print("cRow", row, "cColumn", column)
                            if selected_piece != 0 and isinstance(selected_piece, King):
                                print(selected_piece.get_available_moves(game.board.board, row, column, game.flipped, en_passant=game.en_passant))
                                print("first_move", selected_piece.first_move)
                            #if game.turn == 1:
                            game.select(row, column)
                        game.highlightedSquares = {}
                # Right click
                elif pygame.mouse.get_pressed()[2]:
                    if game.state == "game":
                        row, column = get_position(*pygame.mouse.get_pos())
                        if 0 <= row < rows and 0 <= column < columns:
                            game.selected, game.valid_moves, keys = None, [], pygame.key.get_pressed()
                            highlight = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) + (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) * 2
                            if game.highlightedSquares.get((row, column)) != highlight:
                                game.highlightedSquares[(row, column)] = highlight
                            else:
                                game.highlightedSquares.pop((row, column), None)


if __name__ == "__main__":
    main()