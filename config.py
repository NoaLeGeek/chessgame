import configparser
import ctypes

class Config:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')
        self.height = self.config.getint('GENERAL', 'height') if self.config.getint('GENERAL', 'height') else self.generate_height()
        self.width = int(self.height * 0.85)
        self.tile_size = self.height//12
        self.margin = self.tile_size//2
        self.fps = self.config.getint('GENERAL', 'fps')
        self.piece_asset = self.config.get('ASSETS', 'piece')

    def generate_height(self):
        return round((self.user32.GetSystemMetrics(1)-100)/12)*12

    def save(self):
        pass