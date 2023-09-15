import pygame
import os
import random

from Board import Board

clock = pygame.time.Clock()
width, height = 760, 760
window = pygame.display.set_mode((width, height))
rows, columns = 8, 8
square_size = width // columns
tile_assets = {"brown": ((237, 214, 176), (184, 135, 98)),
               "green": ((233, 237, 204), (119, 153, 84)),
               "sky": ((240, 241, 240), (196, 216, 228)),
               "8-bit": ((243, 243, 244), (106, 155, 65)),
               "purple": ((240, 241, 240), (132, 118, 186)),
               "blue": ((234, 233, 210), (75, 115, 153)),
               "bubblegum": ((254, 255, 254), (251, 217, 225)),
               "checkers": ((199, 76, 81), (48, 48, 48)),
               "light": ((216, 217, 216), (168, 169, 168)),
               "orange": ((250, 228, 174), (209, 136, 21)),
               "red": ((245, 219, 195), (187, 87, 70)),
               "tan": ((237, 203, 165), (216, 164, 109))}
selected_asset = "brown"


def get_position(x, y):
    return x // square_size, y // square_size


def main():
    pygame.init()
    board = Board(width, height, rows, columns, square_size, window)
    for i in range(len(board.board)):
        if i < 1:
            pass
    run = True
    fps = 60
    # Piece images are stored in the following order: pawn, knight, bishop, rook, queen, king. White pieces come first.
    pieces = {}
    for piece in ["wP", "wN", "wB", "wR", "wQ", "wK", "bP", "bN", "bB", "bR", "bQ", "bK"]:
        pieces[piece] = pygame.transform.scale(pygame.image.load(
            os.path.join("assets", ("white" if piece.startswith("w") else "black") + "Pieces", selected_asset,
                         piece + ".png")), (square_size, square_size))
    while run:
        clock.tick(fps)
        for i in range(int(square_size / 2), int(square_size * 8 - square_size / 2), square_size):
            window.blit(pieces["wR"], (i, square_size / 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    location = pygame.mouse.get_pos()
                    window.blit(pieces[list(pieces.keys())[random.randint(0, len(pieces) - 1)]],
                                (location[0] - square_size / 2, location[1] - square_size / 2))
                    row, col = get_position(location[0], location[1])


if __name__ == "__main__":
    main()
