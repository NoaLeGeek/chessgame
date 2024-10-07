import configparser
import ctypes
import sys
import os


class Config:
    #TODO paramètre full screen on/off
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')
        self.rules = dict(self.config.items('RULES'))
        self.fps = self.config.getint('GENERAL', 'fps')
        self.volume = self.config.getfloat('GENERAL', 'volume')
        self.piece_asset = self.config.get('ASSETS', 'piece')
        self.board_asset = self.config.get('ASSETS', 'board')
        self.sound_asset = self.config.get('ASSETS', 'sound')
        self.background_asset = self.config.get('ASSETS', 'background')
        self.rows = self.config.getint('BOARD', 'rows')
        self.columns = self.config.getint('BOARD', 'columns')

    def save(self):
        pass

    def set_dimensions(self, width, height):
        self.dimensions = (width, height)
        self.height = self.config.getint('GENERAL', 'height') if self.config.getint('GENERAL', 'height') else self.dimensions[1] - 48
        self.width = self.height
        self.margin = self.height//(self.columns*2 + 2)
        self.tile_size = self.height//(self.columns+1)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
