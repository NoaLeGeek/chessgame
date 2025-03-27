import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

file_path = ''
df = pd.read_csv(file_path)


plt.figure(figsize=(18, 5))

plt.subplot(1, 3, 1)  
plt.plot(df["Epoch"], df["Training Loss"], label="Training Loss", marker="o", linestyle="-", color="blue")
plt.plot(df["Epoch"], df["Validation Loss"], label="Validation Loss", marker="s", linestyle="--", color="red")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.title("Training vs Validation Loss")
plt.legend()
plt.grid(True)

plt.subplot(1, 3, 2)  
plt.plot(df["Epoch"], df["Training Accuracy (%)"], label="Training Accuracy", marker="o", linestyle="-", color="green")
plt.plot(df["Epoch"], df["Validation Accuracy (%)"], label="Validation Accuracy", marker="s", linestyle="--", color="orange")
plt.xlabel("Epochs")
plt.ylabel("Accuracy (%)")
plt.title("Training vs Validation Accuracy")
plt.legend()
plt.grid(True)

plt.subplot(1, 3, 3)  
plt.plot(df["Epoch"], df["Learning Rate"], label="Learning Rate", marker="o", linestyle="-", color="purple")
plt.xlabel("Epochs")
plt.ylabel("Learning Rate")
plt.title("Learning Rate Evolution")
plt.yscale("log") 
plt.legend()
plt.grid(True)

plt.tight_layout()  
plt.show()
