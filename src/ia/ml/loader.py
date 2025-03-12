import os

import json

import yaml
import torch

try :
    from builder import build_model, build_optimizer
except :
    from ia.ml.builder import build_model, build_optimizer
    

def load_encoded_moves(filepath):
    """
    Load encoded moves from a JSON file.

    Args:
        filepath (str): Path to the encoded moves file.

    Returns:
        dict: Dictionary of encoded moves.
    """
    with open(filepath, "r", encoding='utf-8') as file:
        return json.load(file)


def load_config(filepath):
    """
    Load configuration from a YAML file.

    Args:
        filepath (str): Path to the configuration file.

    Returns:
        dict: Configuration data.
    """
    with open(filepath, "r", encoding='utf-8') as file:
        return yaml.safe_load(file)


def load_checkpoint(filepath, model, optimizer):
    """
    Load model checkpoint.

    Args:
        filepath (str): Path to the checkpoint file.
        model (torch.nn.Module): Model to load the state dict into.
        optimizer (torch.optim.Optimizer): Optimizer to load the state dict into.

    Returns:
        tuple: model, optimizer, epoch, loss
    """
    checkpoint = torch.load(filepath)
    model.load_state_dict(checkpoint['model_state_dict'])
    current_lr = optimizer.param_groups[0]['lr']
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    for param_group in optimizer.param_groups:
        if param_group['lr'] != current_lr:
            param_group['lr'] = current_lr
    epoch = checkpoint['epoch']
    return model, optimizer, epoch


def load_model_from_checkpoint(model_path, num_checkpoint):
    """
    Load model from checkpoint.

    Returns:
        ChessModel: Loaded model.
    """
    config = load_config(os.path.join(model_path, ('config.yaml')))
    encoded_moves = load_encoded_moves('data/encoded_moves.json')
    model = build_model(config["model"], {"num_classes": len(encoded_moves)}, encoded_moves)
    checkpoint = torch.load(os.path.join(model_path, 'checkpoints', f'checkpoint_{num_checkpoint}.pth'))
    model.load_state_dict(checkpoint["model_state_dict"])
    return model

