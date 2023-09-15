import pygame
import os


def main():
    pygame.init()
    clock = pygame.time.Clock()
    run = True
    fps = 60
    width, height = 760, 760
    win = pygame.display.set_mode((width, height))
    rows, cols = 8, 8
    square_size = width // cols
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
    # Piece images are stored in the following order: pawn, knight, bishop, rook, queen, king. White pieces come first.
    pieces = {}
    for piece in ["wP", "wN", "wB", "wR", "wQ", "wK", "bP", "bN", "bB", "bR", "bQ", "bK"]:
        pieces[piece] = pygame.transform.scale(pygame.image.load(
            os.path.join("assets", ("white" if piece.startswith("w") else "black") + "Pieces", selected_asset, piece + ".png")), (square_size, square_size))
    while run:
        clock.tick(fps)
        win.blit(pieces["wR"], (50, 50))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()


if __name__ == "__main__":
    main()
