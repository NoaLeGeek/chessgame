import yaml
import json
import torch

from ia.ml.builder import build_model, build_optimizer, build_scheduler


def load_encoded_moves(filepath):
    """
    Load encoded moves from a JSON file.

    Args:
        filepath (str): Path to the encoded moves file.

    Returns:
        dict: Dictionary of encoded moves.
    """
    print(f"Loading encoded moves from {filepath}...")
    with open(filepath, "r") as file:
        return json.load(file)


def load_config(filepath):
    """
    Load configuration from a YAML file.

    Args:
        filepath (str): Path to the configuration file.

    Returns:
        dict: Configuration data.
    """
    print(f"Loading configuration from {filepath}...")
    with open(filepath, "r") as file:
        return yaml.safe_load(file)


def load_checkpoint(filepath, model, optimizer, scheduler):
    """
    Load model checkpoint.

    Args:
        filepath (str): Path to the checkpoint file.
        model (torch.nn.Module): Model to load the state dict into.
        optimizer (torch.optim.Optimizer): Optimizer to load the state dict into.
        scheduler (torch.optim.lr_scheduler._LRScheduler): Scheduler to load the state dict into.

    Returns:
        tuple: model, optimizer, scheduler, epoch, loss
    """
    checkpoint = torch.load(filepath)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
    epoch = checkpoint['epoch']
    loss = checkpoint['loss']
    return model, optimizer, scheduler, epoch, loss


def load_model_from_checkpoint():
    """
    Load model from checkpoint.

    Returns:
        ChessModel: Loaded model.
    """
    config = load_config("models/metadatas/config.yaml")
    encoded_moves = load_encoded_moves(config["encoded_moves_path"])
    model = build_model(config["architecture"], {"num_classes": len(encoded_moves)}, encoded_moves)
    checkpoint = torch.load("models/checkpoint.pth")
    model.load_state_dict(checkpoint["model_state_dict"])
    return model


def load_model():
    """
    Load model from state dictionary.

    Returns:
        ChessModel: Loaded model.
    """
    config = load_config("models/metadatas/config.yaml")
    encoded_moves = load_encoded_moves(config["encoded_moves_path"])
    model = build_model(config["architecture"], {"num_classes": len(encoded_moves)}, encoded_moves) 
    model.load_state_dict(torch.load("models/ChessModel.pth"))
    return model
