import pygame
import constants
import os

from Pieces import *
from Menu import SETTINGS_MENU
from constants import piece_assets, generate_pieces, generate_board, generate_sounds, available_background_assets, available_board_assets, available_piece_assets, available_sound_assets

def change_piece(board, asset):
        config["selected_piece_asset"] = asset
        if config["selected_piece_asset"] == "blindfold":
            return
        piece_assets[config["selected_piece_asset"]] = generate_pieces(asset)
        for row in range(config["rows"]):
            for column in range(config["columns"]):
                piece = board[row][column]
                if piece != 0:
                    piece.image = piece_assets[config["selected_piece_asset"]][Piece.piece_to_index(piece) + 3 * (1 - piece.color)]
                    piece.calc_pos(piece.image)

def change_background(asset):
    constants.background_assets[asset] = pygame.transform.scale(pygame.image.load(os.path.join("assets", "backgrounds", asset + ".png")), (config["width"], config["height"]))
    config["selected_background_asset"] = asset

def change_sound(asset):
    constants.sound_assets.update(generate_sounds(asset))
    config["selected_sound_asset"] = asset

def change_board(asset):
    constants.board_assets[asset] = generate_board(asset)
    config["selected_board_asset"] = asset

def play_sound(sound):
    constants.sound_assets[("all" if sound in ["illegal", "notify", "tenseconds"] else config["selected_sound_asset"], sound)].play()

def refresh_parameters():
    global selected_config
    for i, config_type in enumerate(["piece_asset", "board_asset", "sound_asset", "background_asset"]):
        if SETTINGS_MENU.buttons[i].is_clicked():
            available_assets = None
            match selected_config:
                case "board_asset":
                    available_assets = available_board_assets
                case "piece_asset":
                    available_assets = available_piece_assets
                case "background_asset":
                    available_assets = available_background_assets
                case "sound_asset":
                    available_assets = available_sound_assets
            SETTINGS_MENU.buttons[i].label = available_assets[config_index[selected_config]]
            SETTINGS_MENU.buttons[i].refresh()

config_index = {"piece_asset": available_piece_assets.index(config["selected_piece_asset"]), "board_asset": available_board_assets.index(config["selected_board_asset"]), "sound_asset": available_sound_assets.index(config["selected_sound_asset"]), "background_asset": available_background_assets.index(config["selected_background_asset"])}
selected_config = None