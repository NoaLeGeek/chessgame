import pygame.draw
import os

from Pieces import *
import constants


class Board:
    def __init__(self, width, height, rows, columns, frame):
        self.width = width
        self.height = height
        self.rows = rows
        self.columns = columns
        self.frame = frame
        self.board = []
        self.debug = False

    def draw_board(self):
        self.frame.blit(constants.board_assets[constants.board_asset], (margin, margin))

    def draw_piece(self, piece, window):
        window.blit(piece.image, (piece.x, piece.y))

    def draw_rect(self, row, column):
        pygame.draw.rect(self.frame, (255, 0, 0), (column * square_size + margin, row * square_size + margin, square_size, square_size))

    def draw_pieces(self, promotion=None):
        for row in range(self.rows):
            for column in range(self.columns):
                if self.debug:
                    self.frame.blit(pygame.font.SysFont("monospace", 15).render(f"({column},{row})", 1, (0, 0, 0)), (row*square_size+35, column*square_size+60))
                piece = self.board[row][column]
                if piece == 0 or (promotion and promotion[0] == piece):
                    continue
                self.draw_piece(piece, self.frame)

    def draw_moves(self, moves):
        for pos in moves:
            row, column = pos[0], pos[1]
            transparent_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            pygame.draw.circle(transparent_surface, (0, 0, 0, 63), (square_size // 2, square_size // 2), square_size // 8)
            self.frame.blit(transparent_surface, (column * square_size + margin, row * square_size + margin))

    def draw_promotion(self, promotion, offset, flipped):
        # TODO add exit button with a X
        x = (promotion.color * -flipped)
        pygame.draw.rect(self.frame, (255, 255, 255), ((promotion.column + offset * flipped) * square_size + margin, 2 * (1 - x) * square_size + margin, square_size, 4*square_size))
        # [Queen, Pieces.Knight, Pieces.Rook, Pieces.Bishop][(row if self.selected.color == 1 else 7 - row)]
        if pieces_asset != "blindfold":
            for i in range(4):
                render = [Queen, Knight, Rook, Bishop][i](promotion.color, 7 * (1 - x) // 2 + x * i, promotion.column + offset * flipped)
                render.image = constants.piece_assets[constants.pieces_asset][Piece.piece_to_index(render) + 3 * (1 - render.color)]
                self.frame.blit(render.image, (render.x, render.y))
            
    def draw_highlightedSquares(self, highlightedSquares):
        for ((row, column), highlight) in highlightedSquares.items():
            match highlight:
                case 0:
                    r, g, b = 255, 0, 0
                case 1:
                    r, g, b = 0, 255, 0
                case 2:
                    r, g, b = 255, 165, 0
                case 3:
                    r, g, b = 255, 255, 0
                case _:
                    continue
            transparent_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            transparent_surface.fill((r, g, b, 75))
            self.frame.blit(transparent_surface, (column * square_size + margin, row * square_size + margin))

    def flip_board(self):
        for row in range(self.rows):
            for column in range(self.columns):
                piece = self.board[row][column]
                if piece != 0:
                    piece.piece_move(7 - piece.row, 7 - piece.column)
        for row in self.board:
            row.reverse()
        self.board.reverse()

    def change_asset(self, asset):
        constants.pieces_asset = asset
        print(constants.pieces_asset)
        if pieces_asset == "blindfold":
            return
        constants.piece_assets[constants.pieces_asset] = constants.generate_images(asset)
        for row in range(self.rows):
            for column in range(self.columns):
                piece = self.board[row][column]
                if piece != 0:
                    piece.image = piece_assets[asset][Piece.piece_to_index(piece) + 3 * (1 - piece.color)]
                    piece.calc_pos(piece.image)
    
    def draw_background(self):
        self.frame.blit(constants.background_assets[constants.background_asset], (0, 0))

    def change_background(self, asset):
        constants.background_assets[asset] = pygame.transform.scale(pygame.image.load(os.path.join("assets", "backgrounds", asset + ".png")), (self.width, self.height))
        constants.background_asset = asset
