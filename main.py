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
                    selected_piece = game.get_board().board[row][column]
                    print("clicked on:", selected_piece.type if selected_piece != 0 else 0)
                    print("cRow", row, "cColumn", column)
                    if selected_piece != 0:
                        pass
                        # print("avaible moves:", selected_piece.get_available_moves(row, column, game.get_board().board))
                    print("king pos:", game.get_king_position(game.get_board().board, game.turn))
                    print("king checked:", game.is_king_checked())
                    game.select(row, column)


if __name__ == "__main__":
    main()
