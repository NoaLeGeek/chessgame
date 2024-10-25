import pygame
import os
from Board.tile import Tile
from utils import get_position, generate_piece_images, play_sound, generate_board_image, generate_sounds, flip_coords
from Board.piece import Piece
from Board.move import Move
from config import Config
from random import choice

class Board:
    def __init__(self, config: Config, size: int):
        self.config = config
        self.image = generate_board_image(self.config.board_asset, self.config.tile_size)
        self.sounds = generate_sounds(self.config.sound_asset)
        self.sounds.update({name: pygame.mixer.Sound(os.path.join("assets", "sounds", f"{name}.ogg")) for name in ['illegal', 'notify', 'tenseconds']})
        self.size = size
        self.selected = None
        self.turn = 1
        self.winner = None
        self.ep_square = None
        self.promotion = False
        self.history = []
        self.halfMoves = 0
        self.fullMoves = 1
        self.flipped = 1
        self.kings = {1: None, -1: None}
        self.game_over = False
        if self.config.rules["+3_checks"] == True:
            self.win_condition = 0
        self.piece_images = generate_piece_images(self.config.piece_asset, self.config.tile_size)
        #self.reserves = {player: {piece: [] for piece in 'PLNSGBR'} for player in (-1, 1)}
        self.debug = False
        self.create_board()

    def create_board(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq – 0 1"
        self.board = {}
        for i, part in enumerate(fen.split()):
            match i:
                # Initialize the board
                case 0:
                    for r, string in enumerate(part.split("/")):
                        c = 0
                        for char in string:
                            if char.isdigit():
                                c += int(char)
                            else:
                                if char not in "rnbqkbnpRNBQKBNP":
                                    raise ValueError("Not a valid FEN")
                                color = 1 if char.isupper() else -1
                                tile = Tile(r, c, self.config.tile_size, self.config.margin)
                                tile.object = Piece.notation_to_piece(char)(self.config.rules, color, r, c, self.piece_images[("w" if color == 1 else "b") + char.upper()])
                                self.board[(r, c)] = tile
                                self.update_kings(r, c)
                                c += 1
                # Turn
                case 1:
                    self.turn = 1 if part == "w" else -1
                # Castling rights
                case 2:
                    # TODO doesn't work with 960
                    if "K" not in part and self.get(7, 7).object.notation == "R":
                        self.get(7, 7).object.first_move = False
                    if "Q" not in part and self.get(7, 0).object.notation == "R":
                        self.get(7, 0).object.first_move = False
                    if "k" not in part and self.get(0, 7).object.notation == "R":
                        self.get(0, 7).object.first_move = False
                    if "q" not in part and self.get(0, 0).object.notation == "R":
                        self.get(0, 0).object.first_move = False
                # En passant square
                case 3:
                    if part not in ['-', '–']:
                        self.ep_square = (flip_coords(int(part[1]) - 1, flipped = -self.flipped), flip_coords(ord(part[0]) - 97, flipped = self.flipped))
                # Half moves
                case 4:
                    self.halfMoves = int(part)
                # Full moves
                case 5:
                    self.fullMoves = int(part)
        play_sound(self.sounds, "game-start")         

    def generate_960_row(self, parts):
        last_row = [None]*len(self.config.columns)
        for index, piece in enumerate(["B", "B", "N", "N", "Q", "R", "K", "R"]):
            # Bishops
            if index < 2:
                last_row[choice(range(index, self.config.columns, 2))] = piece
            # Knights and Queen
            elif index < 5:
                last_row[choice([i for i, val in enumerate(last_row) if val is None])] = piece
            # Rooks and King
            else:
                last_row[[i for i, val in enumerate(last_row) if val is None][0]] = piece
        rows = parts[0].split("/")
        for row in [0, 7]:
            rows[row] = "".join(last_row)
            if row == 0:
                rows[row] = rows[row].lower()
        parts[0] = "/".join(rows)
        return parts
    
    def check_game(self) -> None:
        if self.config.rules["king_of_the_hill"] == True and any([not self.is_empty(*center) and self.get_object(*center).notation == "K" for center in self.get_center()]):
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.config.rules["+3_checks"] == True and self.win_condition >= 3:
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.config.rules["giveaway"] == True and (any([self.dict_color_pieces(color) == dict() for color in [1, -1]]) or self.is_stalemate()):
            print("{} Wins".format("Black" if self.turn == -1 else "White"))
            self.game_over = True
        elif self.config.rules["giveaway"] == False and self.is_checkmate():
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.is_stalemate():
            print("Stalemate")
            self.game_over = True
        elif self.halfMoves >= 100:
            print("Draw by the 50 moves rule")
            self.game_over = True
        elif self.is_insufficient_material():
            self.game_over = True
            print("Draw by insufficient material")
        elif self.is_threesold_repetition():
            self.game_over = True
            print("Draw by threesold repetition")
        if self.game_over:
            play_sound("game-end")

    def is_threesold_repetition(self):
        last_index = 0
        # TODO maybe make this a global variable to avoid recalculating it
        for i in range(len(self.history)-1, -1, -1):
            move = self.history[i]
            # Irreversible move are captures, pawn moves, castling or losing castling rights
            if move.capture or move.get_piece().notation == "P" or move.is_castling() or move.fen.split(" ")[2] != self.history[i-1].fen.split(" ")[2]:
                last_index = i
                break
        for i in range(last_index, len(self.history)):
            position1 = self.history[i].fen.split(" ")[0:4]
            count = 0
            for j in range(last_index, len(self.history)):
                position2 = self.history[j].fen.split(" ")[0:4]
                # Two positions are the same if the pieces are in the same position, if it's the same player to play, if the castling rights are the same and if the en passant square is the same
                if position1 == position2:
                    count += 1
                    if count == 3:
                        return True
        return False

    def get_center(self):
        return [(i, j) for i in range((self.config.rows-1)//2, (self.config.rows//2)+1) for j in range((self.config.columns-1)//2, (self.config.columns//2)+1)]
    
    def convert_to_move(self, row, column):
        return Move(self, (self.selected.row, self.selected.column), (row, column))

    # def select(self, row: int, column: int):
    #     self.selected = None
    #     if 0 <= row < 9 and 0 <= column < 9:
    #         piece = self.get(row, column).object
    #         if piece and piece.color == self.turn:
    #             self.selected = piece
    #             self.selected.calc_moves(self, row, column)
    #     elif self.is_valid_reserve_selection(row, column):
    #         self.selected = self.get_object_from_reserve(column)

    # def is_valid_reserve_selection(self, row, column):
    #     return ((row == -1 and 1 <= column < 8 and self.turn == 1) or
    #             (row == 9 and 1 <= column < 8 and self.turn == -1))

    # def get_object_from_reserve(self, column):
    #     piece_type = list(self.reserves[self.turn].keys())[column - 1]
    #     if self.reserves[self.turn][piece_type]:
    #         piece = self.reserves[self.turn][piece_type][0]
    #         piece.moves = self.get_empty_tiles()
    #         return piece
    #     return None

    def make_move(self, move):
        capture = self.get(*move).object
        self.move_piece(self.selected, move)
        if capture:
            self.capture_piece(capture)
        if (self.selected.row <= 2 and self.turn == -1 or self.selected.row >= 6 and self.turn == 1):
            self.promotion = True
            self.selected.moves = []
            return
        self.change_turn()

    def make_drop(self, move):
        self.place_piece(self.selected, move)
        self.change_turn()

    def move_piece(self, piece, move):
        self.board[piece.row][piece.column].object = None
        self.board[move[0]][move[1]].object = piece
        piece.move(*move)

    def capture_piece(self, piece):
        if piece.notation != 'K':
            piece.__init__(None, None, self.turn, None)
            piece.image = self.piece_images[piece.player][piece.notation]
            self.reserves[self.turn][piece.notation].append(piece)
        else :
            self.winner = self.turn
            print(f'{'black' if self.winner == 1 else 'white'} win')

    def place_piece(self, piece, move):
        self.board[move[0]][move[1]].object = piece
        piece.move(*move)
        self.remove_piece_from_reserve(piece)
        self.selected = None

    def remove_piece_from_reserve(self, piece):
        self.reserves[self.turn][piece.notation].remove(piece)
    
    def promote_piece(self, type_piece):
        new_piece = type_piece(self.selected.color, self.selected.row, self.selected.column)
        new_piece.image = self.piece_images[new_piece.notation]
        self.promotion = False
        self.change_turn()

    def change_turn(self):
        self.selected = None
        self.turn *= -1

    def update_kings(self, row, column):
        piece = self.get_object(row, column)
        if piece.notation == "K":
            self.kings[piece.color] = (row, column)

    def is_in_check(self):
        return self.get_object(*self.kings[self.turn]).in_check(self)

    def get_tile(self, row, column):
        return self.board.get((row, column), None)
    
    def get_object(self, row, column):
        if self.is_empty(row, column):
            return None
        return self.get_tile(row, column).object
    
    # True = Tile has no object
    def is_empty(self, row, column):
        return self.get_tile(row, column) is None
    
    # True = Tile has an object with an hitbox
    def is_occupied(self, row, column):
        if self.is_empty(row, column):
            return False
        return self.get_object(row, column).has_hitbox()
    
    def get_empty_tiles(self):
        return [(r, c) for r, c in self.board.keys() if not self.is_occupied(r, c)]

    def select_object(self, row, column):
        if self.selected:
            x = self.selected.color * self.flipped
            # If in the state of promotion
            if self.selected.notation == "P" and self.promotion:
                # User clicked in the range of promotion
                if row in range(flip_coords(0, flipped=x), flip_coords(0, flipped=x) + x*len(self.selected.promotion), x) and column == self.promotion[1] + self.selected.column:
                    self.promote_piece(self.selected.promotion[flip_coords(row, flipped=x)])
                    return
                # User did not click in the range of promotion
                self.promotion = False
                # Reselect the pawn if clicked
                if (row, column) == (self.selected.row, self.selected.column):
                    self.selected = None
                    self.select_object(row, column)
                    return
            # If the player clicks on one of his pieces, it will change the selected piece
            if not self.is_empty(row, column) and self.get_object(row, column).is_piece() and self.get_object(row, column).is_ally(self.selected) and (row, column) != (self.selected.row, self.selected.column):
                # Castling move
                if self.selected.notation == "R" and self.get_object(row, column).notation == "K" and (row, column) in self.selected.moves:
                    self.execute_move(row, column)
                    return
                self.selected = None
                self.select_object(row, column)
                return
            # If the play clicks on the selected piece, the selection is removed
            if (row, column) == (self.selected.row, self.selected.column):
                self.selected = None
                return
            # If the player clicks on a square where the selected piece can't move, it will remove the selection
            if (row, column) not in self.selected.moves:
                self.selected = None
                if self.kings[self.turn] is None or self.is_in_check():
                    play_sound("illegal")
                return
            # If the player push a pawn to one of the last rows, it will be in the state of promotion
            if self.selected.notation == "P" and row in [0, self.config.rows - 1]:
                self.selected.move(row, column)
                self.promotion = True
                if self.config.rules["giveaway"] == True:
                    self.promote_piece(self.selected.promotion)
                    return
                return
            self.execute_move(row, column)
        else:
            # Empty tile
            if self.is_empty(row, column):
                return
            # Not a piece
            if not self.get_object(row, column).is_piece():
                return
            # Not the player's piece
            if self.get_object(row, column).color != self.turn:
                return
            self.selected = self.get_object(row, column)
            moves = self.selected.moves
            if self.config.rules["giveaway"] == True and any([self.convert_to_move(*move).is_capture() for move in moves]):
                moves = list(filter(lambda move: self.convert_to_move(*move).is_capture(), moves))
            else:
                moves = list(filter(lambda move: self.convert_to_move(*move).is_legal(), moves))
            self.selected.moves = moves

    def handle_left_click(self):
        x, y = pygame.mouse.get_pos()
        row, column = get_position(x, y, self.config.margin, self.config.tile_size)
        if not self.is_empty(row, column) and self.get_object(row, column).is_piece() and self.get_object(row, column).color == self.turn:
            self.get_object(row, column).calc_moves(self, row, column, self.flipped, ep_square=self.ep_square)
        self.select_object(row, column)

    def draw(self, screen):
        self.draw_tiles(screen)
        self.draw_pieces(screen)
        if self.selected:
            self.draw_moves(screen)
        self.draw_reserves(screen)
        if self.promotion:
            self.draw_promotion(screen)
        
class FEN:
    def __init__(self, board, turn, castling_rights, ep_square, half_move, full_move):
        self.board = board
        self.turn = turn
        self.castling_rights = castling_rights
        self.ep_square = ep_square
        self.half_move = half_move
        self.full_move = full_move
    
    def to_literal():
        pass
