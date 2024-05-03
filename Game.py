import Pieces
import Move

from constants import config, window, sign, flip_coords, get_value
from Config import play_sound
from GUI import draw_highlightedSquares, draw_pieces, draw_moves, draw_promotion, draw_board
from random import choice

class Game:
    def __init__(self, gamemode: str = "classic"):
        self.window = window
        self.board = []
        self.turn = 0
        self.selected = None
        self.promotion = None
        self.en_passant = None
        self.flipped = 1
        self.valid_moves = []
        self.halfMoves = 0
        self.fullMoves = 1
        self.history = []
        self.highlightedSquares = {}
        self.game_over = False
        self.win_condition = 0
        self.gamemode = gamemode
        self.debug = False
        if config["state"] == "game":
            customfen = "rnb1kb1r/pppqpppp/5n2/3N2B1/2P5/3P4/PPp1PPPP/R3KBNR w KQkq - 3 7"
            custom2fen = "r3k2r/ppPpp1pp/4B3/8/8/4b3/PPpPP1PP/R3K2R w KQkq - 0 1"
            self.create_board()

    def create_board(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq – 0 1") -> None:
        self.board = [[0] * config["columns"] for _ in range(config["rows"])]
        pieces_fen = {chr([80, 78, 66, 82, 81, 75][i%6] + 32 * (i > 5)): Pieces.Piece.index_to_piece(i%6) for i in range(12)}
        parts = fen.split(' ')
        if self.gamemode == "Chess960":
            last_row = [None] * config["columns"]
            for index, piece in enumerate(["B", "B", "N", "N", "Q", "R", "K", "R"]):
                if index < 2:
                    last_row[choice(range(index, config["columns"], 2))] = piece
                elif index < 5:
                    last_row[choice([i for i, val in enumerate(last_row) if val is None])] = piece
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
                                self.board[row][column] = pieces_fen[char]((2 * (ord(char) < 91) - 1), row, column)
                                column += 1
                case 1:
                    self.turn = int((2 * ord(parts[part])) / 21 - (31 / 3))
                case 2:
                    if "K" not in parts[part] and isinstance(self.board[7][7], Pieces.Rook):
                        self.board[7][7].first_move = False
                    if "Q" not in parts[part] and isinstance(self.board[7][0], Pieces.Rook):
                        self.board[7][0].first_move = False
                    if "k" not in parts[part] and isinstance(self.board[0][7], Pieces.Rook):
                        self.board[0][7].first_move = False
                    if "q" not in parts[part] and isinstance(self.board[0][0], Pieces.Rook):
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
            draw_highlightedSquares({self.history[-1][0].from_: 3, self.history[-1][0].to: 3})
        if self.highlightedSquares:
            draw_highlightedSquares(self.highlightedSquares)
        if config["selected_piece_asset"] != "blindfold":
            draw_pieces(self.board, self.promotion, self.debug)
        if self.valid_moves:
            draw_moves(self.valid_moves)
        if self.promotion:
            draw_promotion(*self.promotion, self.flipped)

    def reset(self):
        self.board = []
        self.selected = None

    def is_king_checked(self) -> bool:
        king = self.get_king(self.turn)
        if king is None and self.gamemode == "Giveaway":
            return False
        return (king.row, king.column) in self.get_color_moves(-self.turn)
    
    def is_checkmate(self):
        return self.is_king_checked() and self.is_stalemate()

    def check_game(self):
        if self.gamemode == "KOTH" and any([isinstance(self.board[row][column], Pieces.King) for row in [3, 4] for column in [3, 4]]):
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.gamemode == "+3 Checks" and self.win_condition >= 3:
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.is_checkmate():
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            self.game_over = True
        elif self.is_stalemate():
            print("Stalemate")
            self.game_over = True
        elif self.halfMoves >= 100:
            print("Draw by the 50 moves rule")
            self.game_over = True
        elif all(not isinstance(self.board[row][column], Pieces.Pawn) for column in range(len(self.board[0])) for row in range(len(self.board))):
            if self.get_color_pieces(self.turn):
                pass
        else:
            pass
            #get the last move that is irreversible
        # TODO for threesold repetition, we can use self.history and check repetitions after the last irreversible moves, irreversible moves are captures, pawn moves, king or rook losing castling rights, castling
        if self.game_over:
            play_sound("game-end")
            
    def get_color_moves(self, color: int):
        return [move for piece in self.get_color_pieces(color) for move in piece.get_available_moves(self.board, piece.row, piece.column, self.flipped, en_passant = self.en_passant)]

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

    def get_king(self, color: int):
        for row in range(len(self.board)):
            for column in range(len(self.board[0])):
                if isinstance(self.board[row][column], Pieces.King) and self.board[row][column].color == color:
                    return self.board[row][column]

    def possible_moves(self, board: list[list[int | Pieces.Piece]]):
        possible_moves = []
        for row in range(len(board)):
            for column in range(len(board[0])):
                if board[row][column] != 0 and board[row][column].color == self.turn and isinstance(board[row][column], Pieces.King):
                    possible_moves += board[row][column].get_available_moves(board, row, column, self.flipped, self.en_passant)
        return possible_moves

    def is_stalemate(self) -> bool:
        return not any([self.is_legal(piece, *move) for piece in self.get_color_pieces(self.turn) for move in piece.get_available_moves(self.board, piece.row, piece.column, self.flipped, en_passant = self.en_passant)])

    def move(self, piece: Pieces.Piece, row: int, column: int):
        x = piece.color * self.flipped
        # Castling
        # TODO the rook disappear in the chess960 order : xRxxxKRx, the rook replace the king and the king is now the void
        if isinstance(piece, Pieces.King) and isinstance(self.board[row][column], Pieces.Rook) and self.board[row][column].color == piece.color:
            # Calculate old and new position of the rook for O-O and O-O-O
            rook_column = (7 + self.flipped + get_value(self.flipped * sign(column - piece.column), 2, -2)) // 2
            self.board[row][rook_column], self.board[row][column] = self.board[row][column], self.board[row][rook_column]
            self.board[row][rook_column].piece_move(row, rook_column)
            column = (7 + self.flipped + get_value(self.flipped * sign(column - piece.column), 4, -4)) // 2
            print("CALCULATED COLUMN", column, "ROOK", rook_column)
        # En-passant
        elif isinstance(piece, Pieces.Pawn) and isinstance(self.board[row + x][column], Pieces.Pawn) and self.en_passant == (piece.row - x, column):
            self.board[row + x][column] = 0
        self.en_passant = (row + x, column) if isinstance(piece, Pieces.Pawn) and abs(piece.row - row) == 2 else None
        self.board[row][column] = 0
        self.board[piece.row][piece.column], self.board[row][column] = self.board[row][column], self.board[piece.row][piece.column]
        piece.piece_move(row, column)
        # Update the first_move attribute of the piece if it moved
        if isinstance(piece, (Pieces.King, Pieces.Rook, Pieces.Pawn)) and piece.first_move:
            piece.first_move = False

    def is_legal(self, piece: Pieces.Piece, row: int, column: int) -> bool:
        is_legal = self.can_move(piece, row, column)
        # Castling
        if isinstance(piece, Pieces.King) and abs(piece.column - column) > 1:
            for next_column in range(piece.column, column, 2 * (piece.column < column) - 1):
                is_legal = is_legal and self.can_move(piece, piece.row, next_column)
                if not is_legal:
                    break
        return is_legal
    
    def can_move(self, piece: Pieces.Piece, row: int, column: int) -> bool:
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
            if isinstance(self.selected, Pieces.Pawn) and self.promotion:
                # Promote the pawn
                if row in range(2*(1 - x), 2*(3 - x)) and column == self.promotion[1] + self.selected.column:
                    move = Move.Move(self, (self.selected.row, self.selected.column), (7 * (1 - x) // 2, column), self.selected, self.board[7 * (1 - x) // 2][column] if self.board[7 * (1 - x) // 2][column] != 0 and self.board[7 * (1 - x) // 2][column].color != self.selected.color else False, [Pieces.Queen, Pieces.Knight, Pieces.Rook, Pieces.Bishop][flip_coords(row, flipped = x)](self.selected.color, 7 * (1 - x) // 2, column))
                    move.make_move()
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
            if self.board[row][column] != 0 and self.board[row][column].color == self.selected.color and (row, column) != (self.selected.row, self.selected.column):
                # Castling move
                if isinstance(self.selected, Pieces.King) and isinstance(self.board[row][column], Pieces.Rook) and self.board[row][column].color == self.selected.color:
                    self.execute_move(row, column)
                    return
                self.selected = None
                self.select(row, column)
                return
            # If the play clicks on the selected piece, the selection is removed
            if (row, column) == (self.selected.row, self.selected.column):
                self.valid_moves = []
                self.selected = None
                return
            # If the player clicks on a square where the selected piece can't move, it will remove the selection
            if (row, column) not in self.valid_moves:
                self.valid_moves = []
                self.selected = None
                if self.is_king_checked():
                    play_sound("illegal")
                return
            # If the player push a pawn to one of the last rows, it will be in the state of promotion
            if isinstance(self.selected, Pieces.Pawn) and row in [0, 7]:
                self.promotion = self.selected, column - self.selected.column
                self.valid_moves = []
                return
            self.execute_move(row, column)
        else:
            piece = self.board[row][column]
            if piece != 0 and self.turn == piece.color:
                self.selected = piece
                moves = set([move for move in piece.get_available_moves(self.board, row, column, self.flipped, en_passant = self.en_passant)])
                if self.gamemode != "Giveaway":
                    moves = list(filter(lambda move: self.is_legal(self.selected, *move), moves))
                elif any([self.board[move[0]][move[1]] != 0 and self.board[move[0]][move[1]].color != piece.color for move in self.get_color_moves(piece.color)]):
                    moves = list(filter(lambda move: self.board[move[0]][move[1]] != 0 and self.board[move[0]][move[1]].color != piece.color, moves))
                self.valid_moves = moves

    def execute_move(self, row: int, column: int):
        x, captured = self.selected.color * self.flipped, False
        if self.board[row][column] != 0:
            captured = self.board[row][column]
        elif isinstance(self.selected, Pieces.Pawn) and isinstance(self.board[row + x][column], Pieces.Pawn) and self.en_passant == (self.selected.row - x, column):
            captured = self.board[row + x][column]
        move = Move.Move(self, (self.selected.row, self.selected.column), (row, column), self.selected, captured, False)
        move.make_move()

    def flip_game(self):
        self.flipped *= -1
        self.selected, self.valid_moves, self.promotion = None, [], None
        if self.en_passant:
            self.en_passant = flip_coords(*self.en_passant)
        if self.history:
            self.history[-1][0].from_, self.history[-1][0].to = flip_coords(*self.history[-1][0].from_), flip_coords(*self.history[-1][0].to)
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
                    # Lowercase characters if piece.color == -1
                    # Uppercase characters if piece.color == 1
                    fen += chr([96, 94, 82, 98, 97, 91][Pieces.Piece.piece_to_index(piece)] - 16 * piece.color)
            if empty_squares > 0:
                fen += str(empty_squares)
            if row < len(self.board) - 1:
                fen += "/"
        # "w" if self.turn == 1
        # "b" if self.turn == -1
        fen += chr(get_value(self.turn, 119, 98))
        castle_rights = ""
        if self.get_king(1) is not None and self.get_king(1).first_move:
            if isinstance(self.board[7][7], Pieces.Rook) and self.board[7][7].first_move:
                castle_rights += "K"
            if isinstance(self.board[7][0], Pieces.Rook) and self.board[7][0].first_move:
                castle_rights += "Q"
        if self.get_king(-1) is not None and self.get_king(-1).first_move:
            if isinstance(self.board[0][7], Pieces.Rook) and self.board[0][7].first_move:
                castle_rights += "k"
            if isinstance(self.board[0][0], Pieces.Rook) and self.board[0][0].first_move:
                castle_rights += "q"
        fen += " " + (castle_rights if castle_rights != "" else "-")
        fen += " " + (chr(97 + flip_coords(self.en_passant[1], flipped = self.flipped)) + str(flip_coords(self.en_passant[0], flipped = -self.flipped) + 1) if self.en_passant else "-")
        fen += " " + str(self.halfMoves)
        fen += " " + str(self.fullMoves)
        return fen
