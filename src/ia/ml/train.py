import os
import csv
import json
import time
import yaml
import warnings

import torch
from tqdm import tqdm
from torch.nn import CrossEntropyLoss
from torch.utils.data import DataLoader

from dataset import ChessDataset
from builder import build_model, build_optimizer
from loader import load_checkpoint, load_config, load_encoded_moves

# Constants
MODEL_PATH = 'models/v1'
ENCODED_MOVES_PATH = 'data/encoded_moves.json'
CONFIG_PATH = os.path.join(MODEL_PATH, 'config.yaml')
CHECKPOINT_DIR = os.path.join(MODEL_PATH, 'checkpoints')
LOGS_PATH = os.path.join(MODEL_PATH, 'training_logs.csv')

def initialize_dataloaders(config: dict, encoded_moves: dict) -> tuple[DataLoader, DataLoader]:
    """
    Initialize DataLoaders with specified parameters.

    Args:
        config (dict): Configuration dictionary containing data paths and training parameters.
        encoded_moves (dict): Dictionary containing encoded moves used for model training.

    Returns:
        tuple: A tuple containing two DataLoader objects, one for training data and one for validation data.
    """
    print('Initializing Training Dataset...')
    train_dataset = ChessDataset(config["data"]["train_path"], encoded_moves, config["training"]["batch_size"])
    print('Initializing Validation Dataset...')
    val_dataset = ChessDataset(config["data"]["val_path"], encoded_moves, config["training"]["batch_size"])
    return (
        DataLoader(train_dataset, batch_size=None, num_workers=config["training"]["num_workers"], pin_memory=True),
        DataLoader(val_dataset, batch_size=None, num_workers=config["training"]["num_workers"], pin_memory=True)
    )

def setup_device() -> str:
    """
    Setup the device for computation.

    Returns:
        device (str): The device to be used.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    return device

def compute_accuracy(outputs: torch.Tensor, labels: torch.Tensor) -> int:
    """
    Compute the accuracy of the model's predictions.

    Args:
        outputs (torch.Tensor): Model outputs, typically the raw logits.
        labels (torch.Tensor): True labels (ground truth).

    Returns:
        int: The number of correct predictions.
    """
    _, predicted = torch.max(outputs, 1)
    return (predicted == labels).sum().item()

def save_logs(logs: list):
    """
    Save training logs to a CSV file.

    Args:
        logs (list): List of logs to save, including epoch, loss, accuracy, etc.
    """
    with open(LOGS_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(["Epoch", "Training Loss", "Training Accuracy (%)", "Validation Loss", "Validation Accuracy (%)", "Learning Rate", "Time"])
        writer.writerow(logs)

def save_checkpoint(model: torch.nn.Module, optimizer: torch.optim.Optimizer, epoch: int):
    """
    Save the model checkpoint.

    Args:
        model (torch.nn.Module): The model to save.
        optimizer (torch.optim.Optimizer): The optimizer state to save.
        epoch (int): The current epoch.
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    torch.save(checkpoint, os.path.join(CHECKPOINT_DIR, f'checkpoint_{epoch}.pth'))

def validate_model(model: torch.nn.Module, dataloader: DataLoader, criterion: torch.nn.Module, device: torch.device, batch_size: int) -> tuple[float, float]:
    """
    Validate the model.

    Args:
        model (torch.nn.Module): The model to validate.
        dataloader (DataLoader): The DataLoader used for validation.
        criterion (torch.nn.Module): The loss function to compute.
        device (torch.device): The device to run the validation on.
        batch_size (int): The batch size used during validation.

    Returns:
        tuple: A tuple containing the average validation loss and accuracy.
    """
    model.eval()
    total_loss, total_accuracy, total_samples = 0, 0, 0
    
    with torch.no_grad():
        with tqdm(dataloader, total=dataloader.dataset.num_samples // batch_size, desc="Validation", unit="batch") as pbar:
            for inputs, labels in pbar:
                inputs, labels = inputs.to(device), labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                total_loss += loss.item() * batch_size
                total_accuracy += compute_accuracy(outputs, labels)
                total_samples += batch_size

                avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
                avg_accuracy = (total_accuracy / total_samples) * 100
                
                pbar.set_postfix(loss=avg_loss, acc=avg_accuracy)
    
    return avg_loss, avg_accuracy

def train_model(config: dict, model: torch.nn.Module, train_dataloader: DataLoader, val_dataloader: DataLoader, criterion: torch.nn.Module, optimizer: torch.optim.Optimizer, device: torch.device, start_epoch: int):
    """
    Train the model.

    Args:
        config (dict): Configuration dictionary containing training settings.
        model (torch.nn.Module): The model to train.
        train_dataloader (DataLoader): The DataLoader for training data.
        val_dataloader (DataLoader): The DataLoader for validation data.
        criterion (torch.nn.Module): The loss function used during training.
        optimizer (torch.optim.Optimizer): The optimizer for gradient updates.
        device (torch.device): The device (CPU/GPU) for training.
        start_epoch (int): The epoch from which to start training (useful for resuming training).
    """
    num_epochs = config["training"]["num_epochs"]
    batch_size = config["training"]["batch_size"]

    for epoch in range(start_epoch, num_epochs):
        epoch_start_time = time.time()
        model.train()
        total_loss, total_accuracy, total_samples = 0, 0, 0
        
        with tqdm(train_dataloader, total=train_dataloader.dataset.num_samples // batch_size, desc=f"Epoch {epoch+1}/{num_epochs}", unit="batch") as pbar:
            for inputs, labels in pbar:
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()

                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()

                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

                optimizer.step()
                
                total_loss += loss.item() * batch_size
                total_accuracy += compute_accuracy(outputs, labels)
                total_samples += batch_size

                avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
                avg_accuracy = (total_accuracy / total_samples) * 100

                learning_rate = optimizer.param_groups[0]['lr']
                
                pbar.set_postfix(loss=avg_loss, accuracy=f'{avg_accuracy:.2f}%', lr=learning_rate)
        
        val_loss, val_accuracy = validate_model(model, val_dataloader, criterion, device, batch_size)
        
        epoch_end_time = time.time()
        epoch_time = epoch_end_time - epoch_start_time
        minutes, seconds = divmod(int(epoch_time), 60)

        print(f"Epoch {epoch + 1} completed. Training Loss: {avg_loss:.4f}, Training Accuracy: {avg_accuracy:.2f}%, Validation Loss: {val_loss:.4f}, Validation Accuracy: {val_accuracy:.2f}%, Time: {minutes}m{seconds}s, LR: {learning_rate}")

        save_checkpoint(model, optimizer, epoch + 1)
        save_logs([epoch + 1, avg_loss, avg_accuracy, val_loss, val_accuracy, learning_rate, f'{minutes}m{seconds}s'])

def main():
    """
    Main function to train the chess model.
    """
    warnings.filterwarnings("ignore")

    print(f"Loading configuration from {CONFIG_PATH}...")
    config = load_config(CONFIG_PATH)

    print(f"Loading encoded moves from {ENCODED_MOVES_PATH}...")
    encoded_moves = load_encoded_moves(ENCODED_MOVES_PATH)
    
    variables = {"num_classes": len(encoded_moves)}

    train_dataloader, val_dataloader = initialize_dataloaders(config, encoded_moves)
    device = setup_device()

    model = build_model(config['model'], variables, encoded_moves, 1).to(device)
    optimizer = build_optimizer(config['training']['optimizer'], model.parameters(), variables)
    criterion = CrossEntropyLoss()
    
    checkpoint = config['training']['checkpoint']
    if checkpoint != 0 :
        model, optimizer, start_epoch = load_checkpoint(os.path.join(MODEL_PATH, 'checkpoints', f'checkpoint_{checkpoint}.pth'), model, optimizer)
    else :
        start_epoch = 0

    train_model(config, model, train_dataloader, val_dataloader, criterion, optimizer, device, start_epoch)


if __name__ == "__main__":
    main()
