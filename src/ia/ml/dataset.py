import os
import json
from multiprocessing import Pool, cpu_count

import torch
import numpy as np
from tqdm import tqdm
from chess import pgn, Board
from torch.utils.data import IterableDataset

class ChessDataset(IterableDataset):
    """
    A custom dataset for processing chess games stored in PGN format.
    """
    def __init__(self, file_path: str, encoded_moves: dict[str, int] = {}, batch_size: int = 64):
        """
        Initializes the ChessDataset.

        Args:
            file_path (str): The path to the PGN file.
            encoded_moves (dict[str, int]): A dictionary mapping move strings to encoded values.
            batch_size (int): The number of samples per batch.
        """
        self.file_path = file_path
        self.encoded_moves = encoded_moves
        self.batch_size = batch_size
        self.num_games, self.num_samples = self.process_dataset()
        print(f'Number of games: {self.num_games}')
        print(f'Number of samples: {self.num_samples}')

    def process_segment(self, start_offset: int, end_offset: int) -> tuple[int, int]:
        """
        Processes a segment of the PGN file.

        Args:
            start_offset (int): The start byte offset.
            end_offset (int): The end byte offset.

        Returns:
            tuple[int, int]: Number of samples and games processed.
        """
        num_samples = 0
        num_games = 0

        with open(self.file_path, "r", encoding="UTF-8", errors="ignore") as f:
            f.seek(start_offset)
            if start_offset != 0:
                f.readline()
                while True:
                    line = f.readline()
                    if line.startswith("[Event ") or not line:
                        break

            while f.tell() < end_offset:
                game = pgn.read_game(f)
                if game is None:
                    break
                num_games += 1
                for move in game.mainline_moves():
                    num_samples += 1
        
        return num_samples, num_games

    def process_dataset(self) -> tuple[int, int]:
        """
        Processes the entire PGN dataset using multiple workers.

        Returns:
            tuple[int, int]: Total number of games and samples processed.
        """
        total_games, total_samples = 0, 0
        file_size = os.path.getsize(self.file_path)
        num_workers = cpu_count()
        chunk_size = file_size // num_workers
        
        offsets = sorted([
            (i * chunk_size, min((i + 1) * chunk_size, file_size))
            for i in range(num_workers)
        ])

        with Pool(num_workers) as pool:
            results = pool.starmap(self.process_segment, offsets)
        
        for num_samples, num_games in results:
            total_samples += num_samples
            total_games += num_games
        
        return total_games, total_samples

    @staticmethod
    def board_to_matrix(board: Board) -> np.ndarray:
        """
        Converts a chess board to a 14x8x8 matrix representation.

        Args:
            board (Board): A chess board object.

        Returns:
            np.ndarray: A 14x8x8 matrix representation of the board.
        """
        matrix = np.zeros((14, 8, 8))
        for square, piece in board.piece_map().items():
            row, col = divmod(square, 8)
            row = 7 - row
            channel = piece.piece_type - 1
            if not piece.color:
                channel += 6
            matrix[channel, row, col] = 1
        for move in board.legal_moves:
            from_square = move.from_square
            to_square = move.to_square
            from_row, from_col = divmod(from_square, 8)
            to_row, to_col = divmod(to_square, 8)
            from_row, to_row = 7 - from_row, 7 - to_row
            matrix[12, from_row, from_col] = 1
            matrix[13, to_row, to_col] = 1
        return matrix

    @staticmethod
    def process_X(X: list[np.ndarray]) -> torch.Tensor:
        """
        Processes the input data.

        Args:
            X (list[np.ndarray]): The input data.

        Returns:
            torch.Tensor: Processed input tensor.
        """
        return torch.tensor(np.array(X), dtype=torch.float32)

    def process_y(self, y: list[str]) -> torch.Tensor:
        """
        Processes the target data.

        Args:
            y (list[str]): The target data (list of move strings).

        Returns:
            torch.Tensor: Processed target tensor.
        """
        y = np.array([self.encoded_moves[move] for move in y])
        return torch.tensor(y, dtype=torch.long)

    def __iter__(self):
        """
        Creates an iterator over the dataset.

        Yields:
            tuple[torch.Tensor, torch.Tensor]: A tuple of processed input and target tensors.
        """
        worker_info = torch.utils.data.get_worker_info()
        if worker_info is None:
            iter_start, iter_end = 0, os.path.getsize(self.file_path)
        else:
            file_size = os.path.getsize(self.file_path)
            num_workers = worker_info.num_workers
            worker_id = worker_info.id
            chunk_size = file_size // num_workers
            iter_start = worker_id * chunk_size
            iter_end = (worker_id + 1) * chunk_size if worker_id < num_workers - 1 else file_size
        
        X, y = [], []
        with open(self.file_path, "r", encoding="UTF-8", errors="ignore") as f:
            f.seek(iter_start)
            if iter_start != 0:
                f.readline()
                while True:
                    line = f.readline()
                    if line.startswith("[Event ") or not line:
                        break

            while f.tell() < iter_end:
                game = pgn.read_game(f)
                if game is None:
                    break
                
                board = game.board()
                for move in game.mainline_moves():
                    X.append(self.board_to_matrix(board))
                    y.append(move.uci())
                    board.push(move)
                    
                    if len(X) >= self.batch_size:
                        yield self.process_X(X), self.process_y(y)
                        X, y = [], []
        
        if X:
            yield self.process_X(X), self.process_y(y)
