import pygame
import os
from Board.tile import Tile
from constants import castling_rook_pos
from utils import get_position, generate_piece_images, play_sound, generate_board_image, generate_sounds, flip_coords, sign
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
        self.ep = None
        self.ep_log = []
        self.promotion = False
        self.moveLogs = []
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
                                tile.piece = Piece.notation_to_piece(char)(self.config.rules, color, r, c, self.piece_images[("w" if color == 1 else "b") + char.upper()])
                                self.board[(r, c)] = tile
                                self.update_kings(r, c)
                                c += 1
                # Turn
                case 1:
                    self.turn = 1 if part == "w" else -1
                # Castling rights
                case 2:
                    # for d in [-1, 1]:
                    #     for row in 
                    # TODO doesn't work with 960
                    if "K" not in part and self.get_piece(7, 7).notation == "R":
                        self.get_piece(7, 7).first_move = False
                    if "Q" not in part and self.get_piece(7, 0).notation == "R":
                        self.get_piece(7, 0).first_move = False
                    if "k" not in part and self.get_piece(0, 7).notation == "R":
                        self.get_piece(0, 7).first_move = False
                    if "q" not in part and self.get_piece(0, 0).notation == "R":
                        self.get_piece(0, 0).first_move = False
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
        if self.config.rules["king_of_the_hill"] == True and any([not self.is_empty(*center) and self.get_piece(*center).notation == "K" for center in self.get_center()]):
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
        for i in range(len(self.moveLogs)-1, -1, -1):
            move = self.moveLogs[i]
            # Irreversible move are captures, pawn moves, castling or losing castling rights
            if move.capture or move.get_piece().notation == "P" or move.is_castling() or move.fen.split(" ")[2] != self.moveLogs[i-1].fen.split(" ")[2]:
                last_index = i
                break
        for i in range(last_index, len(self.moveLogs)):
            position1 = self.moveLogs[i].fen.split(" ")[0:4]
            count = 0
            for j in range(last_index, len(self.moveLogs)):
                position2 = self.moveLogs[j].fen.split(" ")[0:4]
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

    def make_move(self, move):
        capture = self.get(*move).piece
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
    
    def promote_piece(self, type_piece):
        new_piece = type_piece(self.selected.color, self.selected.row, self.selected.column)
        if self.config.piece_asset != "blindfold":
            new_piece.image = self.piece_images[new_piece.notation]
        self.board[(self.selected.row, self.selected.column)].piece = new_piece
        self.promotion = False

    def change_turn(self):
        self.selected = None
        self.turn *= -1

    def update_kings(self, row, column):
        piece = self.get_piece(row, column)
        if piece.notation == "K":
            self.kings[piece.color] = (row, column)

    def is_in_check(self):
        return self.get_piece(*self.kings[self.turn]).in_check(self)

    def get_tile(self, row, column):
        return self.board.get((row, column), None)
    
    def get_piece(self, row, column):
        if self.is_empty(row, column):
            return None
        return self.get_tile(row, column).piece
    
    # True = Tile has no object
    def is_empty(self, row, column):
        return self.get_tile(row, column) is None
    
    def get_empty_tiles(self):
        return [(r, c) for r, c in self.board.keys() if self.is_empty(r, c)]
    
    def move_piece(self, move: Move):
        piece, row, column = move.get_piece(), *move.to
        assert not self.is_empty(piece.row, piece.column)
        del self.board[(piece.row, piece.column)]
        self.board[(row, column)] = piece

        x = piece.color * self.flipped
        # Castling
        if move.is_castling():
            d = sign(column - piece.column)
            # Rook and King's positions are swapped to avoid King's deletion during some 960 castling
            # King is now at (row, column)
            # Rook is now at (row, piece.column)
            self.board[(row, column)], self.board[(row, piece.column)] = self.board[(row, piece.column)], self.board[(row, column)]
            # Calculate the new position for the rook
            rook_column = flip_coords(castling_rook_pos[d*self.flipped], flipped=d*self.flipped)
            # piece.column hasn't updated, we can use it as the old King's pos where the rook is
            self.get_piece(row, piece.column).move(row, rook_column)
            self.board[(row, piece.column)], self.board[(row, rook_column)] = self.board[(row, rook_column)], self.board[(row, piece.column)]
            # King's pos is updated
            self.get_piece(row, column).move(row, column)
            # Calculate the new position for the king
            column = flip_coords(castling_rook_pos[d*self.flipped]+d, flipped=d*self.flipped)
        # En-passant
        elif piece.notation == "P" and not self.is_empty(row + x, column) and self.get_piece(row + x, column).notation == "P" and self.en_passant == (piece.row - x, column):
            del self.board[(row + x, column)]
        self.en_passant = (row + x, column) if piece.notation == "P" and abs(piece.row - row) == 2 else None
        if column != piece.column or row != piece.row:
            if not self.is_empty(row, column):
                del self.board[(row, column)]
            self.board[(piece.row, piece.column)], self.board[(row, column)] = self.board[(row, column)], self.board[(piece.row, piece.column)]
            piece.move(row, column)
        # Update the first_move attribute of the piece if it moved
        if piece.notation in "KRP" and piece.first_move:
            piece.first_move = False

    def select_piece(self, row, column):
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
                    self.select_piece(row, column)
                    return
            # If the player clicks on one of his pieces, it will change the selected piece
            if self.is_ally(row, column, self.selected) and (row, column) != (self.selected.row, self.selected.column):
                # Castling move
                if self.selected.notation == "R" and self.get_piece(row, column).notation == "K" and (row, column) in self.selected.moves:
                    self.convert_to_move(row, column).execute()
                    return
                self.selected = None
                self.select_piece(row, column)
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
            self.convert_to_move(row, column).execute()
        else:
            # Not the player's piece
            if self.get_piece(row, column).color != self.turn:
                return
            self.selected = self.get_piece(row, column)
            moves = self.selected.moves
            if self.config.rules["giveaway"] == True and any([self.convert_to_move(*move).is_capture() for move in moves]):
                moves = list(filter(lambda move: self.convert_to_move(*move).is_capture(), moves))
            else:
                moves = list(filter(lambda move: self.convert_to_move(*move).is_legal(), moves))
            self.selected.moves = moves

    def handle_left_click(self):
        x, y = pygame.mouse.get_pos()
        row, column = get_position(x, y, self.config.margin, self.config.tile_size)
        if not self.is_empty(row, column) and self.get_piece(row, column).color == self.turn:
            self.get_piece(row, column).calc_moves(self, row, column, self.flipped, ep_square=self.ep_square)
            self.select_piece(row, column)

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
