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
    game = Game(width, height, rows, columns, square_size, window)
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
            #     moves = {}
            #     for row in range(rows):
            #         for column in range(columns):
            #             if game.board.board[row][column] != 0 and game.board.board[row][column].color == -1 and game.board.board[row][column].get_available_moves(game.board.board, row, column):
            #                 moves[(row, column)] = random.choice(game.board.board[row][column].get_available_moves(game.board.board, row, column))
            #     row, column = random.choice(list(moves.keys()))
            #     game.move(game.board.board[row][column], moves[(row, column)][0], moves[(row, column)][1])
            #     game.turn = 1
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if pygame.mouse.get_pressed()[0]:
                    location = pygame.mouse.get_pos()
                    row, column = get_position(location[0], location[1])
                    selected_piece = game.get_board().board[row][column]
                    print("clicked on:", selected_piece.type if selected_piece != 0 else 0)
                    print("cRow", row, "cColumn", column)
                    if selected_piece != 0:
                        pass
                        # print("avaible moves:", selected_piece.get_available_moves(game.get_board().board, row, column))
                    print("king pos:", game.get_king_position(game.turn))
                    if game.is_king_checked():
                        print("king checked")
                    print("checkmate:", game.checkmate())
                    game.select(row, column)


if __name__ == "__main__":
    main()
