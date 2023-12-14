import random

from Game import Game
from constants import *

pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode((width, height))


def get_position(x, y):
    return y // square_size, x // square_size


def main():
    run = True
    game_over = False
    fps = 60
    game = Game(width, height, rows, columns, window)
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
            # if game.turn == -1:
            #     randomPiece = random.choice(list(filter(lambda p: len(p.get_available_moves(game.get_board().board, p.row, p.column)) != 0, game.get_color_pieces(game.turn))))
            #     game.select(randomPiece.row, randomPiece.column)
            #     randomMove = random.choice(randomPiece.get_available_moves(game.get_board().board, randomPiece.row, randomPiece.column))
            #     game.select(randomMove[0], randomMove[1])
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
                    print("king pos:", game.get_king_position(game.turn))
                    if game.is_king_checked():
                        print("king checked")
                    print("checkmate:", game.is_stalemate() and game.is_king_checked())
                    #if game.turn == 1:
                    game.select(row, column)
                    game.highlightedSquares = []


if __name__ == "__main__":
    main()
