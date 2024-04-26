import Pieces
from Board import Board
import constants
import pygame
import Move
import Menu


class Game:
    def __init__(self, width: int, height: int, rows: int, columns: int, window: pygame.Surface):
        self.window = window
        self.board = Board(width, height, rows, columns, window)
        self.turn = 0
        self.selected = None
        self.promotion = None
        self.en_passant = None
        self.flipped = -1
        self.valid_moves = []
        self.black_pieces_left = 16
        self.white_pieces_left = 16
        self.halfMoves = 0
        self.fullMoves = 1
        self.history = []
        self.highlightedSquares = {}
        self.game_over = False
        self.state = "main_menu"
        if self.state == "game":
            customfen = "rnb1kb1r/pppqpppp/5n2/3N2B1/2P5/3P4/PPp1PPPP/R3KBNR w KQkq - 3 7"
            custom2fen = "r3k2r/ppPpp1pp/4B3/8/8/4b3/PPpPP1PP/R3K2R w KQkq - 0 1"
            self.create_board()

    def create_board(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq – 0 1") -> None:
        self.board.board = [[0] * constants.columns for _ in range(constants.rows)]
        fen = {(['p', 'n', 'b', 'r', 'q', 'k'] if i > 5 else ['P', 'N', 'B', 'R', 'Q', 'K'])[i%6]: Pieces.Piece.index_to_piece(i%6) for i in range(12)}
        split = fen.split(' ')
        for i in range(len(split)):
            match i:
                case 0:
                    for j, rang in enumerate(split[i].split('/')):
                        k = 0
                        for char in rang:
                            if char.isdigit():
                                k += int(char)
                            else:
                                self.board.board[j][k] = fen[char]((1 if ord(char) < 91 else -1), j, k)
                                k += 1
                case 1:
                    self.turn = int((2 * ord(split[i])) / 21 - (31 / 3))
                case 2:
                    if "K" not in split[i] and isinstance(self.board.board[7][7], Pieces.Rook):
                        self.board.board[7][7].first_move = False
                    if "Q" not in split[i] and isinstance(self.board.board[7][0], Pieces.Rook):
                        self.board.board[7][0].first_move = False
                    if "k" not in split[i] and isinstance(self.board.board[0][7], Pieces.Rook):
                        self.board.board[0][7].first_move = False
                    if "q" not in split[i] and isinstance(self.board.board[0][0], Pieces.Rook):
                        self.board.board[0][0].first_move = False
                case 3:
                    if split[i] not in ['-', '–']:
                        self.en_passant = (constants.flip_coords(int(split[i][1]) - 1, flipped = -self.flipped), constants.flip_coords(ord(split[i][0]) - 97, flipped = self.flipped))
                case 4:
                    self.halfMoves = int(split[i])
                case 5:
                    self.fullMoves = int(split[i])
        self.board.play_sound("game-start")

    def update_window(self):
        self.board.draw_background()
        match self.state:
            case "main_menu":
                Menu.MAIN_MENU.draw_menu(self.window)
            case "game":
                self.board.draw_board()
                if self.selected:
                    self.board.draw_highlightedSquares({(self.selected.row, self.selected.column): 4})
                if self.history:
                    self.board.draw_highlightedSquares({self.history[-1][0].from_: 3, self.history[-1][0].to: 3})
                if self.highlightedSquares:
                    self.board.draw_highlightedSquares(self.highlightedSquares)
                if constants.selected_piece_asset != "blindfold":
                    self.board.draw_pieces(self.promotion)
                if self.valid_moves:
                    self.board.draw_moves(self.valid_moves)
                if self.promotion:
                    self.board.draw_promotion(*self.promotion, self.flipped)
        pygame.display.update()

    def reset(self, frame: pygame.Surface):
        self.board = Board(constants.width, constants.height, constants.rows, constants.columns, frame)
        self.selected = None

    def is_king_checked(self) -> bool:
        king = self.get_king(self.turn)
        return (king.row, king.column) in self.get_color_moves(-self.turn)
    
    def is_checkmate(self):
        return self.is_king_checked() and self.is_stalemate()

    def check_game(self):
        if self.black_pieces_left == 0:
            print("Whites win")
            self.game_over = True
        elif self.white_pieces_left == 0:
            print("Blacks win")
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
        elif all(not isinstance(self.board.board[row][column], Pieces.Pawn) for column in range(len(self.board.board[0])) for row in range(len(self.board.board))):
            if self.get_color_pieces(self.turn):
                pass
        else:
            pass
            #get the last move that is irreversible
        # TODO for threesold repetition, we can use self.history and check repetitions after the last irreversible moves, irreversible moves are captures, pawn moves, king or rook losing castling rights, castling
        if self.game_over:
            self.board.play_sound("game-end")
            
    def get_color_moves(self, color: int):
        return [move for piece in self.get_color_pieces(color) for move in piece.get_available_moves(self.board.board, piece.row, piece.column, self.flipped, en_passant = self.en_passant)]

    def get_color_pieces(self, color: int):
        color_pieces = []
        for row in range(len(self.board.board)):
            for column in range(len(self.board.board[0])):
                piece = self.board.board[row][column]
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
        for row in range(len(self.board.board)):
            for column in range(len(self.board.board[0])):
                if isinstance(self.board.board[row][column], Pieces.King) and self.board.board[row][column].color == color:
                    return self.board.board[row][column]

    def possible_moves(self, board: list[list[int | Pieces.Piece]]):
        possible_moves = []
        for row in range(len(board)):
            for column in range(len(board[0])):
                if board[row][column] != 0 and board[row][column].color == self.turn and isinstance(board[row][column], Pieces.King):
                    possible_moves += board[row][column].get_available_moves(board, row, column, self.flipped, self.en_passant)
        return possible_moves

    def is_stalemate(self) -> bool:
        return not any([self.can_move(piece, move[0], move[1]) for piece in self.get_color_pieces(self.turn) for move in piece.get_available_moves(self.board.board, piece.row, piece.column, self.flipped, en_passant = self.en_passant)])

    def remove(self, row: int, column: int):
        piece = self.board.board[row][column]
        if piece != 0:
            self.board.board[row][column] = 0
            if piece.color == 1:
                self.white_pieces_left -= 1
            else:
                self.black_pieces_left -= 1

    def move(self, piece: Pieces.Piece, row: int, column: int):
        x = piece.color * -self.flipped
        # Castling
        if isinstance(piece, Pieces.King) and abs(piece.column - column) == 2 and not self.is_king_checked():
            # Calculate old and new position of the rook for O-O and O-O-O
            new_rook_pos, old_rook_pos = (2 * column + 7 - self.flipped) // 4, (7 * (2 * column - 3 + self.flipped)) // 8
            self.board.board[row][new_rook_pos], self.board.board[row][old_rook_pos] = self.board.board[row][old_rook_pos], self.board.board[row][new_rook_pos]
            self.board.board[row][new_rook_pos].piece_move(row, new_rook_pos)
            piece.not_castled = False
        # En-passant
        if isinstance(piece, Pieces.Pawn) and isinstance(self.board.board[row + x][column], Pieces.Pawn) and self.en_passant == (piece.row - x, column):
            self.board.board[row + x][column] = 0
        self.en_passant = (row + x, column) if isinstance(piece, Pieces.Pawn) and abs(piece.row - row) == 2 else None
        self.board.board[piece.row][piece.column], self.board.board[row][column] = self.board.board[row][column], self.board.board[piece.row][piece.column]
        piece.piece_move(row, column)
        # Update the first_move attribute of the piece if it moved
        if isinstance(piece, (Pieces.King, Pieces.Rook, Pieces.Pawn)) and piece.first_move:
            piece.first_move = False

    def can_move(self, piece: Pieces.Piece, row: int, column: int) -> bool:
        piece_row, piece_column = piece.row, piece.column
        save_piece = self.board.board[row][column]
        if self.board.board[row][column] != 0:
            self.board.board[row][column] = 0
        self.board.board[piece.row][piece.column], self.board.board[row][column] = self.board.board[row][column], self.board.board[piece.row][piece.column]
        piece.row, piece.column = row, column
        can_move = not self.is_king_checked()
        piece.row, piece.column = piece_row, piece_column
        self.board.board[piece_row][piece_column] = piece
        self.board.board[row][column] = save_piece
        if isinstance(piece, Pieces.King) and abs(piece.column - column) == 2 and can_move:
            piece_row, piece_column = piece.row, piece.column
            next_column = column + (((piece.column - column) * -self.flipped) // 2)
            self.board.board[piece.row][piece.column], self.board.board[row][next_column] = self.board.board[row][next_column], self.board.board[piece.row][piece.column]
            piece.row, piece.column = row, next_column
            can_move = can_move and not self.is_king_checked()
            piece.row, piece.column = piece_row, piece_column
            self.board.board[piece_row][piece_column] = piece
            self.board.board[row][next_column] = 0
        return can_move

    def select(self, row: int, column: int):
        if self.selected:
            x = self.selected.color * -self.flipped
            # If in the state of promotion
            if isinstance(self.selected, Pieces.Pawn) and self.promotion:
                # Promote the pawn
                if row in range(2*(1 - x), 2*(3 - x)) and column == self.promotion[1] + self.selected.column:
                    move = Move.Move(self, (self.selected.row, self.selected.column), (7 * (1 - x) // 2, column), self.selected, self.board.board[7 * (1 - x) // 2][column] if self.board.board[7 * (1 - x) // 2][column] != 0 and self.board.board[7 * (1 - x) // 2][column].color != self.selected.color else False, [Pieces.Queen, Pieces.Knight, Pieces.Rook, Pieces.Bishop][constants.flip_coords(row, flipped = -x)](self.selected.color, 7 * (1 - x) // 2, column))
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
            if self.board.board[row][column] != 0 and self.board.board[row][column].color == self.selected.color and (row, column) != (self.selected.row, self.selected.column):
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
                    self.board.play_sound("illegal")
                return
            # If the player push a pawn to one of the last rows, it will be in the state of promotion
            if isinstance(self.selected, Pieces.Pawn) and row in [0, 7]:
                self.promotion = self.selected, column - self.selected.column
                self.valid_moves = []
                return
            captured = False
            if self.board.board[row][column] != 0 and self.board.board[row][column].color != self.selected.color:
                captured = self.board.board[row][column]
            elif isinstance(self.selected, Pieces.Pawn) and isinstance(self.board.board[row + x][column], Pieces.Pawn) and self.en_passant == (self.selected.row - x, column):
                captured = self.board.board[row + x][column]
            move = Move.Move(self, (self.selected.row, self.selected.column), (row, column), self.selected, captured, False)
            move.make_move()
        else:
            piece = self.board.board[row][column]
            if piece != 0 and self.turn == piece.color:
                self.selected = piece
                # TODO /!\ NEEDS to be optimised, needs to remove all moves that are not in the "Cross pin" if there is one, see chessprogramming.org/Pin
                self.valid_moves = [move for move in piece.get_available_moves(self.board.board, row, column, self.flipped, en_passant = self.en_passant) if self.can_move(self.selected, *move)]

    def flip_game(self):
        self.flipped *= -1
        self.selected, self.valid_moves, self.promotion = None, [], None
        if self.en_passant:
            self.en_passant = constants.flip_coords(*self.en_passant)
        if self.history:
            self.history[-1][0].from_, self.history[-1][0].to = constants.flip_coords(*self.history[-1][0].from_), constants.flip_coords(*self.history[-1][0].to)
            self.highlightedSquares = {constants.flip_coords(row, column): value for ((row, column), value) in self.highlightedSquares.items()}

    def generate_fen(self):
        fen = ""
        for row in range(len(self.board.board)):
            empty_squares = 0
            for column in range(len(self.board.board[0])):
                piece = self.board.board[row][column]
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
            if row < len(self.board.board) - 1:
                fen += "/"
        # "w" if self.turn == 1
        # "b" if self.turn == -1
        fen += chr((21 * self.turn + 217) // 2)
        castle_rights = " "
        if self.get_king(1).first_move and isinstance(self.board.board[7][7], Pieces.Rook) and self.board.board[7][7].first_move:
            castle_rights += "K"
        if self.get_king(1).first_move and isinstance(self.board.board[7][0], Pieces.Rook) and self.board.board[7][0].first_move:
            castle_rights += "Q"
        if self.get_king(-1).first_move and isinstance(self.board.board[0][7], Pieces.Rook) and self.board.board[0][7].first_move:
            castle_rights += "k"
        if self.get_king(-1).first_move and isinstance(self.board.board[0][0], Pieces.Rook) and self.board.board[0][0].first_move:
            castle_rights += "q"
        fen += castle_rights if castle_rights else "-"
        fen += " " + (chr(97 + constants.flip_coords(self.en_passant[1], flipped = self.flipped)) + str(constants.flip_coords(self.en_passant[0], flipped = -self.flipped) + 1)) if self.en_passant else "-"
        fen += " " + str(self.halfMoves) + " " + str(self.fullMoves)
        return fen
