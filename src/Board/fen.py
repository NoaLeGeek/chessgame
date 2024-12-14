from Board.piece import Piece
from utils import flip_coords

class FEN:
    def __init__(self, board, turn, castling_rights, ep, half_move, full_move):
        self.board = board
        self.turn = turn
        self.castling_rights = castling_rights
        self.ep = ep
        self.half_move = half_move
        self.full_move = full_move
    
    def __str__(self) -> str:
        fen = ""
        # Board
        for row in range(self.board.config.rows):
            empty_squares = 0
            for column in range(self.board[0])):
                piece = self.board.get_piece(row, column)
                if piece is None:
                    empty_squares += 1
                else:
                    if empty_squares > 0:
                        fen += str(empty_squares)
                        empty_squares = 0
                    char = Piece.piece_to_notation(piece)
                    fen += (char if piece.color == 1 else char.lower())
            if empty_squares > 0:
                fen += str(empty_squares)
            if row < len(self.board) - 1:
                fen += "/"
        fen += " " + ("w" if self.turn == 1 else "b")
        # Castling rights
        castling = ""
        white_king = self.board.find_piece("K", 1)
        if white_king is not None and white_king.piece.first_move:
            if next((self.board[white_king.row][i] for i in range(white_king.column - self.flipped, flip_coords(-1, flipped=self.flipped), -self.flipped) if self.board.get_piece(white_king.row, i).notation == "R" and self.board[white_king.row][i].first_move), None) is not None:
                castling += "K"
            if next((self.board[white_king.row][i] for i in range(white_king.column + self.flipped, flip_coords(8, flipped = self.flipped), self.flipped) if self.board.get_piece(white_king.row, i).notation == "R" and self.board[white_king.row][i].first_move), None) is not None:
                castling += "Q"
        black_king = self.board.find_piece("K", -1)
        if black_king is not None and black_king.piece.first_move:
            if next((self.board[black_king.row][i] for i in range(black_king.column - self.flipped, flip_coords(-1, flipped=self.flipped), -self.flipped) if self.board.get_piece(black_king.row, i).notation == "R" and self.board[black_king.row][i].first_move), None) is not None:
                castling += "k"
            if next((self.board[black_king.row][i] for i in range(black_king.column + self.flipped, flip_coords(8, flipped = self.flipped), self.flipped) if self.board.get_piece(black_king.row, i).notation == "R" and self.board[black_king.row][i].first_move), None) is not None:
                castling += "q"
        fen += " " + (castling if castling != "" else "-")
        can_en_passant = bool(self.en_passant)
        if can_en_passant:
            x = ((7-2*self.en_passant[0])//3)
            r, c = self.en_passant
            if not any([self.board.get_piece([r + x, c + i]).notation == "P" and self.board[r + x][c + i].color == x*self.flipped for i in [-1, 1]]):
                can_en_passant = False
        fen += " " + (chr(97 + flip_coords(self.en_passant[1], flipped = self.flipped)) + str(flip_coords(self.en_passant[0], flipped = -self.flipped) + 1) if can_en_passant else "-")
        fen += " " + str(self.halfMoves)
        fen += " " + str(self.fullMoves)
        return fen