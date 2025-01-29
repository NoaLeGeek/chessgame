import configparser
import sys
import os


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')
        self.fps = self.config.getint('GENERAL', 'fps')
        self.volume = self.config.getfloat('GENERAL', 'volume')
        self.piece_asset = self.config.get('ASSETS', 'piece')
        self.board_asset = self.config.get('ASSETS', 'board')
        self.sound_asset = self.config.get('ASSETS', 'sound')
        self.flipped_assets = self.config.getboolean('ASSETS', 'flipped_assets')
        self.background_asset = self.config.get('ASSETS', 'background')
        self.rows = self.config.getint('BOARD', 'rows')
        self.columns = self.config.getint('BOARD', 'columns')
        self.rules = {
            "puissance_4_pawns": False,
            "mutation_chess": False,
            "king_of_the_hill": False,
            "+3_checks": False,
            "giveaway": False,
            "chess960": False,
            "random_position": False,
            "random_promotion": False,
            "no_promotion": False,
            "only_piece_promotion": False, # types of pieces
            "no_en_passant": False,
            "en_passant_forced": False,
            "swapper": False,  # n pourcentage
            "freezer": False,  # n pourcentage
            "any_capture": False,
            "barbarians": False,  # n pourcentage and types of pieces
            "torpedo": False,
            "crawl": False,
            "overpass": False,
            "retreat": False,
            "leap": False,
            "sideways": False,
            "upside_down": False,
            "regal_sweep": False,
            "frozen_wonderland": False,
            "reverse_strike": False,
            "inward_strike": False,
            "allow_passing": False,
            "double_play": False,
            "bare_piece": False,
            "duck_chess": False,
            "opposite_castling": False,
            "no_big_castle": False,
            "no_small_castle": False,
            "no_castling": False,
            "ignore_check": False,
            "teleporter_madness": False,
            "atomic": False,
            "fatal_capture": False,
            "blindfold": False,
            "ghostboard": False,
            "forward_march": False,
            "colorblind": False,
            "crazyhouse": False,
            "racing_kings": False,
            "4_player_chess": False,
            "mystery_chess": False,
            "royal_quota": False,
            "corregal": False,
            "decimation": False,
            "knightmate": False,
            "extinction": False,
            "pawns_only": False,
            "cylinder": False,
            "bouncing": False,
            "infinite_bouncing": False,
            "berolina": False,
            "absorption": False,
            "cannibal": False,
            "fog_of_war": False,
            "chess18": False,
            "shuffle_chess": False,  # no castling
            "chess2880": False,
            "reverse_backrank": False,
            "random_play_first": False,
            "black_play_first": False,
            "half_chaos": False,
            "random_asset": False,
            "asset_chaos": False,
            "thanos": False,  # n pourcentage
            "mirror": False,
            "pawn_parade": False,
            "half_commitment": False,
            "unique_step": False,
            "instant_void": False,  # n moves
            "random_walls": False,  # n pourcentage
            "minefield": False,  # n pourcentage
            "super_size": False,  # n
            "abstract": False,
            "accelerated": False,
            "active": False,
            "rotating_center": False,  # clockwise, anticlockwise or diagonal
            "advance": False,
            "el_vaticano": False,
            "all-in": False,
            "all-mate": False,
            "almost": False,
            "amazon": False,
            "annihilation": False,
            "anti-gravity": False,
            "anti-magnet": False,
            "anywhere": False,
            "archimedes": False,
            "alternating": False,
            "atlantis": False,
            "bachelor": False,
        }

    def save(self):
        pass

    def set_dimensions(self, width, height):
        #self.dimensions = (width, height)
        #self.height = self.config.getint('GENERAL', 'height') if self.config.getint('GENERAL', 'height') else self.dimensions[1] - 48
        #self.width = self.height
        self.width, self.height = width, height
        self.margin = self.height//(self.columns*2 + 2)
        self.tile_size = self.height//(self.columns+1)
        

    def update_rule(self, rule, value = None):
        if value is None:
            value = not bool(self.rules.get(rule))
        self.rules[rule] = value

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

config = Config()