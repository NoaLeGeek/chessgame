import json

import torch
import numpy as np
import torch.nn as nn

from board.player import Player

class ChessModel(nn.Module, Player):
    """
    A neural network model for playing chess, inheriting from PyTorch's nn.Module and a Player class.
    """
    def __init__(self, layers: nn.ModuleList, encoded_moves: dict[str, int], color: int):
        """
        Initialize the ChessModel.

        Args:
            layers (nn.ModuleList): List of layers for the model.
            encoded_moves (dict[str, int]): Dictionary mapping moves to indices.
            color (int): The color of the player.
        """
        super(ChessModel, self).__init__()
        Player.__init__(self, color)
        self.layers: nn.ModuleList = layers
        self.encoded_moves: dict[str, int] = encoded_moves
        self.decoded_moves: dict[int, str] = {v: k for k, v in encoded_moves.items()}
        self.ia: bool = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the model.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor after passing through all layers.
        """
        for layer in self.layers:
            x = layer(x)
        return x

    def predict(self, board_matrix: np.ndarray) -> np.ndarray:
        """
        Predict the best move probabilities given a board matrix.

        Args:
            board_matrix (np.ndarray): Board representation as a matrix.

        Returns:
            np.ndarray: Sorted indices of moves based on their probabilities.
        """
        self.to('cpu')
        X = torch.tensor(board_matrix, dtype=torch.float32).unsqueeze(0).to('cpu')

        with torch.no_grad():
            logits = self(X)

        logits = logits.squeeze(0)
        probabilities = torch.softmax(logits, dim=0).cpu().numpy()
        sorted_indices = np.argsort(probabilities)[::-1]

        return sorted_indices

    def get_best_move(self, board) -> object:
        """
        Get the best legal move based on model predictions.

        Args:
            board: The current chess board state.

        Returns:
            object: The best legal move according to the model.
        """
        sorted_indices = self.predict(board.to_matrix())
        for idx in sorted_indices:
            uci_move = self.decoded_moves[idx]
            move = board.convert_uci_to_move(uci_move)
            if move and move.is_legal(board):
                return move

    def play_move(self, board) -> None:
        """
        Execute the best move on the given board and update highlights.

        Args:
            board: The current chess board state.
        """
        best_move = self.get_best_move(board)
        if best_move:
            best_move.execute(board)
            board.update_highlights()
