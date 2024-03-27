from PIL import Image, ImageTk
import tkinter as tk
import ctypes
import os
import json
from tkinter import filedialog, ttk

WIDTH, HEIGHT = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1) - 48 - 23
# 1 is hiding -1 is showing
mode = 1
# 1 is second image towards the first -1 is the first image towards the second
arrow = 1
first_image = ""
second_image = ""
hidden_image = None
win = tk.Tk()
language = tk.StringVar()

def select_file(text, index):
    global first_image, second_image
    fileTypes = (('PNG files', '*.png'),)
    filePath = filedialog.askopenfilename(title=text, initialdir='~', filetypes=fileTypes)
    if index == 1:
        first_image = filePath
        if first_image == "":
            return
        first_label['text'] = f"First image selected:\n{os.path.basename(first_image)}"
        show_first_button.config(state=tk.NORMAL)
    else:
        second_image = filePath
        if second_image == "":
            return
        second_label['text'] = f"Second image selected:\n{os.path.basename(second_image)}"
        show_second_button.config(state=tk.NORMAL)
    if first_image != "" and second_image != "":
        hide_image_button.config(state=tk.NORMAL)

def save_file(text):
    fileTypes = (('PNG files', '*.png'),)
    fileName = filedialog.asksaveasfilename(title=text, initialdir='~', filetypes=fileTypes)
    return fileName

def combine_pixels(pixel1, pixel2):
    return bin((pixel1 & 0b11110000) | (pixel2 >> 4))

def open_image(index):
    global first_image, second_image
    try:
        image = Image.open(first_image if index == 1 else second_image)
        return image
    except FileNotFoundError:
        print("Fichier non trouvé. Veuillez vérifier le chemin d'accès.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def change_mode():
    global mode
    mode *= -1
    for widget in [hide_button, show_button]:
        widget.config(state=tk.NORMAL if widget['state'] == tk.DISABLED else tk.DISABLED)
    change_widgets(win, "hide" if mode == 1 else "show")
        
def change_widgets(widget, mode):
    for w in widget.winfo_children():
        if w.winfo_children():
            change_widgets(w, mode)
        if mode == "show":
            if w.bindtags()[0].startswith("hide"):
                w.grid_remove()
            elif w.bindtags()[0].startswith("show"):
                w.grid()
        else:
            if w.bindtags()[0].startswith("hide"):
                w.grid()
            elif w.bindtags()[0].startswith("show"):
                w.grid_remove()

def hide_image():
    global hidden_image, first_image, second_image
    if first_image == "" or second_image == "":
        return
    image1 = open_image((-arrow+3)//2)
    image2 = open_image((arrow+3)//2)
    if image1.size != image2.size:
        print("Les images n'ont pas la même taille.")
        return
    hidden_image = Image.new("RGB", image1.size)
    pixels1 = image1.load()
    pixels2 = image2.load()
    for i in range(image1.size[0]):
        for j in range(image1.size[1]):
            r, g, b = pixels1[i, j]
            r2, g2, b2 = pixels2[i, j]
            r = int(combine_pixels(r, r2), 2)
            g = int(combine_pixels(g, g2), 2)
            b = int(combine_pixels(b, b2), 2)
            hidden_image.putpixel((i, j), (r, g, b))
    save_hidden_image.config(state=tk.NORMAL)
    show_hidden_image.config(state=tk.NORMAL)

def flip_arrow():
    global arrow
    arrow *= -1
    arrow_button['text'] = ("<" if arrow == 1 else "") + "-"*10 + (">" if arrow == -1 else "")

def translate(key):
    global language
    # On traduit le texte en fonction de la langue choisie.
    with open(f"{language.get()}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get(key, key)

def update_widget(widget):
    # Si le widget a pour tag "noTranslation", on ne met pas à jour son texte.
    if widget.bindtags()[0] != "noTranslation":
        # On met à jour le texte des widgets en fonction de la langue choisie.
        if "text" in widget.config():
            widget.config(text=translate(widget.bindtags()[0]))
        if isinstance(widget, tk.Tk):
            widget.title(translate(widget.bindtags()[0]))
    # On met à jour les widgets enfants du widget.
    if widget.winfo_children():
        for child in widget.winfo_children():
            update_widget(child)

win.geometry(f"{WIDTH}x{HEIGHT}")
win.title("title")
win.config(bg="white")
win.columnconfigure(tuple(range(6)), weight=1)
win.rowconfigure(tuple(range(6)), weight=1)

hide_button = tk.Button(win, text="Hide", command=change_mode)
hide_button.bindtags(("button.hide",) + hide_button.bindtags())
hide_button.grid(row=0, column=0, columnspan=3, sticky="new")
hide_button.config(state=tk.DISABLED)

first_button = tk.Button(win, text="Select first image", command=lambda: select_file("Select first image", 1), width=round(WIDTH/3))
first_button.bindtags(("hide.first_button",) + first_button.bindtags())
first_button.grid(row=0, column=0, columnspan=2, sticky="s")

first_label = tk.Label(win, text="No first image selected", justify=tk.CENTER, width=round(WIDTH/3))
first_label.bindtags(("hide.first_label",) + first_label.bindtags())
first_label.grid(row=1, column=0, columnspan=2, sticky="n")

show_first_button = tk.Button(win, text="Show first image", command=lambda: open_image(1).show(), width=round(WIDTH/3))
show_first_button.bindtags(("hide.show_first_button",) + show_first_button.bindtags())
show_first_button.grid(row=1, column=0, columnspan=2, sticky="s")
show_first_button.config(state=tk.DISABLED)

arrow_button = tk.Button(win, text="<" + "-"*10, command=flip_arrow, width=round(WIDTH/3))
arrow_button.bindtags(("hide.arrow",) + arrow_button.bindtags())
arrow_button.grid(row=0, column=2, columnspan=2, sticky="sew")

hide_image_button = tk.Button(win, text="Hide image", command=lambda: hide_image(), width=round(WIDTH/3))
hide_image_button.bindtags(("hide.hide_image_button",) + hide_image_button.bindtags())
hide_image_button.grid(row=1, column=2, columnspan=2, sticky="sew")
hide_image_button.config(state=tk.DISABLED)

save_hidden_image = tk.Button(win, text="Save hidden image", command=lambda: hidden_image.save(save_file("Save the hidden image"), "PNG"), width=round(WIDTH/3))
save_hidden_image.bindtags(("hide.save_hidden_image",) + save_hidden_image.bindtags())
save_hidden_image.grid(row=2, column=2, columnspan=2, sticky="new")
save_hidden_image.config(state=tk.DISABLED)

show_hidden_image = tk.Button(win, text="Show hidden image", command=lambda: hidden_image.show(), width=round(WIDTH/3))
show_hidden_image.bindtags(("hide.show_hidden_image",) + show_hidden_image.bindtags())
show_hidden_image.grid(row=2, column=2, columnspan=2, sticky="sew")
show_hidden_image.config(state=tk.DISABLED)

language_text = tk.Label(win, font=("Helvetica", 9))
language_text.bindtags(("config.language_text",) + language_text.bindtags())
language_text.grid(row=3, column=2, columnspan=2, sticky="s")

language_option = ttk.OptionMenu(win, language, "fr", "fr", "en", command=lambda _: update_widget(win))
language_option.grid(row=4, column=2, columnspan=2, sticky="n")

second_button = tk.Button(win, text="Select second image", command=lambda: select_file("Select second image", -1), width=round(WIDTH/3))
second_button.bindtags(("hide.second_button",) + second_button.bindtags())
second_button.grid(row=0, column=4, columnspan=2, sticky="s")

second_label = tk.Label(win, text="No second image selected", justify=tk.CENTER, width=round(WIDTH/3))
second_label.bindtags(("hide.second_label",) + second_label.bindtags())
second_label.grid(row=1, column=4, columnspan=2, sticky="n")

show_second_button = tk.Button(win, text="Show second image", command=lambda: open_image(2).show(), width=round(WIDTH/3))
show_second_button.bindtags(("hide.show_second_button",) + show_second_button.bindtags())
show_second_button.grid(row=1, column=4, columnspan=2, sticky="s")
show_second_button.config(state=tk.DISABLED)

show_button = tk.Button(win, text="Show", command=change_mode)
show_button.bindtags(("button.hide",) + show_button.bindtags())
show_button.grid(row=0, column=3, columnspan=3, sticky="new")

quit_button = tk.Button(win, text="Quit", command=win.destroy)
quit_button.grid(row=5, column=0, columnspan=6, sticky="sew")

win.mainloop()