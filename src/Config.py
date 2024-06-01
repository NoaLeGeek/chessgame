import configparser
import ctypes

class Config:
    def __init__(self):
        self.screen_width, self.screen_height = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')
        self.height = self.config.getint('GENERAL', 'height') if self.config.getint('GENERAL', 'height') else self.screen_height
        self.width = self.height
        self.rules = []
        self.tile_size = self.height//12
        self.margin = self.tile_size//2
        self.fps = self.config.getint('GENERAL', 'fps')
        self.piece_asset = self.config.get('ASSETS', 'piece')

    def save(self):
        pass