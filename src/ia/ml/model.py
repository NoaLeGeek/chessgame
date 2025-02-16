import json
import torch
import numpy as np
import torch_directml
import torch.nn as nn


class ChessModel(nn.Module):
    def __init__(self, layers, encoded_moves):
        """
        Initialize the ChessModel.

        Args:
            layers (nn.ModuleList): List of layers for the model.
            encoded_moves (dict): Dictionary of encoded moves.
        """
        super(ChessModel, self).__init__()
        self.layers = layers
        self.encoded_moves = encoded_moves
        self.decoded_moves = {v: k for k, v in encoded_moves.items()}

    def forward(self, x):
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

    def predict(self, board):
        device = torch_directml.device()
        self.to(device)

        X = board.to_matrix()

        X = torch.tensor(X, dtype=torch.float32).unsqueeze(0).to(device)

        with torch.no_grad():
            logits = self(X)

        logits = logits.squeeze(0)
        probabilities = torch.softmax(logits, dim=0).cpu().numpy()
        sorted_indices = np.argsort(probabilities)[::-1]

        for move_index in sorted_indices:
            uci_move = self.decoded_moves.get(move_index)
            move = board.convert_uci_to_move(uci_move)
            if move:
                if move.is_legal():
                    return move
                
