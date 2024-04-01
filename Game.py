import Pieces
from Board import Board
from constants import *
import Move


class Game:
    def __init__(self, width, height, rows, columns, window):
        self.window = window
        self.board = Board(width, height, rows, columns, window)
        self.turn = 0
        self.create_board()
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
        # TODO function that, from a certain position, generate the FEN if asked

    def create_board(self):
        self.board.board = [[0] * columns for _ in range(rows)]
        fen = {(['p', 'n', 'b', 'r', 'q', 'k'] if i > 5 else ['P', 'N', 'B', 'R', 'Q', 'K'])[i%6]: Pieces.Piece.index_to_piece(i%6) for i in range(12)}
        defaultfen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq – 0 1"
        customfen = "rnb1kb1r/pppqpppp/5n2/3N2B1/2P5/3P4/PPp1PPPP/R3KBNR w KQkq - 3 7"
        split = customfen.split(' ')
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
                                pie = self.board.board[j][k]
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
                        self.en_passant = (flip_coord(-self.flipped, int(split[i][1])) + self.turn + 1, ord(flip_coord(self.flipped, split[i][0])) - 97)
                case 4:
                    self.halfMoves = int(split[i])
                case 5:
                    self.fullMoves = int(split[i])

    def update_window(self):
        self.board.draw_background()
        self.board.draw_board()
        if self.history:
            self.board.draw_highlightedSquares({flip_coords(self.flipped, *self.history[-1][0].from_): 3, flip_coords(self.flipped, *self.history[-1][0].to): 3})
        if self.highlightedSquares:
            self.board.draw_highlightedSquares(self.highlightedSquares)
        self.board.draw_pieces()
        if self.valid_moves:
            self.board.draw_moves(self.valid_moves)
        for row in range(len(self.board.board)):
            for column in range(len(self.board.board[0])):
                if isinstance(self.board.board[row][column], Pieces.Pawn) and self.board.board[row][column].promotion[0]:
                    self.board.draw_promotion(self.board.board[row][column], self.board.board[row][column].promotion[1], self.flipped)
        pygame.display.update()

    def reset(self, frame):
        self.board = Board(width, height, rows, columns, frame)
        self.selected = None

    def is_king_checked(self):
        return self.get_king_position(self.turn) in self.get_color_moves(-self.turn)
    
    def is_checkmate(self):
        return self.is_king_checked() and self.is_stalemate()

    def check_game(self):
        if self.black_pieces_left == 0:
            print("Whites win")
            return True
        elif self.white_pieces_left == 0:
            print("Blacks win")
            return True
        elif self.is_checkmate():
            print("{} Wins".format("Black" if self.turn == 1 else "White"))
            return True
        elif self.is_stalemate():
            print("Stalemate")
            return True
        elif self.halfMoves >= 100:
            print("Draw by the 50 moves rule")
            return True
        # TODO for threesold repetition, we can use self.history and check repetitions after the last irreversible moves, irreversible moves are captures, pawn moves, king or rook losing castling rights, castling

    def get_color_moves(self, color: int):
        color_moves = []
        for row in range(len(self.board.board)):
            for column in range(len(self.board.board[0])):
                if self.board.board[row][column] != 0 and self.board.board[row][column].color == color:
                    color_moves += self.board.board[row][column].get_available_moves(self.board.board, row, column, self.flipped)
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
        print("turn", self.turn)

    def get_king_position(self, color: int):
        for row in range(len(self.board.board)):
            for column in range(len(self.board.board[0])):
                if isinstance(self.board.board[row][column], Pieces.King) and self.board.board[row][column].color == color:
                    return row, column

    def possible_moves(self, board: list[list[int | Pieces.Piece]]):
        possible_moves = []
        for row in range(len(board)):
            for column in range(len(board[0])):
                if board[row][column] != 0 and board[row][column].color == self.turn and isinstance(board[row][column], Pieces.King):
                    possible_moves += self.flip_moves(board[row][column].get_available_moves(board, row, column))
        return possible_moves

    def is_stalemate(self) -> bool:
        return not any([self.can_move(piece, move[0], move[1]) for piece in self.get_color_pieces(self.turn) for move in piece.get_available_moves(self.board.board, piece.row, piece.column)])

    def remove(self, row: int, column: int):
        piece = self.board.board[row][column]
        if piece != 0:
            self.board.board[row][column] = 0
            if piece.color == 1:
                self.white_pieces_left -= 1
            else:
                self.black_pieces_left -= 1

    def move(self, piece: Pieces.Piece, row: int, column: int):
        piece.en_passant = (isinstance(piece, Pieces.Pawn) and abs(piece.row - row) == 2)
        # Castling
        if isinstance(piece, Pieces.King) and abs(piece.column - column) == 2 and not self.is_king_checked():
            # Calculate old and new position of the rook for O-O and O-O-O
            new_rook_pos, old_rook_pos = (column + 4) // 2, 7 * (column - 2) // 4
            self.board.board[row][new_rook_pos], self.board.board[row][old_rook_pos] = self.board.board[row][old_rook_pos], self.board.board[row][new_rook_pos]
            self.board.board[row][new_rook_pos].piece_move(row, new_rook_pos)
            piece.not_castled = False
        # En-passant
        if isinstance(piece, Pieces.Pawn) and isinstance(self.board.board[row + (piece.color * -self.flipped)][column], Pieces.Pawn) and self.board.board[row + (piece.color * -self.flipped)][column].en_passant:
            self.board.board[row + (piece.color * -self.flipped)][column] = 0
        self.board.board[piece.row][piece.column], self.board.board[row][column] = self.board.board[row][column], self.board.board[piece.row][piece.column]
        piece.piece_move(row, column)
        # Update the first_move attribute of the piece if it moved
        if isinstance(piece, (Pieces.King, Pieces.Rook, Pieces.Pawn)) and piece.first_move:
            piece.first_move = False
        # Remove the en-passant attribute
        for row in range(rows):
            for column in range(columns):
                if isinstance(self.board.board[row][column], Pieces.Pawn) and self.board.board[row][column].en_passant and self.board.board[row][column].color != piece.color:
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
            x = self.selected.color * -self.flipped
            # If in the state of promotion
            if isinstance(self.selected, Pieces.Pawn) and self.selected.promotion[0]:
                # Promote the pawn
                if row in range(2*(1 - x), 2*(3 - x)) and column == self.selected.promotion[1] + self.selected.column:
                    move = Move.Move(self, (self.selected.row, self.selected.column), (row, column), self.selected, (self.board.board[row][column] != 0 and self.board.board[row][column].color != self.selected.color), [Pieces.Queen, Pieces.Knight, Pieces.Rook, Pieces.Bishop][(row if x == 1 else 7 - row)])
                    move.promote()
                    print(move.to_literal())
                    return
                # Remove the promotion
                else:
                    self.selected.promotion = (False, 0)
            # If the player clicks on one of his pieces, it will change the selected piece
            if self.board.board[row][column] != 0 and self.board.board[row][column].color == self.selected.color:
                self.selected = None
                self.select(row, column)
                return
            # If the player clicks on a square where the selected piece can't move, it will remove the selection
            if (row, column) not in self.valid_moves or (row, column) == (self.selected.row, self.selected.column):
                self.valid_moves = []
                self.selected = None
                return
            # If the player push a pawn to one of the last rows, it will be in the state of promotion
            if isinstance(self.selected, Pieces.Pawn) and row in [0, 7]:
                self.selected.promotion = (True, column - self.selected.column)
                self.valid_moves = []
                return
            move = Move.Move(self, (self.selected.row, self.selected.column), (row, column), self.selected, ((self.board.board[row][column] != 0 and self.board.board[row][column].color != self.selected.color) or (0 < row + x < len(self.board.board) - 1 and isinstance(self.board.board[row + x][column], Pieces.Pawn) and self.board.board[row + x][column].color != self.selected.color and self.board.board[row + x][column].en_passant)), False)
            move.make_move()
            print(move.to_literal())
        else:
            piece = self.board.board[row][column]
            if piece != 0 and self.turn == piece.color:
                self.selected = piece
                # TODO /!\ NEEDS to be optimised, needs to remove all moves that are not in the "Cross pin" if there is one, see chessprogramming.org/Pin
                self.valid_moves = [move for move in self.flip_moves(piece.get_available_moves(self.board.board, row, column)) if self.can_move(self.selected, move[0], move[1])]
