import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

file_path = "models/metadatas/training_logs.csv"
df = pd.read_csv(file_path)

df["Time (sec)"] = df["Time (min:sec)"].apply(lambda x: int(x.split("m")[0]) * 60 + int(x.split("m")[1][:-1]))

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
plt.title("Évolution du Learning Rate")
plt.yscale("log") 
plt.legend()
plt.grid(True)

plt.tight_layout()  
plt.show()
