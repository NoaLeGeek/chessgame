from PIL import Image
import tkinter as tk
import ctypes
from tkinter import filedialog

width, height = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1) - 48 - 23
# 1 is hiding -1 is showing
mode = 1
# 1 is second image towards the first -1 is the first image towards the second
arrow = 1
first_image = ""
second_image = ""
win = tk.Tk()

def select_file_toOpen(text, index):
    fileTypes = (('PNG files', '*.png'),)
    fileName = filedialog.askopenfilename(title=text, initialdir='~', filetypes=fileTypes)
    if index == 1:
        first_image = fileName
        first_image_label['text'] = f"First image selected: {fileName}"
        first_image_image = tk.Image()
    else:
        second_image = fileName
        second_image_label['text'] = f"Second image selected: {fileName}"

def select_file_toSave(text):
    fileTypes = (('PNG files', '*.png'),)
    fileName = filedialog.asksaveasfilename(title=text, initialdir='~', filetypes=fileTypes)
    return fileName

def combine_pixels(pixel1, pixel2):
    return bin((pixel1 & 0b11110000) | (pixel2 >> 4))

def toggle_buttons():
    global mode
    for widget in [hide_button, show_button, first_image_button, second_image_button]:
        if widget.bindtags()[0] in ("hide", "show"):
            widget.config(state=tk.NORMAL if widget['state'] == tk.DISABLED else tk.DISABLED)
        else:
            if widget.winfo_ismapped():
                widget.pack_forget()
            else:
                widget.pack(side=tk.BOTTOM, fill=tk.X)
    mode *= -1

def flip_arrow():
    arrow *= -1

win.geometry(f"{width}x{height}")
win.title("title")
win.config(bg="deepskyblue")
for i in range(6):
    win.columnconfigure(i, weight=1)
win.rowconfigure(3, weight=1)
hide_button = tk.Button(win, text="Hide", command=toggle_buttons)
hide_button.bindtags(("hide",) + hide_button.bindtags())
hide_button.grid(row=0, column=0, columnspan=3, sticky="ew")
hide_button.config(state=tk.DISABLED)
first_image_button = tk.Button(win, text="Select first image", command=lambda: select_file_toOpen("Select first image", 1))
first_image_button.bindtags(("hide.first_button",) + first_image_button.bindtags())
first_image_button.grid(row=1, column=0, columnspan=2, pady=50)
first_image_label = tk.Label(win, text="No first image selected")
first_image_label.bindtags(("hide.first_label",) + first_image_label.bindtags())
first_image_label.grid(row=2, column=0, columnspan=2)
arrow_button = tk.Button(win, text="🡰" + "-"*10, command=flip_arrow) #probably do an image 
arrow_button.bindtags(("arrow",) + first_image_button.bindtags())
arrow_button.grid(row=1, column=2, columnspan=2, pady=50, sticky="ew")
second_image_button = tk.Button(win, text="Select second image", command=lambda: select_file_toOpen("Select second image", -1))
second_image_button.bindtags(("hide.second_button",) + second_image_button.bindtags())
second_image_button.grid(row=1, column=4, columnspan=2, pady=50)
second_image_label = tk.Label(win, text="No second image selected")
second_image_label.bindtags(("hide.second_label",) + second_image_label.bindtags())
second_image_label.grid(row=2, column=4, columnspan=2)
show_button = tk.Button(win, text="Show", command=toggle_buttons)
show_button.bindtags(("show",) + show_button.bindtags())
show_button.grid(row=0, column=3, columnspan=3, sticky="ew")
quit_button = tk.Button(win, text="Quit", command=win.destroy)
quit_button.grid(row=4, column=0, columnspan=6, sticky="ew")
win.mainloop()