import configparser
import ctypes
import sys
import os

class config:
    def __init__(self):
        self.screen_width, self.screen_height = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')
        self.height = self.config.getint('GENERAL', 'height') if self.config.getint('GENERAL', 'height') else self.screen_height
        self.width = self.height
        self.rules = dict(self.config.items('RULES'))
        self.tile_size = self.height//12
        self.margin = self.tile_size//2
        self.fps = self.config.getint('GENERAL', 'fps')
        self.volume = self.config.getfloat('GENERAL', 'volume')
        self.piece_asset = self.config.get('ASSETS', 'piece')
        self.board_asset = self.config.get('ASSETS', 'board')
        self.board_8x8_asset = self.config.get('ASSETS', 'board_8x8')
        self.sound_asset = self.config.get('ASSETS', 'sound')
        self.background_asset = self.config.get('ASSETS', 'background')

    def save(self):
        pass

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)