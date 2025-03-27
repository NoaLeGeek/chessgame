from src.config import config
from src.constants import castling_king_column
from src.board.piece import piece_to_notation
from src.utils import flip_pos, sign, get_value, debug_print, play_sound

class Move:
    def __init__(self, board, from_pos, to_pos, promotion=None):
        """
        Initializes a Move object representing a chess move on the board.

        This constructor validates the move, determines its type (e.g., normal move, 
        promotion, en passant, castling), and initializes the relevant attributes.

        Parameters:
            board (Board): The chess board on which the move is being made.
            from_pos (tuple): A tuple (row, col) representing the starting position of the move.
            to_pos (tuple): A tuple (row, col) representing the destination position of the move.
            promotion (str, optional): The piece to promote to if the move is a pawn promotion 
                                       (e.g., 'Q' for Queen). Defaults to None.

        Attributes:
            from_pos (tuple): The starting position of the move.
            to_pos (tuple): The destination position of the move.
            moving_piece (Piece): The piece being moved.
            en_passant (bool): True if the move is an en passant capture, False otherwise.
            captured_piece (Piece or None): The piece being captured, if any. For en passant, 
                                            this is the pawn being captured.
            castling (bool): True if the move is a castling move, False otherwise.
            promotion (str or None): The piece to promote to if the move is a pawn promotion.
            notation (str or None): The algebraic notation of the move. Defaults to None.
            fen (str or None): The FEN string representing the board state after the move. Defaults to None.

        Raises:
            ValueError: If there is no piece at `from_pos`.
            ValueError: If the promotion is invalid (e.g., not a pawn or not at the last row).
        """
        if board.is_empty(from_pos):
            raise ValueError(f"There is no piece at {from_pos}")
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.moving_piece = board.get_piece(from_pos)
        if promotion is not None and (to_pos[0] not in [0, config.rows - 1] or self.moving_piece.notation != "P"):
            raise ValueError("Promotion is only possible for pawns at the last row")
        self.en_passant = self._is_en_passant(board)
        self.captured_piece = board.get_piece((self.from_pos[0], board.ep[1])) if self.en_passant else board.get_piece(to_pos) 
        self.castling = self._is_castling(board)
        self.promotion = promotion
        self.notation = None
        self.fen = None
    
    def is_capture(self) -> bool:
        """
        Determines if the move results in the capture of an opponent's piece.

        Returns:
            bool: True if the move captures an opponent's piece, False otherwise.
        """
        return self.captured_piece is not None
    
    def flip_move(self) -> None:
        """
        Reverses the positions of a move on the board by flipping the coordinates.

        This method updates the `from_pos` and `to_pos` attributes of the move
        by applying the `flip_pos` function to each. It is typically used to
        adjust the move representation when the perspective of the board changes.
        """
        self.from_pos = flip_pos(self.from_pos)
        self.to_pos = flip_pos(self.to_pos)

    def execute(self, board) -> None:
        """
        Executes a chess move for the first time on the given board and updates the board state accordingly.

        This method handles all necessary updates to the board when a move is executed,
        including castling rights, en passant status, move counters, and game history.
        It also evaluates the board state after the move and checks for game-ending conditions.
        All these updates and the move are saved in a MoveNode object and added to the move tree.
        This method should be called only once for each move.

        Parameters:
            board (Board): The chess board object on which the move is executed.
        """
        # All the things to update when the move is done for the first time
        if config.rules["giveaway"] == False:
            board._update_castling(self)
        board._update_en_passant(self)
        board._update_last_irreversible_move(self)
        board.half_moves += 1
        # Reset half_moves if it's a capture, castling or a pawn move
        if self.is_capture() or self.castling or (not board.is_empty(self.to_pos) and self.captured_piece.notation == "P"):
            board.half_moves = 0
        if board.turn == -1:
            board.full_moves += 1
        # Remember the move for undo
        board.move_tree.add(board, MoveNode(self, board.move_tree.current.move, board))
        # This is the board state after the move
        self.fen = str(board)
        self.notation = self.to_notation(board)
        board.update_history()
        board.check_game()
        board.score = board.negamax.evaluate_board(board)

    def move(self, board):
        """
        Executes a move on the chessboard, updating the board state and handling special rules.
        This method can be called ad infinitum on the board.

        Parameters:
            board (Board): The current state of the chessboard. This object is updated to reflect the move.

        Functionality:
            - If the move involves a promotion, the piece is promoted accordingly.
            - Otherwise, the piece is moved to the target position.
            - Updates the turn to the next player.
            - Resets the selected piece on the board.
            - Swaps the current player and the waiting player.
            - Checks for the "+3 checks" rule, and increments the check count for the opponent if applicable.
        """
        # Update the board state
        if self.promotion is not None:
            self.promote_piece(board, self.promotion)
        else:
            self.move_piece(board)
        board.turn *= -1
        board.selected = None
        board.current_player, board.waiting_player = board.waiting_player, board.current_player
        if config.rules["+3_checks"] == True and board.current_player.is_king_check(board):
            board.checks[board.waiting_player.color] += 1

    def move_piece(self, board):
        # Update kings' positions
        if self.moving_piece.notation == "K":
            board.current_player.king = self.to_pos

        # Update player's pieces
        if self.is_capture() and not self.castling and not self.en_passant:
            board.waiting_player.remove_piece(self.captured_piece)

        # Capture en passant
        if self.en_passant:
            board.waiting_player.remove_piece(board.get_tile((self.from_pos[0], self.to_pos[1])).piece)
            board.get_tile((self.from_pos[0], self.to_pos[1])).piece = None

        # Handle castling logic
        if self.castling:
            self._handle_castling(board)
        # Handle normal move
        else:
            self._handle_normal_move(board)
        
        # Anarchy chess
        if config.rules["+3_checks"] == True and board.current_player.is_king_check(board):
            self.checks[board.waiting_player.color] += 1

    def _handle_castling(self, board):
        """
        Handles the castling move in a chess game. Castling is a special move 
        involving the king and a rook, where both pieces move simultaneously 
        under specific conditions.
        Parameters:
            board (Board): The current state of the chessboard. It provides 
                           access to the positions of pieces and tiles.
        Utility:
            This function updates the board to reflect the castling move by:
            - Moving the king to its destination column.
            - Moving the rook to its corresponding destination column.
            - Clearing the original positions of the king and rook.
            It also accounts for Chess960 rules, where the rook's initial 
            position may vary.
        """
        from_pos, to_pos = self.from_pos, self.to_pos
        d = sign(to_pos[1] - from_pos[1])
        # Save the pieces
        king = self.moving_piece
        rook_pos = to_pos if config.rules["chess960"] == True else (to_pos[0], (7 if d == 1 else 0))
        rook = board.get_piece(rook_pos)

        # Destinations columns
        dest_king_column = flip_pos(castling_king_column[d*board.flipped], flipped=board.flipped)
        dest_rook_column = dest_king_column - d
        
        # Castling move
        board.get_tile(from_pos).piece = None
        board.get_tile(rook_pos).piece = None
        board.get_tile((from_pos[0], dest_king_column)).piece = king
        board.get_tile((from_pos[0], dest_rook_column)).piece = rook
        
    def _handle_normal_move(self, board):
        """
        Handles a normal chess move by updating the board state.

        This method moves a piece from its current position (`from_pos`) to a new position (`to_pos`) 
        on the board. It updates the board tiles by setting the destination tile's piece to the 
        moving piece and clearing the piece from the original tile.

        Parameters:
            board (Board): The chessboard object that contains the tiles and pieces.
        """
        from_pos, to_pos = self.from_pos, self.to_pos
        board.get_tile(to_pos).piece = self.moving_piece
        board.get_tile(from_pos).piece = None

    def promote_piece(self, board, type_piece):
        """
        Promotes a pawn to a specified piece type during a chess game.

        This function replaces a pawn that has reached the promotion rank with a new piece 
        of the specified type. It updates the board state, assigns the appropriate image 
        to the new piece (if applicable), and ensures the new piece is added to the current 
        player's collection of pieces.

        Parameters:
            board (Board): The chess board object representing the current game state.
            type_piece (Type[Piece]): The class of the piece to which the pawn will be promoted 
                                      (e.g., Queen, Rook, Bishop, Knight).

        Raises:
            ValueError: If the image for the promoted piece is missing in the board's piece images.
        """
        new_piece = type_piece(self.moving_piece.color)
        if config.piece_asset != "blindfold":
            piece_image_key = f"{(('w' if new_piece.color == 1 else 'b') if config.piece_asset != "mono" else "")}{new_piece.notation}"
            if piece_image_key not in board.piece_images:
                raise ValueError(f"Missing piece image for: {piece_image_key}")
            new_piece.image = board.piece_images[piece_image_key]
        board.current_player.add_piece(new_piece)
        board.get_tile(self.to_pos).piece = new_piece
        board.get_tile(self.from_pos).piece = None
        board.promotion = None

    def undo(self, board) -> None:
        """
        Reverts the last move made on the chessboard, restoring the board state 
        to what it was before the move. This includes updating the turn, 
        resetting the selected piece, swapping the current and waiting players, 
        and handling specific rules such as promotion and the "+3 checks" rule.

        Parameters:
            board (Board): The chessboard object representing the current game state. 
                           It contains information about the players, pieces, and rules.
        """
        board.turn *= -1
        board.selected = None
        board.current_player, board.waiting_player = board.waiting_player, board.current_player
        if config.rules["+3_checks"] == True and board.current_player.is_king_check(board):
            board.checks[board.waiting_player.color] -= 1
        if self.promotion is not None:
            self.undo_promote_piece(board)
        else:
            self.undo_move_piece(board)

    def undo_promote_piece(self, board):
        """
        Reverts a pawn promotion on the chessboard by restoring the original piece 
        and removing the promoted piece from the current player's active pieces.

        Parameters:
            board (Board): The chessboard object that contains the tiles and pieces. 
                           It provides access to the tiles and manages the state of the game.

        Utility:
            This function is used to undo a pawn promotion, typically as part of 
            reverting a move in the game. It restores the original state of the 
            board before the promotion occurred, including the original piece 
            and any captured piece.
        """
        board.get_tile(self.from_pos).piece = self.moving_piece
        board.current_player.remove_piece(board.get_tile(self.to_pos).piece)
        board.get_tile(self.to_pos).piece = self.captured_piece

    def undo_move_piece(self, board):
        """
        Reverts the last move made on the chessboard, restoring the board state 
        and updating the necessary attributes.
        Parameters:
            board (Board): The chessboard object representing the current state 
                           of the game. It provides access to tiles, pieces, and 
                           player information.
        Utility:
            - Restores the position of the moving piece to its original location.
            - Restores the captured piece (if any) to its original position.
            - Handles special cases such as en passant and castling.
            - Updates the king's position if the moved piece was a king.
            - Restores the captured piece to the waiting player's list of pieces 
              if the move was a capture.
        """
        # Restore the board state
        board.get_tile(self.from_pos).piece = self.moving_piece
        board.get_tile((self.to_pos[0] + self.moving_piece.color*board.flipped, self.to_pos[1]) if self.en_passant else self.to_pos).piece = self.captured_piece
        if self.en_passant:
            board.get_tile(self.to_pos).piece = None

        # Handle castling
        if self.castling:
            d = sign(self.to_pos[1] - self.from_pos[1])
            rook_pos = (self.from_pos[0], self.from_pos[1] + d)
            rook = board.get_piece(rook_pos)
            dest_rook_pos = self.to_pos if config.rules["chess960"] == True else (self.to_pos[0], (7 if d == 1 else 0))
            board.get_tile(rook_pos).piece = None
            board.get_tile(dest_rook_pos).piece = rook

        # Restore king position
        if self.moving_piece.notation == "K":
            board.current_player.king = self.from_pos

        # Restore player's pieces
        if self.is_capture() and not self.castling:
            board.waiting_player.add_piece(self.captured_piece)

    def play_sound_move(self, board) -> None:
        """
        Plays the appropriate sound effect based on the type of move made on the chessboard.

        This function determines the type of move (e.g., castling, check, promotion, capture, or a regular move)
        and plays the corresponding sound effect using the provided sound system.

        Parameters:
            board (Board): The current state of the chessboard, which includes information about the
                           sounds system, the current player, and the game state (e.g., turn, flipped board).
        """
        if self.castling:
            play_sound(board.sounds, "castle")
        elif board.current_player.is_king_check(board):
            play_sound(board.sounds, "move-check")
        elif self.promotion is not None:
            play_sound(board.sounds, "promote")
        elif self.is_capture():
            play_sound(board.sounds, "capture")
        else:
            play_sound(board.sounds, ("move-self" if board.turn * board.flipped == 1 else "move-opponent"))
    
    def is_legal(self, board) -> bool:
        """
        Determines whether a move is legal on the given chess board.

        This function evaluates the legality of a move based on the current game rules, 
        including standard chess rules, castling rules, and optional giveaway chess rules. 
        It also checks for conditions such as whether the king is in check during castling.

        Parameters:
            board (Board): The current state of the chess board, which includes information 
                           about the tiles, pieces, and game rules.

        Returns:
            bool: True if the move is legal, False otherwise.
        """
        if not self.castling:
            if config.rules["giveaway"] == True:
                return True
            return board.get_tile(self.from_pos).can_move(board, self.to_pos)
        # Castling
        if config.rules["giveaway"] == True or board.current_player.is_king_check(board):
            return False
        d = sign(self.to_pos[1] - self.from_pos[1])
        is_legal = True
        # -1 for O-O-O, 1 for O-O
        castling_direction = d*board.flipped
        rook_pos = self.to_pos if config.rules["chess960"] == True else (self.to_pos[0], (7 if d == 1 else 0))
        dest_rook_column = flip_pos(castling_king_column[castling_direction] - castling_direction, flipped=board.flipped) * d
        dest_king_column = flip_pos(castling_king_column[castling_direction], flipped=board.flipped) * d
        start = d * min(self.from_pos[1] * d, dest_rook_column)
        end = d * max(rook_pos[1] * d, dest_king_column)
        for next_column in range(start + castling_direction, end + castling_direction, castling_direction):
            condition = board.get_tile(self.from_pos).can_move(board, (self.from_pos[0], next_column))
            is_legal = is_legal and condition
            if not is_legal:
                break
        return is_legal
    
    def _is_castling(self, board) -> bool:
        """
        Determines whether the current move is a castling move.

        This function checks if the move being made by the king qualifies as a castling move,
        considering the rules of standard chess or Chess960. It verifies the movement of the king,
        the presence of a rook, and the castling rights for the player's color.

        Parameters:
            board: The current state of the chessboard. It provides information about the positions
                   of pieces, castling rights, and whether specific squares are empty.

        Returns:
            bool: True if the move is a valid castling move, False otherwise.
        """
        if self.moving_piece.notation != "K":
            return False
        d = 1 if self.to_pos[1] > self.from_pos[1] else -1
        if (config.rules["chess960"] == False and abs(self.from_pos[1] - self.to_pos[1]) != 2) or (config.rules["chess960"] == True and (not self.is_capture() or board.is_empty(self.to_pos) or self.captured_piece.notation != "R" or self.moving_piece.is_enemy(self.captured_piece))):
            return False
        # O-O-O castling's right
        if d == -1 and not board.castling[self.moving_piece.color][d]:
            return False
        # O-O castling's right
        elif d == 1 and not board.castling[self.moving_piece.color][d]:
            return False
        return True
    
    def _is_en_passant(self, board) -> bool:
        """
        Determines if the current move is an en passant capture in a chess game.

        An en passant capture occurs when a pawn moves two squares forward from its 
        starting position and lands beside an opponent's pawn, allowing the opponent's 
        pawn to capture it as if it had only moved one square forward.

        Parameters:
            board (Board): The current state of the chessboard, which includes the 
                           en passant target square (`ep`) if applicable.

        Returns:
            bool: True if the move is an en passant capture, False otherwise.
        """
        return (
            self.moving_piece.notation == "P" and
            board.ep is not None and
            self.to_pos == board.ep
            )
        
    def to_notation(self, board) -> str:
        """
        Converts the current move into standard chess notation.

        This method generates a string representation of the move in standard chess
        notation, including special cases such as castling, captures, promotions, 
        and checks/checkmates. The notation is adjusted based on the board's flipped 
        state to ensure correct representation.

        Parameters:
            board (Board): The current state of the chessboard, which provides 
                           context for the move, including flipped orientation 
                           and player information.

        Returns:
            str: A string representing the move in standard chess notation.
        """
        string = ""
        # The move is O-O or O-O-O
        if self.castling:
            string += "O" + "-O"*(get_value(sign(self.to_pos[1] - self.from_pos[1]) * board.flipped, 1, 2))
        else:
            # Add the symbol of the piece
            if self.moving_piece.notation != "P":
                string += self.moving_piece.notation
            if self.is_capture():
                # Add the starting column if it's a pawn
                if self.moving_piece.notation == "P":
                    string += chr(flip_pos(self.from_pos[1], flipped = board.flipped) + 97)
                # Add x if it's a capture
                string += "x"
            # Add the destination's column
            string += chr(flip_pos(self.to_pos[1], flipped = board.flipped) + 97)
            # Add the destination's row
            string += str(flip_pos(self.to_pos[0], flipped = -board.flipped) + 1)
            # Add promotion
            if self.promotion is not None:
                string += "=" + piece_to_notation(self.promotion)
        # Add # if it's checkmate or + if it's a check
        if board.current_player.is_king_check(board):
            if board.is_stalemate():
                string += "#"
            else:
                string += "+"
        return string
    
class MoveNode:
    """
    Represents a node in a move tree for a chess game, storing information about a specific move 
    and its relationship to other moves.

    Attributes:
        move: The move associated with this node.
        parent: The parent MoveNode representing the previous move in the sequence.
        children: A list of child MoveNode objects representing subsequent moves.
        ep: The en passant target square from the board state.
        castling: The castling rights from the board state.
        half_moves: The number of half-moves since the last capture or pawn advance.
        full_moves: The total number of full moves in the game.
        last_irreversible_move: The move number of the last irreversible move in the game.

    Args:
        move: The move associated with this node.
        parent: The parent MoveNode representing the previous move in the sequence.
        board: The board state from which to extract additional move-related information.
    """
    def __init__(self, move, parent, board):
        self.move = move
        self.parent = parent
        self.children = []
        self.ep = board.ep
        self.castling = board.castling
        self.half_moves = board.half_moves
        self.full_moves = board.full_moves
        self.last_irreversible_move = board.last_irreversible_move

class MoveTree:
    def __init__(self, board):
        """
        Initializes the MoveTree object with a root node and sets the current node to the root.

        Parameters:
            board (Board): The initial state of the chessboard.

        Attributes:
            root (MoveNode): The root node of the move tree, representing the starting position of the board.
            current (MoveNode): The current node in the move tree, initially set to the root.
        """
        self.root = MoveNode(None, None, board)
        self.current = self.root

    def add(self, board, move_node: MoveNode):
        """
        Adds a new move node to the current position in the move tree and updates the board state.

        This function links the given move node to the current node as its parent, appends it to the 
        list of children of the current node, and then moves the game state forward to the newly added move.

        Parameters:
            board: The current state of the chessboard, which will be updated to reflect the new move.
            move_node (MoveNode): The move node to be added to the move tree. This represents a potential move 
                                  in the game and will be linked to the current node.
        """
        move_node.parent = self.current
        self.current.children.append(move_node)
        self.go_forward(board, -1)

    def go_forward(self, board, index=0):
        """
        Advances the game state by moving to the next child node in the game tree.

        This function updates the current position in the game tree to the specified child node,
        executes the associated move on the board, plays the corresponding move sound, and updates
        the board's highlights and move history.

        Parameters:
            board (Board): The current game board object to apply the move to.
            index (int, optional): The index of the child node to move to. Defaults to 0.
        """
        if self.current.children:
            self.current = self.current.children[index]
            self.current.move.move(board)
            self.current.move.play_sound_move(board)
            board.update_highlights()
            board.update_history()

    def go_backward(self, board):
        """
        Reverts the game state to the previous move by undoing the current move 
        and updating the board and game history accordingly.

        Parameters:
            board (Board): The current state of the chessboard, which will be 
                           updated to reflect the previous move.
        """
        if self.current.parent:
            self.current.move.undo(board)
            self.current.move.play_sound_move(board)
            self.current = self.current.parent
            board.update_highlights()
            board.update_history()

    def go_previous(self, board):
        """
        Navigate to the previous sibling node in the game tree and update the board state accordingly.

        This function moves the current position in the game tree to the previous sibling
        of the current node, if it exists. It first navigates backward to the parent node,
        then forward to the appropriate sibling node based on the calculated index.

        Parameters:
            board: The current state of the chessboard. This parameter is used to update
                   the board state as the navigation occurs.
        """
        if self.current.parent:
            siblings = self.current.parent.children
            index = (siblings.index(self.current) - 1) % len(siblings)
            # print("SIBLINGS BEFORE", [s.move.notation for s in siblings])
            # siblings.append(siblings.pop(0))
            # siblings.insert(0, siblings.pop(index))
            # self.current.parent.children = siblings
            # print("SIBLINGS AFTER", [s.move.notation for s in siblings])
            self.go_backward(board)
            self.go_forward(board, index)

    def go_next(self, board):
        """
        Advances to the next sibling node in the game tree and updates the board state accordingly.

        This function navigates to the next sibling of the current node in the game tree, if it exists. 
        It first moves the game state backward to the root of the current node, then moves forward 
        to the selected sibling node, updating the board state in the process.

        Parameters:
            board (object): The current state of the chessboard, which will be updated as the function 
                            navigates through the game tree.
        """
        if self.current.parent:
            siblings = self.current.parent.children
            index = (siblings.index(self.current) + 1) % len(siblings)
            #print("SIBLINGS BEFORE", [s.move.notation for s in siblings])
            #siblings.append(siblings.pop(0))
            #siblings.insert(0, siblings.pop(index))
            #self.current.parent.children = siblings
            #print("SIBLINGS AFTER", [s.move.notation for s in siblings])
            self.go_backward(board)
            self.go_forward(board, index)

    def go_root(self, board):
        """
        Navigates to the root of the move tree by repeatedly moving backward 
        until the current node has no parent.

        Parameters:
            board (object): The board object representing the current state 
                            of the chess game. It is used to update the board 
                            state as the function traverses backward through 
                            the move tree.
        """
        while self.current.parent:
            self.go_backward(board)

    def go_leaf(self, board):
        """
        Navigates to the leaf node in a tree structure by iteratively moving forward 
        through the first child of the current node.

        Parameters:
            board (object): The current state of the board, which is used to update 
                            the state as the function traverses through the tree.
        """
        while self.current.children:
            self.go_forward(board)

    def get_root_to_leaf(self):
        """
        Retrieves the sequence of moves from the root node to the current node in a tree structure.

        Utility:
        This function is useful for reconstructing the path of moves that led to the current state 
        in a game or decision tree. It traverses the parent nodes starting from the current node 
        and collects the moves in reverse order, returning them in the correct sequence.

        Returns:
        list: A list of moves representing the path from the root node to the current node.
        """
        moves = []
        current = self.current
        while current.parent:
            moves.append(current.move)
            current = current.parent
        return moves[::-1]
    
    def flip_tree(self):
        """
        Flips the moves in the entire tree structure starting from the root node.

        This function traverses a tree structure starting from the root node and 
        flips the moves associated with each node using the `flip_move` method. 
        It ensures that all moves in the tree are inverted or mirrored as needed.
        """
        current = self.root
        queue = [current]
        while queue:
            node = queue.pop()
            if node.move:
                node.move.flip_move()
            queue.extend(node.children)