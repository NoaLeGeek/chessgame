from PIL import Image
import tkinter as tk
import ctypes
import os
from tkinter import filedialog

width, height = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1) - 48 - 23
# 1 is hiding -1 is showing
mode = 1
# 1 is second image towards the first -1 is the first image towards the second
arrow = 1
first_image = ""
second_image = ""
win = tk.Tk()

def select_file(text, index):
    fileTypes = (('PNG files', '*.png'),)
    fileName = filedialog.askopenfilename(title=text, initialdir='~', filetypes=fileTypes)
    if index == 1:
        first_image = fileName
        if first_image == "":
            return
        first_image_label['text'] = f"First image selected:\n{os.path.basename(fileName)}"
    else:
        second_image = fileName
        if second_image == "":
            return
        second_image_label['text'] = f"Second image selected:\n{os.path.basename(fileName)}"

def save_file(text):
    fileTypes = (('PNG files', '*.png'),)
    fileName = filedialog.asksaveasfilename(title=text, initialdir='~', filetypes=fileTypes)
    return fileName

def combine_pixels(pixel1, pixel2):
    return bin((pixel1 & 0b11110000) | (pixel2 >> 4))

def change_mode():
    global mode
    mode *= -1
    # hide mode
    for widget in [hide_button, show_button]:
        widget.config(state=tk.NORMAL if widget['state'] == tk.DISABLED else tk.DISABLED)
    if mode == 1:
        
    # show mode
    else:
        pass

def flip_arrow():
    global arrow
    arrow *= -1
    arrow_button['text'] = ("<" if arrow == 1 else "") + "-"*10 + (">" if arrow == -1 else "")

win.geometry(f"{width}x{height}")
win.title("title")
win.config(bg="white")
win.columnconfigure(tuple(range(6)), weight=1)
win.rowconfigure(tuple(range(6)), weight=1)

hide_button = tk.Button(win, text="Hide", command=change_mode)
hide_button.bindtags(("hide",) + hide_button.bindtags())
hide_button.grid(row=0, column=0, columnspan=3, sticky="new")
hide_button.config(state=tk.DISABLED)

first_image_button = tk.Button(win, text="Select first image", command=lambda: select_file("Select first image", 1))
first_image_button.bindtags(("hide.first_button",) + first_image_button.bindtags())
first_image_button.grid(row=1, column=0, columnspan=2, sticky="s")

first_image_label = tk.Label(win, text="No first image selected", justify=tk.CENTER)
first_image_label.bindtags(("hide.first_label",) + first_image_label.bindtags())
first_image_label.grid(row=2, column=0, columnspan=2, sticky="n")

arrow_button = tk.Button(win, text="<" + "-"*10, command=flip_arrow)
arrow_button.bindtags(("arrow",) + first_image_button.bindtags())
arrow_button.grid(row=1, column=2, columnspan=2, sticky="sew")

second_image_button = tk.Button(win, text="Select second image", command=lambda: select_file("Select second image", -1))
second_image_button.bindtags(("hide.second_button",) + second_image_button.bindtags())
second_image_button.grid(row=1, column=4, columnspan=2, sticky="s")

second_image_label = tk.Label(win, text="No second image selected", justify=tk.CENTER)
second_image_label.bindtags(("hide.second_label",) + second_image_label.bindtags())
second_image_label.grid(row=2, column=4, columnspan=2, sticky="n")

show_button = tk.Button(win, text="Show", command=change_mode)
show_button.bindtags(("show",) + show_button.bindtags())
show_button.grid(row=0, column=3, columnspan=3, sticky="new")

quit_button = tk.Button(win, text="Quit", command=win.destroy)
quit_button.grid(row=5, column=0, columnspan=6, sticky="sew")

win.mainloop()