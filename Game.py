import Move

from constants import config, window, sign, flip_coords, get_value
from Config import play_sound
from GUI import draw_highlightedSquares, draw_pieces, draw_moves, draw_promotion, draw_board
from random import choice
from Pieces import Piece, King, Rook, Pawn, Queen, Knight, Bishop

class Game:
    def __init__(self, gamemode: str = "classic"):
        self.window = window
        self.board = []
        self.turn = 0
        self.selected = None
        self.promotion = None
        self.en_passant = None
        self.flipped = 1
        self.legal_moves = []
        self.halfMoves = 0
        self.fullMoves = 1
        self.history = []
        self.highlightedSquares = {}
        self.game_over = False
        self.gamemode = gamemode
        if gamemode == "+3 Checks":
            self.win_condition = 0
        self.debug = False
        if config["state"] == "game":
            self.create_board()

    def create_board(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq – 0 1") -> None:
        self.board = [[0] * config["columns"] for _ in range(config["rows"])]
        pieces_fen = {chr([80, 78, 66, 82, 81, 75][i%6] + 32 * (i > 5)): Piece.index_to_piece(i%6) for i in range(12)}
        parts = fen.split(' ')
        if self.gamemode == "Chess960":
            last_row = [None]*len(self.board[0])
            for index, piece in enumerate(["B", "B", "N", "N", "Q", "R", "K", "R"]):
                # Bishops
                if index < 2:
                    last_row[choice(range(index, len(self.board[0]), 2))] = piece
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
        for part in range(len(parts)):
            match part:
                case 0:
                    for row, string in enumerate(parts[part].split("/")):
                        column = 0
                        for char in string:
                            if char.isdigit():
                                column += int(char)
                            else:
                                self.board[row][column] = pieces_fen[char]((1 if ord(char) < 91 else -1), row, column)
                                column += 1
                case 1:
                    self.turn = 1 if parts[part] == "w" else -1
                case 2:
                    # TODO dont work in 960
                    if "K" not in parts[part] and isinstance(self.board[7][7], Rook):
                        self.board[7][7].first_move = False
                    if "Q" not in parts[part] and isinstance(self.board[7][0], Rook):
                        self.board[7][0].first_move = False
                    if "k" not in parts[part] and isinstance(self.board[0][7], Rook):
                        self.board[0][7].first_move = False
                    if "q" not in parts[part] and isinstance(self.board[0][0], Rook):
                        self.board[0][0].first_move = False
                case 3:
                    if parts[part] not in ['-', '–']:
                        self.en_passant = (flip_coords(int(parts[part][1]) - 1, flipped = -self.flipped), flip_coords(ord(parts[part][0]) - 97, flipped = self.flipped))
                case 4:
                    self.halfMoves = int(parts[part])
                case 5:
                    self.fullMoves = int(parts[part])
        play_sound("game-start")

    def update_window(self):
        draw_board(self.flipped)
        if self.selected:
            draw_highlightedSquares({(self.selected.row, self.selected.column): 4})
        if self.history:
            draw_highlightedSquares({self.history[-1].from_: 3, self.history[-1].to: 3})
        if self.highlightedSquares:
            draw_highlightedSquares(self.highlightedSquares)
        if config["selected_piece_asset"] != "blindfold":
            draw_pieces(self.board, self.promotion, self.debug)
        if self.legal_moves:
            draw_moves(self.legal_moves)
        if self.promotion:
            draw_promotion(*self.promotion, self.flipped)

    def is_king_checked(self) -> bool:
        king = self.get_piece(self.turn, King)
        if king is None and self.gamemode == "Giveaway":
            return False
        return (king.row, king.column) in self.get_color_moves(-self.turn)
    
    def is_checkmate(self):
        return self.is_king_checked() and self.is_stalemate()

    def check_game(self):
        if self.gamemode == "KOTH" and any([isinstance(self.board[row][column], King) for row in [3, 4] for column in [3, 4]]):
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.gamemode == "+3 Checks" and self.win_condition >= 3:
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.gamemode == "Giveaway" and (any([self.dict_color_pieces(color) == dict() for color in [1, -1]]) or self.is_stalemate()):
            print("{} Wins".format("Black" if self.turn == -1 else "White"))
            self.game_over = True
        elif self.gamemode != "Giveaway" and self.is_checkmate():
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
        else:
            last_index = 0
            for i in range(len(self.history)-1, 0, -1):
                move = self.history[i]
                # Irreversible move are captures, pawn moves, castling or losing castling rights
                if move.capture or isinstance(move.piece, Pawn) or self.is_castling(move.piece, *move.to) or move.fen.split(" ")[2] != self.history[i-1].fen.split(" ")[2]:
                    last_index = i
                    break
            print("last_index_found", last_index)
            for i in range(last_index, len(self.history)):
                fen = self.history[i].fen.split(" ")
                count = 0
                for j in range(last_index, len(self.history)):
                    iterate_fen = self.history[j].fen.split(" ")
                    # Two positions are the same if the pieces are in the same position, if it's the same player to play, if the castling rights are the same and if the en passant square is the same
                    if all([iterate_fen[k] == fen[k] for k in range(4)]):
                        count += 1
                        if count == 3:
                            break
                if count == 3:
                    self.game_over = True
                    print("Draw by threesold repetition")
                    break
        if self.game_over:
            play_sound("game-end")
            
    def get_color_moves(self, color: int):
        return [move for piece in self.get_color_pieces(color) for move in piece.get_available_moves(self.board, piece.row, piece.column, self.flipped, en_passant = self.en_passant)]
    
    def is_insufficient_material(self):
        return (self.count_pieces() == 2) or (self.count_pieces() == 3 and (any([self.dict_color_pieces(color * self.turn).get(Bishop, 0) == 1 for color in [-1, 1]]) or any([self.dict_color_pieces(color * self.turn).get(Knight, 0) == 1 for color in [-1, 1]]))) or (self.count_pieces() == 4 and all([self.dict_color_pieces(color * self.turn).get(Bishop, 0) == 1 for color in [-1, 1]]) and self.get_piece(self.turn, Bishop).get_square_color() == self.get_piece(-self.turn, Bishop).get_square_color())

    def get_color_pieces(self, color: int):
        color_pieces = []
        for row in range(len(self.board)):
            for column in range(len(self.board[0])):
                piece = self.board[row][column]
                if piece != 0 and piece.color == color:
                    color_pieces.append(piece)
        return color_pieces

    def change_turn(self):
        if self.turn == -1:
            self.fullMoves += 1
        self.turn *= -1
        self.halfMoves += 1
        print("turn", self.turn)

    def get_piece(self, color: int, piece: Piece):
        for row in range(len(self.board)):
            for column in range(len(self.board[0])):
                if isinstance(self.board[row][column], piece) and self.board[row][column].color == color:
                    return self.board[row][column]

    def is_stalemate(self) -> bool:
        return not any([self.is_legal(piece, *move) for piece in self.get_color_pieces(self.turn) for move in piece.get_available_moves(self.board, piece.row, piece.column, self.flipped, en_passant = self.en_passant)])
    
    def is_castling(self, piece: Piece, row: int, column: int):
        return isinstance(piece, King) and isinstance(self.board[row][column], Rook) and self.board[row][column].is_ally(piece)

    def move(self, move: Move.Move):
        piece, row, column = move.piece, *move.to
        x = piece.color * self.flipped
        # Castling
        if self.is_castling(move.piece, *move.to):
            s = sign(column - piece.column)
            # Rook and King's positions are swapped to avoid King's deletion during some 960 castling
            # King is now at (row, column)
            # Rook is now at (row, piece.column)
            self.board[row][column], self.board[row][piece.column] = self.board[row][piece.column], self.board[row][column]
            # Calculate the new position for the rook
            rook_column = (7 + self.flipped + get_value(s, 2, -2)) // 2
            # piece.column hasn't updated, we can use it as the old King's pos
            self.board[row][piece.column].piece_move(row, rook_column)
            self.board[row][piece.column], self.board[row][rook_column] = self.board[row][rook_column], self.board[row][piece.column]
            # King's pos is updated
            self.board[row][column].piece_move(row, column)
            # Calculate the new position for the king
            column = (7 + self.flipped + get_value(s, 4, -4)) // 2
        # En-passant
        elif isinstance(piece, Pawn) and isinstance(self.board[row + x][column], Pawn) and self.en_passant == (piece.row - x, column):
            self.board[row + x][column] = 0
        self.en_passant = (row + x, column) if isinstance(piece, Pawn) and abs(piece.row - row) == 2 else None
        if column != piece.column or row != piece.row:
            self.board[row][column] = 0
            self.board[piece.row][piece.column], self.board[row][column] = self.board[row][column], self.board[piece.row][piece.column]
            piece.piece_move(row, column)
        # Update the first_move attribute of the piece if it moved
        if isinstance(piece, (King, Rook, Pawn)) and piece.first_move:
            piece.first_move = False

    def is_legal(self, piece: Piece, row: int, column: int) -> bool:
        is_legal = self.can_move(piece, row, column)
        # Castling
        if self.is_castling(piece, row, column):
            if self.is_king_checked() or self.gamemode == "Giveaway":
                return False
            for next_column in range(piece.column, column, 2 * (piece.column < column) - 1):
                is_legal = is_legal and self.can_move(piece, piece.row, next_column)
                if not is_legal:
                    break
        return is_legal
    
    def count_pieces(self):
        return len(self.get_color_pieces(1)) + len(self.get_color_pieces(-1))
    
    def can_move(self, piece: Piece, row: int, column: int) -> bool:
        if (piece.row, piece.column) == (row, column):
            return True
        piece_row, piece_column = piece.row, piece.column
        save_piece = self.board[row][column]
        if self.board[row][column] != 0:
            self.board[row][column] = 0
        self.board[piece.row][piece.column], self.board[row][column] = self.board[row][column], self.board[piece.row][piece.column]
        piece.row, piece.column = row, column
        can_move = not self.is_king_checked()
        self.board[piece_row][piece_column] = piece
        self.board[row][column] = save_piece
        piece.row, piece.column = piece_row, piece_column
        return can_move
        
    def select(self, row: int, column: int):
        if self.selected:
            x = self.selected.color * self.flipped
            # If in the state of promotion
            if isinstance(self.selected, Pawn) and self.promotion:
                # Promote the pawn
                if row in range(get_value(x, 0, 4), get_value(x, 4, 8)) and column == self.promotion[1] + self.selected.column:
                    promotion_row = get_value(x, 0, 7)
                    self.execute_move(promotion_row, column, ([Queen, Knight, Rook, Bishop][flip_coords(row, flipped = x)] if self.gamemode != "Giveway" else King)(self.selected.color, promotion_row, column))
                    self.promotion = None
                    return
                # Remove the promotion
                self.promotion = None
                # Reselect the pawn if clicked
                if (row, column) == (self.selected.row, self.selected.column):
                    self.selected = None
                    self.select(row, column)
                    return
            # If the player clicks on one of his pieces, it will change the selected piece
            if self.board[row][column] != 0 and self.board[row][column].is_ally(self.selected) and (row, column) != (self.selected.row, self.selected.column):
                # Castling move
                if isinstance(self.selected, King) and isinstance(self.board[row][column], Rook) and self.board[row][column].is_ally(self.selected) and (row, column) in self.legal_moves:
                    self.execute_move(row, column)
                    return
                self.selected = None
                self.select(row, column)
                return
            # If the play clicks on the selected piece, the selection is removed
            if (row, column) == (self.selected.row, self.selected.column):
                self.legal_moves = []
                self.selected = None
                return
            # If the player clicks on a square where the selected piece can't move, it will remove the selection
            if (row, column) not in self.legal_moves:
                self.legal_moves = []
                self.selected = None
                if self.is_king_checked():
                    play_sound("illegal")
                return
            # If the player push a pawn to one of the last rows, it will be in the state of promotion
            if isinstance(self.selected, Pawn) and row in [0, 7]:
                self.promotion = self.selected, column - self.selected.column
                self.legal_moves = []
                return
            self.execute_move(row, column)
        else:
            piece = self.board[row][column]
            if piece != 0 and self.turn == piece.color:
                self.selected = piece
                moves = set([move for move in piece.get_available_moves(self.board, row, column, self.flipped, en_passant = self.en_passant)])
                if self.gamemode != "Giveaway":
                    moves = list(filter(lambda move: self.is_legal(self.selected, *move), moves))
                elif any([self.board[move[0]][move[1]] != 0 and self.board[move[0]][move[1]].is_enemy(piece) for move in self.get_color_moves(piece.color)]):
                    moves = list(filter(lambda move: self.board[move[0]][move[1]] != 0 and self.board[move[0]][move[1]].is_enemy(piece), moves))
                self.legal_moves = moves

    def execute_move(self, row: int, column: int, promotion: bool | Piece = False):
        x, captured = self.selected.color * self.flipped, False
        if self.board[row][column] != 0:
            captured = self.board[row][column]
        elif isinstance(self.selected, Pawn) and isinstance(self.board[row + x][column], Pawn) and self.en_passant == (self.selected.row - x, column):
            captured = self.board[row + x][column]
        move = Move.Move(self, (self.selected.row, self.selected.column), (row, column), self.selected, captured, promotion)
        move.make_move()

    def flip_game(self):
        self.flip_board()
        self.flipped *= -1
        self.selected, self.legal_moves, self.promotion = None, [], None
        if self.en_passant:
            self.en_passant = flip_coords(*self.en_passant)
        if self.history:
            self.history[-1].from_, self.history[-1].to = flip_coords(*self.history[-1].from_), flip_coords(*self.history[-1].to)
            self.highlightedSquares = {flip_coords(row, column): value for ((row, column), value) in self.highlightedSquares.items()}
            
    def flip_board(self):
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                piece = self.board[row][column]
                if piece != 0:
                    piece.piece_move(*flip_coords(piece.row, piece.column, flipped = -1))
        for row in self.board:
            row.reverse()
        self.board.reverse()

    def dict_color_pieces(self, color: int):
        groups = {}
        for piece in self.get_color_pieces(color):
            if type(piece) in groups.keys():
                groups[type(piece)] += 1
            else:
                groups[type(piece)] = 1
        return groups

    def generate_fen(self):
        fen = ""
        for row in range(len(self.board)):
            empty_squares = 0
            for column in range(len(self.board[0])):
                piece = self.board[row][column]
                if piece == 0:
                    empty_squares += 1
                else:
                    if empty_squares > 0:
                        fen += str(empty_squares)
                        empty_squares = 0
                    char = ["p", "n", "b", "r", "q", "k"][Piece.piece_to_index(piece)]
                    fen += (char if piece.is_black() else char.upper())
            if empty_squares > 0:
                fen += str(empty_squares)
            if row < len(self.board) - 1:
                fen += "/"
        fen += " " + ("w" if self.turn == 1 else "b")
        castle_rights = ""
        white_king = self.get_piece(1, King)
        if white_king is not None and white_king.first_move:
            if next((self.board[white_king.row][i] for i in range(white_king.column - self.flipped, flip_coords(-1, flipped=self.flipped), -self.flipped) if isinstance(self.board[white_king.row][i], Rook) and self.board[white_king.row][i].first_move), None) is not None:
                castle_rights += "K"
            if next((self.board[white_king.row][i] for i in range(white_king.column + self.flipped, flip_coords(8, flipped = self.flipped), self.flipped) if isinstance(self.board[white_king.row][i], Rook) and self.board[white_king.row][i].first_move), None) is not None:
                castle_rights += "Q"
        black_king = self.get_piece(-1, King)
        if black_king is not None and black_king.first_move:
            if next((self.board[black_king.row][i] for i in range(black_king.column - self.flipped, flip_coords(-1, flipped=self.flipped), -self.flipped) if isinstance(self.board[black_king.row][i], Rook) and self.board[black_king.row][i].first_move), None) is not None:
                castle_rights += "k"
            if next((self.board[black_king.row][i] for i in range(black_king.column + self.flipped, flip_coords(8, flipped = self.flipped), self.flipped) if isinstance(self.board[black_king.row][i], Rook) and self.board[black_king.row][i].first_move), None) is not None:
                castle_rights += "q"
        fen += " " + (castle_rights if castle_rights != "" else "-")
        can_en_passant = bool(self.en_passant)
        if can_en_passant:
            x = ((7-2*self.en_passant[0])//3)
            r, c = self.en_passant
            if not any([isinstance(self.board[r + x][c + i], Pawn) and self.board[r + x][c + i].color == x*self.flipped for i in [-1, 1]]):
                can_en_passant = False
        fen += " " + (chr(97 + flip_coords(self.en_passant[1], flipped = self.flipped)) + str(flip_coords(self.en_passant[0], flipped = -self.flipped) + 1) if can_en_passant else "-")
        fen += " " + str(self.halfMoves)
        fen += " " + str(self.fullMoves)
        return fen
