import pygame

from Pieces import Piece
from Menu import SETTINGS_MENU
from os.path import join
from constants import *

def change_piece(board: list[list[int | Piece]], asset: str) -> None:
    """
    Change the selected piece asset and update the board with the new piece images.

    Args:
        board (list[list[int | Piece]]): The chessboard represented as a 2D list of integers or Piece objects.
        asset (str): The asset name of the selected piece.

    Returns:
        None
    """
    config["selected_piece_asset"] = asset
    if config["selected_piece_asset"] == "blindfold":
        return
    piece_assets[config["selected_piece_asset"]] = generate_pieces(asset)
    if board is not None:
        for row in range(len(board)):
            for column in range(len(board[row])):
                piece = board[row][column]
                if piece != 0:
                    piece.image = piece_assets[config["selected_piece_asset"]][Piece.piece_to_index(piece) + 3 * (1 - piece.color)]
                    piece.calc_pos(piece.image)

def change_background(asset: str) -> None:
    """
    Change the background of the chess game.

    Args:
        asset (str): The name of the background asset.

    Returns:
        None
    """
    background_assets[asset] = pygame.transform.scale(pygame.image.load(join("assets", "backgrounds", asset + ".png")), (config["width"], config["height"]))
    config["selected_background_asset"] = asset

def change_sound(asset: str) -> None:
    """
    Change the selected sound asset and update the sound assets dictionary.

    Parameters:
    asset (str): The name of the sound asset to be selected.

    Returns:
    None
    """
    sound_assets.update(generate_sounds(asset))
    config["selected_sound_asset"] = asset
    for sound in types_sound_asset:
        sound_assets[(asset, sound)].play()

def change_board(asset: str) -> None:
    """
    Change the board asset and update the selected board asset in the configuration.

    Parameters:
    - asset (str): The new board asset to be set.

    Returns:
    - None
    """
    board_assets[asset] = generate_board(asset)
    config["selected_board_asset"] = asset

def play_sound(sound) -> None:
    """
    Plays the specified sound.

    Args:
        sound (str): The name of the sound to be played.

    Returns:
        None
    """
    sound_assets[("all" if sound in ["illegal", "notify", "tenseconds"] else config["selected_sound_asset"], sound)].play()

def refresh_parameters() -> None:
    """
    Refreshes the parameters of the chess game configuration.

    This function updates the selected configuration parameter in the settings menu
    based on the current value of `selected_config`. It retrieves the available assets
    for the selected configuration type and updates the label and appearance of the
    corresponding button in the settings menu.

    Parameters:
    None

    Returns:
    None
    """
    global selected_config
    button_index = None
    for i, config_type in enumerate(["piece_asset", "board_asset", "sound_asset", "background_asset"]):
        if selected_config == config_type:
            button_index = i
            break
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
    SETTINGS_MENU.buttons[button_index].label.text = available_assets[config_index[selected_config]]
    SETTINGS_MENU.buttons[button_index].refresh()

# Used to keep track of the selected setting type
config_index = {"piece_asset": available_piece_assets.index(config["selected_piece_asset"]), "board_asset": available_board_assets.index(config["selected_board_asset"]), "sound_asset": available_sound_assets.index(config["selected_sound_asset"]), "background_asset": available_background_assets.index(config["selected_background_asset"])}
selected_config = None