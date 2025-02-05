import yaml
import json
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
    loss = checkpoint['loss']
    return model, optimizer, epoch, loss


def load_model_from_checkpoint():
    """
    Load model from checkpoint.

    Returns:
        ChessModel: Loaded model.
    """
    config = load_config("models/metadatas/config.yaml")
    encoded_moves = load_encoded_moves(config["encoded_moves_path"])
    model = build_model(config["architecture"], {"num_classes": len(encoded_moves)}, encoded_moves)
    checkpoint = torch.load(config["checkpoint_path"])
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
