import pygame
import constants
from Pieces import *
from constants import *

def change_piece(self, asset):
        config["selected_piece_asset"] = asset
        if constants.selected_piece_asset == "blindfold":
            return
        piece_assets[config["selected_piece_asset"]] = generate_images(asset)
        for row in range(self.rows):
            for column in range(self.columns):
                piece = self.board[row][column]
                if piece != 0:
                    piece.image = piece_assets[config["selected_piece_asset"]][Piece.piece_to_index(piece) + 3 * (1 - piece.color)]
                    piece.calc_pos(piece.image)

def change_background(asset):
    constants.background_assets[asset] = pygame.transform.scale(pygame.image.load(os.path.join("assets", "backgrounds", asset + ".png")), (config["width"], config["height"]))
    constants.selected_background_asset = asset

def change_sound(asset):
    constants.sound_assets.update(generate_sounds(asset))
    constants.selected_sound_asset = asset

def change_board(asset):
    constants.board_assets[asset] = generate_board(asset)
    constants.selected_board_asset = asset



