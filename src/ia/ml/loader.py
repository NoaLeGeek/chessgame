import os
import json
import yaml
import torch

from src.ia.ml.builder import build_model, build_optimizer

def load_encoded_moves(filepath: str) -> dict[str, object]:
    """
    Load encoded moves from a JSON file.

    Args:
        filepath (str): Path to the encoded moves file.

    Returns:
        dict[str, object]: Dictionary of encoded moves.
    """
    with open(filepath, "r", encoding='utf-8') as file:
        return json.load(file)

def load_config(filepath: str) -> dict[str, object]:
    """
    Load configuration from a YAML file.

    Args:
        filepath (str): Path to the configuration file.

    Returns:
        dict[str, object]: Configuration data.
    """
    with open(filepath, "r", encoding='utf-8') as file:
        return yaml.safe_load(file)

def load_checkpoint(filepath: str, model: torch.nn.Module, optimizer: torch.optim.Optimizer) -> tuple[torch.nn.Module, torch.optim.Optimizer, int]:
    """
    Load model checkpoint.

    Args:
        filepath (str): Path to the checkpoint file.
        model (torch.nn.Module): Model to load the state dict into.
        optimizer (torch.optim.Optimizer): Optimizer to load the state dict into.

    Returns:
        tuple[torch.nn.Module, torch.optim.Optimizer, int]: Tuple containing the updated model, optimizer, and the last saved epoch.
    """
    checkpoint = torch.load(filepath)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch: int = checkpoint['epoch']
    return model, optimizer, epoch

def load_model_from_checkpoint(model_path: str, num_checkpoint: int, color: str) -> torch.nn.Module:
    """
    Load a model from a specific checkpoint.

    Args:
        model_path (str): Path to the model directory.
        num_checkpoint (int): Checkpoint number to load.
        color (str): Color information for the model.

    Returns:
        torch.nn.Module: Loaded model instance.
    """
    config = load_config(os.path.join(model_path, 'config.yaml'))
    encoded_moves = load_encoded_moves('data/encoded_moves.json')
    model = build_model(config["model"], {"num_classes": len(encoded_moves)}, encoded_moves, color)
    checkpoint = torch.load(os.path.join(model_path, 'checkpoints', f'checkpoint_{num_checkpoint}.pth'))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    model.to('cpu')
    torch.save(model.state_dict(), 'models/v1/ChessModel.pth')
    return model

def load_model(model_path: str, color: int) -> torch.nn.Module:
    """
    Load a trained model from the specified path.

    Args:
        model_path (str): Path to the model directory.
        color (int): The color of the player.

    Returns:
        torch.nn.Module: Loaded model instance.
    """
    config = load_config(os.path.join(model_path, 'config.yaml'))
    encoded_moves = load_encoded_moves('data/encoded_moves.json')
    model = build_model(config["model"], {"num_classes": len(encoded_moves)}, encoded_moves, color)
    state_dict = torch.load(os.path.join(model_path, 'ChessModel.pth'), weights_only=True)
    model.load_state_dict(state_dict)
    return model
