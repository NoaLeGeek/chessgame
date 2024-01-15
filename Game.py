import Pieces
from Board import Board
from constants import *


class Game:
    def __init__(self, width, height, rows, columns, window):
        self.window = window
        self.board = Board(width, height, rows, columns, window)
        self.turn = 0
        self.create_board()
        self.selected = None
        self.valid_moves = []
        self.black_pieces_left = 16
        self.white_pieces_left = 16
        self.halfMoves = 0
        self.fullMoves = 1
        self.history = []
        self.highlightedSquares = []
        # TODO function that, from a certain position, generate the FEN if asked

    def create_board(self):
        self.board.board = [[0] * columns for _ in range(rows)]
        fen = {
            'p': (Pieces.Pawn, (square_size, piece_assets[selected_piece][6], -1)),
            'n': (Pieces.Knight, (square_size, piece_assets[selected_piece][7], -1)),
            'b': (Pieces.Bishop, (square_size, piece_assets[selected_piece][8], -1)),
            'r': (Pieces.Rook, (square_size, piece_assets[selected_piece][9], -1)),
            'q': (Pieces.Queen, (square_size, piece_assets[selected_piece][10], -1)),
            'k': (Pieces.King, (square_size, piece_assets[selected_piece][11], -1)),
            'P': (Pieces.Pawn, (square_size, piece_assets[selected_piece][0], 1)),
            'N': (Pieces.Knight, (square_size, piece_assets[selected_piece][1], 1)),
            'B': (Pieces.Bishop, (square_size, piece_assets[selected_piece][2], 1)),
            'R': (Pieces.Rook, (square_size, piece_assets[selected_piece][3], 1)),
            'Q': (Pieces.Queen, (square_size, piece_assets[selected_piece][4], 1)),
            'K': (Pieces.King, (square_size, piece_assets[selected_piece][5], 1))
        }
        defaultFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq – 0 1"
        customfen = "8/6P1/7R/8/4p3/4K1kP/r7/3q4 w - - 0 6"
        split = defaultFen.split(' ')
        for i in range(len(split)):
            match i:
                case 0:
                    for j, rang in enumerate(split[i].split('/')):
                        k = 0
                        for char in rang:
                            if char.isdigit():
                                k += int(char)
                            else:
                                self.board.board[j][k] = fen[char][0](*fen[char][1], j, k)
                                k += 1
                case 1:
                    self.turn = 1 if split[i] == 'w' else -1
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
                        self.board.board[int(split[i][1]) + self.turn][ord(split[i][0]) - 97].en_passant = True
                case 4:
                    # TODO you'll have to put halfMoves = 0 every time a pawn is moved or a piece is captured, this is maybe the time to make Move a class to differenciate between a normal move and a capture
                    self.halfMoves = int(split[i])
                case 5:
                    self.fullMoves = int(split[i])

    def update_window(self):
        self.board.draw_board()
        self.board.draw_pieces()
        if self.valid_moves:
            self.board.draw_moves(self.valid_moves)
        for row in range(len(self.board.board)):
            for column in range(len(self.board.board[0])):
                if isinstance(self.board.board[row][column], Pieces.Pawn) and self.board.board[row][column].promotion[0]:
                    self.board.draw_promotion(self.board.board[row][column], self.board.board[row][column].promotion[1])
        #self.board.draw_test()
        pygame.display.update()

    def reset(self, frame):
        self.board = Board(width, height, rows, columns, frame)
        self.selected = None

    def is_king_checked(self):
        return self.get_king_position(self.turn) in self.get_color_moves(-self.turn)

    def check_game(self):
        if self.black_pieces_left == 0:
            print("Whites win")
            return True
        elif self.white_pieces_left == 0:
            print("Blacks win")
            return True
        elif self.is_king_checked() and self.is_stalemate():
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            return True
        elif self.is_stalemate():
            print("Stalemate")
            return True
        #TODO enabled the 50 moves rule when it's done
        #elif self.halfMoves >= 100:
            #print("Draw by the 50 moves rule")
            #return True
        # TODO for threesold repetition, we can use self.history and check repetitions after the last irreversible moves, irreversible moves are captures, pawn moves, king or rook losing castling rights, castling


    def get_color_moves(self, color: int):
        color_moves = []
        for row in range(len(self.board.board)):
            for column in range(len(self.board.board[0])):
                if self.board.board[row][column] != 0 and self.board.board[row][column].color == color:
                    color_moves += self.board.board[row][column].get_available_moves(self.board.board, row, column)
        return color_moves

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

    def get_king_position(self, color: int):
        for row in range(len(self.board.board)):
            for column in range(len(self.board.board[0])):
                if self.board.board[row][column] != 0 and isinstance(self.board.board[row][column], Pieces.King) and self.board.board[row][column].color == color:
                    return row, column

    def possible_moves(self, board: list[list[int | Pieces.Piece]]):
        possible_moves = []
        for row in range(len(board)):
            for column in range(len(board[0])):
                if board[row][column] != 0 and board[row][column].color == self.turn and isinstance(board[row][column], Pieces.King):
                    possible_moves += board[row][column].get_available_moves(board, row, column)
        return possible_moves

    def is_stalemate(self) -> bool:
        return not any([self.can_move(piece, move[0], move[1]) for piece in self.get_color_pieces(self.turn) for move in piece.get_available_moves(self.board.board, piece.row, piece.column)])

    def remove(self, piece: Pieces.Piece, row: int, column: int):
        if piece != 0:
            self.board.board[row][column] = 0
            if piece.color == 1:
                self.white_pieces_left -= 1
            else:
                self.black_pieces_left -= 1

    def move(self, piece: Pieces.Piece, row: int, column: int):
        piece.en_passant = (isinstance(piece, Pieces.Pawn) and abs(piece.row - row) == 2)
        if isinstance(piece, Pieces.King) and abs(piece.column - column) == 2 and not self.is_king_checked():
            if column == 6:
                self.board.board[row][5], self.board.board[row][7] = self.board.board[row][7], self.board.board[row][5]
                self.board.board[row][5].piece_move(row, 5)
            else:
                self.board.board[row][3], self.board.board[row][0] = self.board.board[row][0], self.board.board[row][3]
                self.board.board[row][3].piece_move(row, 3)
            piece.not_castled = False
        if isinstance(piece, Pieces.Pawn) and self.board.board[row + piece.color][column] != 0 and \
                self.board.board[row + piece.color][column].en_passant:
            self.board.board[row + piece.color][column] = 0
        self.board.board[piece.row][piece.column], self.board.board[row][column] = self.board.board[row][column], \
            self.board.board[piece.row][piece.column]
        piece.piece_move(row, column)
        if isinstance(piece, (Pieces.King, Pieces.Rook, Pieces.Pawn)) and piece.first_move:
            piece.first_move = False
        for row in range(rows):
            for column in range(columns):
                if self.board.board[row][column] != 0 and isinstance(self.board.board[row][column], Pieces.Pawn) and self.board.board[row][column].en_passant and self.board.board[row][column].color != piece.color:
                    self.board.board[row][column].en_passant = False

    def can_move(self, piece: Pieces.Piece, row: int, column: int) -> bool:
        if isinstance(piece, Pieces.King) and abs(piece.column - column) == 2:
            return (row, column + (piece.column - column > 0) - (piece.column - column < 0)) not in self.get_color_moves(-piece.color) and not self.is_king_checked()
        else:
            piece_row, piece_column = piece.row, piece.column
            save_piece = self.board.board[row][column]
            if self.board.board[row][column] != 0:
                self.board.board[row][column] = 0
            self.board.board[piece.row][piece.column], self.board.board[row][column] = self.board.board[row][column], self.board.board[piece.row][piece.column]
            is_checked = self.is_king_checked()
            piece.row, piece.column = piece_row, piece_column
            self.board.board[piece_row][piece_column] = piece
            self.board.board[row][column] = save_piece
            return not is_checked

    def select(self, row, column):
        if self.selected:
            # If the player clicks on one of his pieces, it will change the selected piece
            if self.board.board[row][column] != 0 and self.board.board[row][column].color == self.selected.color:
                self.selected = None
                self.select(row, column)
                return
            # If the player clicks on a square where the selected piece can't move, it will remove the selection
            if (row, column) not in self.valid_moves:
                self.valid_moves = []
                self.selected = None
                return
            self.make_move(row, column)
        else:
            piece = self.board.board[row][column]
            if piece != 0 and self.turn == piece.color:
                self.selected = piece
                # TODO /!\ NEEDS to be optimised, needs to remove all moves that are not in the "Cross pin" if there is one, see chessprogramming.org/Pin
                self.valid_moves = [move for move in piece.get_available_moves(self.board.board, row, column) if self.can_move(self.selected, move[0], move[1])]

    def make_move(self, row, column):
        piece = self.board.board[row][column]
        # TODO maybe move this part to self.select()?
        if isinstance(self.selected, Pieces.Pawn) and row in [0, 7]:
            self.selected.promotion = (True, column - self.selected.column)
            self.valid_moves = []
            return False
        self.remove(piece, row, column)
        self.move(self.selected, row, column)
        self.change_turn()
        print("turn", self.turn)
        self.valid_moves = []
        self.selected = None
        return True

    def get_board(self):
        return self.board
