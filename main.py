import random
import constants
import pygame

from Game import Game
from Pieces import *


pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode((constants.width, constants.height))

def get_position(x, y):
    return y // constants.square_size, x // constants.square_size


def main():
    run = True
    game_over = False
    fps = 60
    game = Game(constants.width, constants.height, constants.rows, constants.columns, window)
    while run:
        clock.tick(fps)
        game.update_window()
        game_over = game.check_game()
        for event in pygame.event.get():
            if game_over or event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.reset(window)
            #if game.turn == -1:
                #randomPiece = random.choice(list(filter(lambda p: len(p.get_available_moves(game.get_board().board, p.row, p.column)) != 0, game.get_color_pieces(game.turn))))
                #game.select(randomPiece.row, randomPiece.column)
                #randomMove = random.choice(randomPiece.get_available_moves(game.get_board().board, randomPiece.row, randomPiece.column))
                #game.select(randomMove[0], randomMove[1])
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
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
                    game.highlightedSquares = []
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