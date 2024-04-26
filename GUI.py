import constants
import pygame

from constants import *
from Pieces import *

def draw_text(text: str, color: tuple[int, int, int], size: int, center: tuple[int, int], font: str):
    text_surface = pygame.font.SysFont(font, size).render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = center
    window.blit(text_surface, text_rect)

def draw_board():
    window.blit(board_assets[config["selected_board_asset"]], (config["margin"], config["margin"]))

def draw_piece(piece):
    window.blit(piece.image, (piece.x, piece.y))

def draw_rect(row, column):
    pygame.draw.rect(window, (255, 0, 0), (column * square_size + config["margin"], row * square_size + config["margin"], square_size, square_size))

def draw_pieces(board, promotion=None, debug: bool = False):
    for row in range(len(board)):
        for column in range(len(board[row])):
            if debug:
                window.blit(pygame.font.SysFont("monospace", 15).render(f"({column},{row})", 1, (0, 0, 0)), (row*square_size+35, column*square_size+60))
            piece =  board[row][column]
            if piece == 0 or (promotion and promotion[0] == piece):
                continue
            draw_piece(piece)

def draw_moves(moves):
    for pos in moves:
        row, column = pos[0], pos[1]
        transparent_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        pygame.draw.circle(transparent_surface, (0, 0, 0, 63), (square_size // 2, square_size // 2), square_size // 8)
        window.blit(transparent_surface, (column * square_size + config["margin"], row * square_size + config["margin"]))

def draw_promotion(promotion, offset, flipped):
    x = (promotion.color * -flipped)
    # Draw the promotion rectangle
    pygame.draw.rect(window, (255, 255, 255), ((promotion.column + offset) * square_size + config["margin"], 2 * (1 - x) * square_size + config["margin"], square_size, 4*square_size))
    # Draw the X rectangle
    pygame.draw.rect(window, (241, 241, 241), ((promotion.column + offset) * square_size + config["margin"], ((15 + x) / 4) * square_size + config["margin"], square_size, .5*square_size))
    # Draw the X
    center_x, center_y = (promotion.column + offset + 1/2) * square_size + config["margin"], ((16 + x) / 4) * square_size + config["margin"]
    pygame.draw.line(window, (139, 137, 135), (center_x - square_size / 8, center_y - square_size / 8), (center_x + square_size / 8, center_y + square_size / 8), round(square_size / 15))
    pygame.draw.line(window, (139, 137, 135), (center_x + square_size / 8, center_y - square_size / 8), (center_x - square_size / 8, center_y + square_size / 8), round(square_size / 15))
    if config["selected_piece_asset"] == "blindfold":
        return
    for i in range(5):
        if i < 4:
            render = [Queen, Knight, Rook, Bishop][i](promotion.color, 7 * (1 - x) // 2 + x * i, promotion.column + offset)
            render.image = piece_assets[config["selected_piece_asset"]][Piece.piece_to_index(render) + 3 * (1 - render.color)]
            window.blit(render.image, (render.x, render.y))
                  
def draw_highlightedSquares(highlightedSquares):
    for ((row, column), highlight) in highlightedSquares.items():
        match highlight:
            # Right click
            case 0:
                r, g, b = 255, 0, 0
            # Shift + Right click
            case 1:
                r, g, b = 0, 255, 0
            # Ctrl + Right click
            case 2:
                r, g, b = 255, 165, 0
            # History move
            case 3:
                r, g, b = 255, 255, 0
            # Selected piece
            case 4:
                r, g, b = 0, 255, 255
            case _:
                continue
        transparent_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        transparent_surface.fill((r, g, b, 75))
        window.blit(transparent_surface, (column * square_size + config["margin"], row * square_size + config["margin"]))

def draw_background():
    window.blit(background_assets[config["selected_background_asset"]], (0, 0))