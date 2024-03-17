from PIL import Image
import tkinter as tk
import ctypes
from tkinter import filedialog

width, height = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
win = tk.Tk()

def select_file_toOpen(text):
    fileTypes = (('png files', '*.png'),)
    fileName = filedialog.askopenfilename(title=text, initialdir='~', filetypes=fileTypes)
    return fileName

def select_file_toSave(text):
    fileTypes = (('png files', '*.png'),)
    fileName = filedialog.asksaveasfilename(title=text, initialdir='~', filetypes=fileTypes)
    return fileName

def combine_pixels(pixel1, pixel2):
    return bin((pixel1 & 0b11110000) | (pixel2 >> 4))

win.geometry(f"{width}x{height}")
win.title("title")
win.config(bg="bisque")
hide_button = tk.Button(win, text="Hide", width=round((win.winfo_reqwidth())/2), height=1)
hide_button.pack(side="top", anchor="nw")
show_button = tk.Button(win, text="Show", width=round((win.winfo_reqwidth())/2), height=1)
show_button.pack(side="top", anchor="ne")
quit_button = tk.Button(win, text="Quit", command=lambda: win.destroy(), width=win.winfo_reqwidth(), height=1)
quit_button.pack(side="bottom")
win.mainloop()