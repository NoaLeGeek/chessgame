from PIL import Image, ImageTk
import tkinter as tk
import ctypes
import os
import json
from tkinter import filedialog, ttk, messagebox

# La librarie ctypes permet ici de récupérer la taille de l'écran de l'utilisateur
# 48 correspond à la hauteur de la barre de tâches de Windows
# 23 correspond à la hauteur de la barre de titre de la fenêtre
WIDTH, HEIGHT = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1) - 48 - 23
# Si le mode est à 1 alors on est dans le mode où on veut cacher une image dans une image
# Si le mode est à -1 alors on est dans le mode où on veut révéler une image cachée dans une image
mode = 1
# Si la flèche est à 1 alors on cache la deuxième image dans la première
# Si la flèche est à -1 alors on cache la première image dans la deuxième
arrow = 1
# Correspond à la première image
first_image = ""
# Correspond à la deuxième image
second_image = ""
# Correspond à l'image sélectionnée pour révéler l'image cachée
show_image = ""
# Correspond à l'image cachée dans une image
hidden_image = None
# Correspond à l'image initiale révélée d'une image cachée dans une image
initial_image = None
# Correspond à l'image cachée révélée d'une image cachée dans une image
revealed_image = None
win = tk.Tk()
# Sert à savoir quel langage est choisi
language = tk.StringVar()
# Sert à savoir si les images cachées doivent être de la même taille (oui par défaut)
config_hide = tk.BooleanVar()

# Permet de sélectionner un fichier
def select_file(text, index):
    global first_image, second_image, show_image
    fileTypes = (('PNG files', '*.png'),)
    filePath = filedialog.askopenfilename(title=text, initialdir='~', filetypes=fileTypes)
    # En fonction de l'index, on met à jour la première, la deuxième ou l'image à révéler
    match index:
        case 1:
            first_image = filePath
            if first_image == "":
                return
            # On met à jour le texte du label lorsque l'image est sélectionnée
            h_first_label.bindtags(("hide.h_first_label.selected",) + h_first_label.bindtags()[1:])
            # On met à jour le texte du label en le traduisant
            update_widget(h_first_label)
            # On active le bouton pour afficher l'image puisqu'on a sélectionné une image
            h_show_first_button.config(state=tk.NORMAL)

            # On fait ce même processus pour l'index 2
        case 2:
            second_image = filePath
            if second_image == "":
                return
            h_second_label.bindtags(("hide.h_second_label.selected",) + h_second_label.bindtags()[1:])
            update_widget(h_second_label)
            h_show_second_button.config(state=tk.NORMAL)
        case 3:
            show_image = filePath
            if show_image == "":
                return
            select_label.bindtags(("show.select_label.selected",) + select_label.bindtags()[1:])
            update_widget(select_label)
            # On active les boutons pour afficher l'image initiale et révélée
            show_initial_button.config(state=tk.NORMAL)
            show_reveal_button.config(state=tk.NORMAL)
            # On active les boutons pour obtenir l'image initiale et révélée
            reveal_button.config(state=tk.NORMAL)
            initial_button.config(state=tk.NORMAL)
            # On active les boutons pour sauvegarder l'image initiale et révélée
            save_initial_button.config(state=tk.NORMAL)
            save_reveal_button.config(state=tk.NORMAL)
            # On active les boutons pour afficher l'image sélectionnée
            show_select_button.config(state=tk.NORMAL)
    if first_image != "" and second_image != "":
        h_image_button.config(state=tk.NORMAL)

# Permet de sauvegarder un fichier
def save_file(text):
    fileTypes = (('PNG files', '*.png'),)
    fileName = filedialog.asksaveasfilename(title=text, initialdir='~', filetypes=fileTypes)
    # On ajoute l'extension .png si elle n'est pas présente
    if fileName and not fileName.endswith(".png"):
        fileName += ".png"
    return fileName

# Permet de combiner deux pixels pour cacher une image dans une autre
def combine_pixels(pixel1, pixel2):
    return bin((pixel1 & 0b11110000) | (pixel2 >> 4))

# Permet d'ouvrir une image en fonction de l'index donné
def open_image(index):
    global first_image, second_image, initial_image, revealed_image
    try:
        match index:
            case 1:
                image = Image.open(first_image)
            case 2:
                image = Image.open(second_image)
            case 3:
                image = Image.open(show_image)
        return image
    # On gère les erreurs qui peuvent survenir lors de l'ouverture d'une image
    except FileNotFoundError:
        messagebox.showerror(translate("error.error"), translate("error.file_not_found"))
    except Exception as e:
        messagebox.showerror(translate("error.error"), translate("error.load_image").format(e))

# Permet de changer le mode
def change_mode():
    global mode
    mode *= -1
    for widget in [h_mode_button, show_button]:
        widget.config(state=tk.NORMAL if widget['state'] == tk.DISABLED else tk.DISABLED)
    change_widgets(win, "hide" if mode == 1 else "show")
        
# Permet de gérer la disparition/apparition des widgets propre à chacun des modes
def change_widgets(widget, mode):
    for w in widget.winfo_children():
        if w.winfo_children():
            change_widgets(w, mode)
        # Si le mode est "hide" alors on cache les widgets du mode "show" et on fait apparaître les widgets du mode "hide" et vice-versa
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

# Permet de cacher une image dans une autre image
def get_hide_image():
    global hidden_image, first_image, second_image
    if first_image == "" or second_image == "":
        return
    # Fonctions affines qui permettent de déterminer en fonction de la flèche laquelle des deux images est celle réceptrice et celle à cacher
    image1, image2 = open_image((-arrow+3)//2), open_image((arrow+3)//2)
    # Si les deux images n'ont pas la même taille et que l'option est activée, on affiche une erreur
    if image1.size != image2.size and config_hide.get():
        messagebox.showerror(translate("error.error"), translate("error.not_same_size"))
        return
    hidden_image, pixels1, pixels2 = Image.new("RGB", image1.size), image1.load(), image2.load()
    for i in range(image1.size[0]):
        for j in range(image1.size[1]):
            if i < image2.size[0] and j < image2.size[1]:
                r, g, b = pixels1[i, j][0:3]
                r2, g2, b2 = pixels2[i, j][0:3]
                r = int(combine_pixels(r, r2), 2)
                g = int(combine_pixels(g, g2), 2)
                b = int(combine_pixels(b, b2), 2)
                hidden_image.putpixel((i, j), (r, g, b))
            else:
                hidden_image.putpixel((i, j), pixels1[i, j])
    # On active les boutons pour sauvegarder et afficher l'image cachée
    h_save_button.config(state=tk.NORMAL)
    h_show_button.config(state=tk.NORMAL)

# Permet d'obtenir l'image initiale d'une image cachée
def get_initial_image():
    global initial_image, show_image
    if show_image == "":
        return
    image = Image.open(show_image)
    initial_image, pixels = Image.new("RGB", image.size), image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            r, g, b = pixels[i, j][0:3]
            r = r & 0b11110000
            g = g & 0b11110000
            b = b & 0b11110000
            initial_image.putpixel((i, j), (r, g, b))

# Permet d'obtenir l'image révélée d'une image cachée
def get_reveal_image():
    global revealed_image, show_image
    if show_image == "":
        return
    image = Image.open(show_image)
    revealed_image, pixels = Image.new("RGB", image.size), image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            r, g, b = pixels[i, j][0:3]
            r = (r & 0b00001111) << 4
            g = (g & 0b00001111) << 4
            b = (b & 0b00001111) << 4
            revealed_image.putpixel((i, j), (r, g, b))

# Permet de retourner la flèche pour changer quelle image sera cachée dans l'autre
def flip_arrow():
    global arrow
    arrow *= -1
    h_arrow_button['text'] = ("<" if arrow == 1 else "") + "-"*10 + (">" if arrow == -1 else "")

# Permet de traduire un texte en fonction de la langue choisie
def translate(key):
    global language
    # On traduit le texte en fonction de la langue choisie.
    with open(f"{language.get()}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get(key, key)

# Permet de mettre à jour le texte des widgets en fonction de la langue choisie
def update_widget(widget):
    # Si le widget a pour tag "noTranslation", on ne met pas à jour son texte
    if "noTranslation" not in widget.bindtags()[0]:
        # Met à jour le texte des widgets en fonction de la langue choisie
        if "text" in widget.config():
            widget.config(text=translate(widget.bindtags()[0]))
        if isinstance(widget, tk.Tk):
            widget.title(translate("title"))
        # Met à jour le widget s'il fait partie des widgets à formatter
        match widget.bindtags()[0]:
            case "hide.h_first_label.selected":
                widget['text'] = translate(widget.bindtags()[0]).format(os.path.basename(first_image), *open_image(1).size)
            case "hide.h_second_label.selected":
                widget['text'] = translate(widget.bindtags()[0]).format(os.path.basename(second_image), *open_image(2).size)
            case "show.select_label.selected":
                widget['text'] = translate(widget.bindtags()[0]).format(os.path.basename(show_image), *open_image(3).size)
    # On met à jour les widgets enfants du widget.
    if widget.winfo_children():
        for child in widget.winfo_children():
            update_widget(child)

win.geometry(f"{WIDTH}x{HEIGHT}")
win.title("title")
win.config(bg="white")
win.columnconfigure(tuple(range(6)), weight=1)
win.rowconfigure(tuple(range(6)), weight=1)

h_mode_button = tk.Button(win, command=change_mode)
h_mode_button.bindtags(("button.hide",) + h_mode_button.bindtags())
h_mode_button.grid(row=0, column=0, columnspan=3, sticky="new")
h_mode_button.config(state=tk.DISABLED)

h_first_button = tk.Button(win, command=lambda: select_file(translate("hide.h_first_button"), 1), width=round(WIDTH/3))
h_first_button.bindtags(("hide.h_first_button",) + h_first_button.bindtags())
h_first_button.grid(row=0, column=0, columnspan=2, sticky="s")

h_first_label = tk.Label(win, justify=tk.CENTER, width=round(WIDTH/3))
h_first_label.bindtags(("hide.h_first_label.not_selected",) + h_first_label.bindtags())
h_first_label.grid(row=1, column=0, columnspan=2, sticky="n")

h_show_first_button = tk.Button(win, command=lambda: open_image(1).show(), width=round(WIDTH/3))
h_show_first_button.bindtags(("hide.h_show_first_button",) + h_show_first_button.bindtags())
h_show_first_button.grid(row=1, column=0, columnspan=2, sticky="s")
h_show_first_button.config(state=tk.DISABLED)

h_arrow_button = tk.Button(win, text="<" + "-"*10, command=flip_arrow, width=round(WIDTH/3))
h_arrow_button.bindtags(("hide.noTranslation",) + h_arrow_button.bindtags())
h_arrow_button.grid(row=0, column=2, columnspan=2, sticky="sew")

h_image_button = tk.Button(win, command=lambda: get_hide_image(), width=round(WIDTH/3))
h_image_button.bindtags(("hide.h_image_button",) + h_image_button.bindtags())
h_image_button.grid(row=1, column=2, columnspan=2, sticky="sew")
h_image_button.config(state=tk.DISABLED)

h_save_button = tk.Button(win, command=lambda: hidden_image.save(save_file(translate("hide.h_save_button")), "PNG"), width=round(WIDTH/3))
h_save_button.bindtags(("hide.h_save_button",) + h_save_button.bindtags())
h_save_button.grid(row=2, column=2, columnspan=2, sticky="new")
h_save_button.config(state=tk.DISABLED)

h_show_button = tk.Button(win, command=lambda: hidden_image.show(), width=round(WIDTH/3))
h_show_button.bindtags(("hide.h_show_button",) + h_show_button.bindtags())
h_show_button.grid(row=2, column=2, columnspan=2, sticky="sew")
h_show_button.config(state=tk.DISABLED)

h_checkbutton = tk.Checkbutton(win, variable=config_hide, onvalue=True, offvalue=False)
h_checkbutton.bindtags(("hide.h_checkbutton",) + h_checkbutton.bindtags())
h_checkbutton.grid(row=3, column=2, columnspan=2, sticky="n")
config_hide.set(True)

language_label = tk.Label(win, font=("Helvetica", 9))
language_label.bindtags(("config.language_label",) + language_label.bindtags())
language_label.grid(row=3, column=2, columnspan=2, sticky="s")

language_option = ttk.OptionMenu(win, language, "fr", "fr", "en", command=lambda _: update_widget(win))
language_option.grid(row=4, column=2, columnspan=2, sticky="n")

h_second_button = tk.Button(win, command=lambda: select_file(translate("hide.h_second_button"), 2), width=round(WIDTH/3))
h_second_button.bindtags(("hide.h_second_button",) + h_second_button.bindtags())
h_second_button.grid(row=0, column=4, columnspan=2, sticky="s")

h_second_label = tk.Label(win, justify=tk.CENTER, width=round(WIDTH/3))
h_second_label.bindtags(("hide.h_second_label.not_selected",) + h_second_label.bindtags())
h_second_label.grid(row=1, column=4, columnspan=2, sticky="n")

h_show_second_button = tk.Button(win, command=lambda: open_image(2).show(), width=round(WIDTH/3))
h_show_second_button.bindtags(("hide.h_show_second_button",) + h_show_second_button.bindtags())
h_show_second_button.grid(row=1, column=4, columnspan=2, sticky="s")
h_show_second_button.config(state=tk.DISABLED)

show_button = tk.Button(win, command=change_mode)
show_button.bindtags(("button.show",) + show_button.bindtags())
show_button.grid(row=0, column=3, columnspan=3, sticky="new")

select_button = tk.Button(win, command=lambda: select_file(translate("show.select_button"), 3))
select_button.bindtags(("show.select_button",) + select_button.bindtags())
select_button.grid(row=0, column=2, columnspan=2, sticky="sew")
select_button.grid_remove()

select_label = tk.Label(win, justify=tk.CENTER)
select_label.bindtags(("show.select_label.not_selected",) + select_label.bindtags())
select_label.grid(row=1, column=2, columnspan=2, sticky="new")
select_label.grid_remove()

show_select_button = tk.Button(win, command=lambda: open_image(3).show())
show_select_button.bindtags(("show.show_select_button",) + show_select_button.bindtags())
show_select_button.grid(row=1, column=2, columnspan=2, sticky="sew")
show_select_button.grid_remove()
show_select_button.config(state=tk.DISABLED)

initial_button = tk.Button(win, command=get_initial_image)
initial_button.bindtags(("show.initial_button",) + initial_button.bindtags())
initial_button.grid(row=2, column=1, columnspan=2, sticky="new")
initial_button.grid_remove()
initial_button.config(state=tk.DISABLED)

show_initial_button = tk.Button(win, command=lambda: initial_image.show())
show_initial_button.bindtags(("show.show_initial_button",) + show_initial_button.bindtags())
show_initial_button.grid(row=2, column=1, columnspan=2, sticky="sew")
show_initial_button.grid_remove()
show_initial_button.config(state=tk.DISABLED)

save_initial_button = tk.Button(win, command=lambda: initial_image.save(save_file(translate("show.save_initial_image")), "PNG"))
save_initial_button.bindtags(("show.save_initial_button",) + save_initial_button.bindtags())
save_initial_button.grid(row=3, column=1, columnspan=2, sticky="new")
save_initial_button.grid_remove()
save_initial_button.config(state=tk.DISABLED)

reveal_button = tk.Button(win, command=get_reveal_image)
reveal_button.bindtags(("show.reveal_button",) + reveal_button.bindtags())
reveal_button.grid(row=2, column=3, columnspan=2, sticky="new")
reveal_button.grid_remove()
reveal_button.config(state=tk.DISABLED)

show_reveal_button = tk.Button(win, command=lambda: revealed_image.show())
show_reveal_button.bindtags(("show.show_reveal_button",) + show_reveal_button.bindtags())
show_reveal_button.grid(row=2, column=3, columnspan=2, sticky="sew")
show_reveal_button.grid_remove()
show_reveal_button.config(state=tk.DISABLED)

save_reveal_button = tk.Button(win, command=lambda: revealed_image.save(save_file(translate("show.save_reveal_image")), "PNG"))
save_reveal_button.bindtags(("show.save_reveal_button",) + save_reveal_button.bindtags())
save_reveal_button.grid(row=3, column=3, columnspan=2, sticky="new")
save_reveal_button.grid_remove()
save_reveal_button.config(state=tk.DISABLED)

quit_button = tk.Button(win, text="Quit", command=win.destroy)
quit_button.bindtags(("button.quit",) + quit_button.bindtags())
quit_button.grid(row=5, column=0, columnspan=6, sticky="sew")

update_widget(win)

win.mainloop()