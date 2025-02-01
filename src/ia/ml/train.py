import csv
import json
import time
import yaml
import torch
import warnings
import torch_directml

from tqdm import tqdm
from dataset import ChessDataset
from torch.nn import CrossEntropyLoss
from torch.utils.data import DataLoader
from builder import build_model, build_optimizer, build_scheduler
from loader import load_checkpoint, load_config, load_encoded_moves

def initialize_dataloaders(training_data_path, validation_data_path, encoded_moves, batch_size, num_workers):
    """
    Initialize DataLoaders with specified parameters.

    Args:
        training_data_path (str): Path to the training dataset file.
        validation_data_path (str): Path to the validation dataset file.
        encoded_moves (dict): Dictionary of encoded moves.
        batch_size (int): Size of the batch.
        num_workers (int): Number of workers for data loading.

    Returns:
        DataLoader: DataLoader objects for training and validation datasets.
    """
    print("Initializing Training Dataset...")
    train_dataset = ChessDataset(training_data_path, encoded_moves, batch_size)
    print("Initializing Validation Dataset...")
    val_dataset = ChessDataset(validation_data_path, encoded_moves, batch_size)
    return DataLoader(train_dataset, batch_size=None, num_workers=num_workers), DataLoader(val_dataset, batch_size=None, num_workers=num_workers)

def setup_device():
    """
    Setup the device for computation.

    Returns:
        torch.device: The device to be used.
    """
    device = torch_directml.device()
    print(f"Used device: {device}")
    return device

def compute_accuracy(outputs, labels):
    """
    Compute the accuracy of the model's predictions.

    Args:
        outputs (torch.Tensor): Model outputs.
        labels (torch.Tensor): True labels.

    Returns:
        int: Number of correct predictions.
    """
    _, predicted = torch.max(outputs, 1)
    correct = (predicted == labels).sum().item()
    return correct

def save_logs(logs, filepath):
    """
    Save training logs to a CSV file.

    Args:
        logs (list): List of logs to save.
        filepath (str): Path to save the logs file.
    """
    with open(f"{filepath}/training_logs.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(["Epoch", "Training Loss", "Training Accuracy (%)", "Validation Loss", "Validation Accuracy (%)", "Time (min:sec)", "Learning Rate"])
        writer.writerow(logs)

def save_checkpoint(model, optimizer, scheduler, epoch, loss, filepath):
    """
    Save the model checkpoint.

    Args:
        model (torch.nn.Module): The model to save.
        optimizer (torch.optim.Optimizer): The optimizer.
        scheduler (torch.optim.lr_scheduler): The scheduler.
        epoch (int): The current epoch.
        loss (float): The current loss.
        filepath (str): Path to save the checkpoint.
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'scheduler_state_dict': scheduler.state_dict(),
        'loss': loss,
    }
    torch.save(checkpoint, f"{filepath}/checkpoint_{epoch}.pth")

def validate_model(model, dataloader, criterion, device):
    """
    Validate the model.

    Args:
        model (torch.nn.Module): The model to validate.
        dataloader (DataLoader): The DataLoader.
        criterion (torch.nn.Module): The loss function.
        device (torch.device): The device to use.

    Returns:
        float: Validation loss.
        float: Validation accuracy.
    """
    model.eval()
    total_loss = 0.0
    total_accuracy = 0
    total_samples = 0

    with torch.no_grad():
        with tqdm(dataloader, total=dataloader.dataset.num_batches, desc="Validation", unit="batch") as pbar:
            for inputs, labels in pbar:
                inputs, labels = inputs.to(device), labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)

                total_loss += loss.item() * inputs.size(0)
                total_samples += inputs.size(0)

                correct = compute_accuracy(outputs, labels)
                total_accuracy += correct

                avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
                avg_accuracy = (total_accuracy / total_samples) * 100

                pbar.set_postfix(val_loss=avg_loss, val_accuracy=f"{avg_accuracy:.2f}%")

    avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
    avg_accuracy = (total_accuracy / total_samples) * 100

    return avg_loss, avg_accuracy

def train_model(model, train_dataloader, val_dataloader, criterion, optimizer, scheduler, device, num_epochs, batch_size, checkpoint_path, logs_path, start_epoch):
    """
    Train the model.

    Args:
        model (torch.nn.Module): The model to train.
        train_dataloader (DataLoader): The DataLoader for training data.
        val_dataloader (DataLoader): The DataLoader for validation data.
        criterion (torch.nn.Module): The loss function.
        optimizer (torch.optim.Optimizer): The optimizer.
        scheduler (torch.optim.lr_scheduler): The scheduler.
        device (torch.device): The device to use.
        num_batches (int): Number of batches.
        num_epochs (int): Number of epochs.
        batch_size (int): Size of the batch.
        checkpoint_path (str): Path to save checkpoints.
        logs_path (str): Path to save logs.
        start_epoch (int): The starting epoch.
    """
    logs = []
    for epoch in range(start_epoch, num_epochs):
        start_time = time.time()
        model.train()
        total_loss = 0.0
        total_accuracy = 0
        total_samples = 0

        print(f"Starting epoch {epoch + 1}/{num_epochs}...")

        with tqdm(train_dataloader, total=train_dataloader.dataset.num_batches, desc=f"Epoch {epoch + 1}/{num_epochs}", unit="batch") as pbar:
            for inputs, labels in pbar:
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()

                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()

                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

                optimizer.step()

                total_loss += loss.item() * batch_size
                total_samples += batch_size

                correct = compute_accuracy(outputs, labels)
                total_accuracy += correct

                avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
                avg_accuracy = (total_accuracy / total_samples) * 100

                pbar.set_postfix(loss=avg_loss, accuracy=f"{avg_accuracy:.2f}%")

        scheduler.step()

        val_loss, val_accuracy = validate_model(model, val_dataloader, criterion, device)

        end_time = time.time()
        epoch_time = end_time - start_time
        minutes, seconds = divmod(int(epoch_time), 60)

        learning_rate = optimizer.param_groups[0]['lr']

        logs.append([epoch + 1, avg_loss, avg_accuracy, val_loss, val_accuracy, f"{minutes}m{seconds}s", learning_rate])

        print(f"Epoch {epoch + 1} completed. Training Loss: {avg_loss:.4f}, Training Accuracy: {avg_accuracy:.2f}%, Validation Loss: {val_loss:.4f}, Validation Accuracy: {val_accuracy:.2f}%, Time: {minutes}m{seconds}s, LR: {learning_rate}")

        save_checkpoint(model, optimizer, scheduler, epoch + 1, avg_loss, checkpoint_path)
        save_logs(logs[-1], logs_path)

def main():
    """
    Main function to train the chess model.
    """
    warnings.filterwarnings("ignore")
    
    config = load_config("models/metadatas/config.yaml")
    encoded_moves = load_encoded_moves(config["encoded_moves_path"])

    variables = {"num_classes": len(encoded_moves)}

    train_dataloader, val_dataloader = initialize_dataloaders(config["training_data_path"], config["validation_data_path"], encoded_moves, config["batch_size"], config["num_workers"])

    with open(config["encoded_moves_path"], "w") as file:
        json.dump(encoded_moves, file)

    device = setup_device()

    model = build_model(config["architecture"], variables, encoded_moves).to(device)
    optimizer = build_optimizer(config["optimizer"], model.parameters(), variables)
    scheduler = build_scheduler(config["scheduler"], optimizer, variables)
    criterion = CrossEntropyLoss()

    try:
        model, optimizer, scheduler, start_epoch, last_loss = load_checkpoint(config["checkpoint_path"], model, optimizer, scheduler)
        print(f"Checkpoint loaded from epoch {start_epoch} with loss {last_loss}")
    except FileNotFoundError:
        print("No checkpoint found, starting from scratch.")
        start_epoch = 0

    train_model(
        model, train_dataloader, val_dataloader, criterion, optimizer, scheduler, device,
        config["epochs"], config["batch_size"],
        config["checkpoint_save_path"], config["logs_save_path"], start_epoch
    )

if __name__ == "__main__":
    main()
