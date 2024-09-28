import configparser
import ctypes
import sys
import os

class Config:
    #TODO revoir le calcul de la taille de la fenêtre
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')
        self.rules = dict(self.config.items('RULES'))
        self.fps = self.config.getint('GENERAL', 'fps')
        self.volume = self.config.getfloat('GENERAL', 'volume')
        self.taskbar_height = self.config.getint('GENERAL', 'taskbar_height')
        self.piece_asset = self.config.get('ASSETS', 'piece')
        self.board_asset = self.config.get('ASSETS', 'board')
        self.board_8x8_asset = self.config.get('ASSETS', 'board_8x8')
        self.sound_asset = self.config.get('ASSETS', 'sound')
        self.background_asset = self.config.get('ASSETS', 'background')

    def save(self):
        pass

    def set_dimensions(self, width, height):
        self.dimensions = (width, height)
        self.height = self.config.getint('GENERAL', 'height') if self.config.getint('GENERAL', 'height') else self.dimensions[1] - self.taskbar_height
        self.width = height
        self.tile_size = self.height//12
        self.margin = self.tile_size//2

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)