#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import json
from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.colorchooser import askcolor
from tkinter import ttk

# rows et columns servent à gérer la taille de la grille pour les variantes.
rows, columns = 3, 3
lengthBoard = 550
margin = 20
length = (lengthBoard - 2 * margin) / 3
boardData = None
# turn sert à savoir qui doit jouer. 1 pour le joueur 1, -1 pour le joueur 2 et 0 pour le match nul.
# turn est explicitement défini à 0 lorsqu'il y a match nul afin de faciliter la gestion du texte de l'état de la partie.
turn = None
numberPlays = 0
gameOver = False
win = Tk()
# selectOpponent sert à savoir si le joueur joue contre un autre joueur ou contre un bot.
selectOpponent = IntVar()
selectOpponent.set(1)
# selectBot sert à savoir quel bot le joueur affronte.
selectBot = IntVar()
selectBot.set(1)
# configSize sert à gérer la taille de la grille pour les variantes.
configSize = IntVar()
configSize.set(3)
# configWinSize sert à gérer la taille de l'alignement pour les variantes.
configWinSize = IntVar()
configWinSize.set(3)
# configLanguage sert à gérer la langue du jeu.
configLanguage = StringVar()
# configColorX et configColorO servent à gérer les couleurs des symboles.
configColorX = "#FF0000"
configColorO = "#0000FF"


def init():
    global boardData, numberPlays, turn, gameOver, rows, columns, length
    # rows et columns sont redéfinis en fonction de la taille de la grille choisie par le joueur.
    rows, columns = configSize.get(), configSize.get()
    # On doit aussi redéfinir la longueur des cases en fonction de la taille de la grille.
    length = (lengthBoard - 2 * margin) / rows
    # On supprime tout ce qui est sur le canvas afin de pouvoir redessiner une grille de la bonne taille.
    board.delete("all")
    # boardData est une liste de rows listes contenant chacune columns 0.
    boardData = [[0] * columns for _ in range(rows)]
    # turn est défini aléatoirement afin de déterminer qui commence.
    turn = random.choice([1, -1])
    # On redéfinit les variables qui servent à gérer la partie pour une nouvelle partie.
    numberPlays = 0
    gameOver = False
    drawBoard()


def newGame():
    # On réinitialise la partie pour commencer une nouvelle partie.
    init()
    updateState()
    if turn == -1 and selectOpponent.get() == 2:
        computerPlays()
    # On bind le clic gauche de la souris sur le canvas à la fonction click.
    board.bind("<Button-1>", click)
    # On désactive les boutons et les spinbox afin d'éviter que le joueur ne change les paramètres de la partie en cours.
    pVSp.configure(state=DISABLED)
    pVSb.configure(state=DISABLED)
    botRandom.configure(state=DISABLED)
    botSmart.configure(state=DISABLED)
    spinboxSize.configure(state=DISABLED)
    spinboxWinSize.configure(state=DISABLED)
    buttonColorX.configure(state=DISABLED)
    buttonColorO.configure(state=DISABLED)
    optionLanguage.configure(state=DISABLED)


def drawBoard():
    # On dessine la grille en fonction de rows et columns.
    y = 0
    for _ in range(rows + 1):
        board.create_line(margin, y + margin, lengthBoard - margin, y + margin, width=4, fill="black")
        y += length
    x = 0
    for _ in range(columns + 1):
        board.create_line(x + margin, margin, x + margin, lengthBoard - margin, width=4, fill="black")
        x += length


def click(event):
    global numberPlays, turn, boardData
    if gameOver or (turn == -1 and selectOpponent.get() == 2):
        return
    # On récupère les coordonnées de la case sur laquelle le joueur a cliqué.
    x, y = int((event.x - margin) // length), int((event.y - margin) // length)
    # Si le joueur clique en dehors de la grille ou sur une case déjà jouée, on ne fait rien.
    if x < 0 or x > columns - 1 or y < 0 or y > rows - 1 or boardData[x][y] in [-1, 1]:
        return
    boardData[x][y] = turn
    numberPlays += 1
    # On dessine le symbole du joueur sur la case sur laquelle il a cliqué en sachant que le premier symbole est toujours un X.
    if numberPlays % 2 == 1:
        drawCross(x, y)
    else:
        drawCircle(x, y)
    isGameOver()
    # On aurait pu changer le tour malgré la condition mais on a besoin de faire comme cela pour pouvoir gérer le texte de l'état de la partie.
    if not gameOver:
        turn *= -1
        if selectOpponent.get() == 2:
            computerPlays()
    updateState()


def drawCircle(x: int, y: int):
    # On dessine un cercle en fonction des coordonnées de la case sur laquelle le joueur a cliqué.
    x1 = 2 * margin + x * length
    y1 = 2 * margin + y * length
    x2 = (x + 1) * length
    y2 = (y + 1) * length
    board.create_oval(x1, y1, x2, y2, width=5, outline=configColorO)


def drawCross(x: int, y: int):
    # On dessine une croix en fonction des coordonnées de la case sur laquelle le joueur a cliqué.
    x1 = 2 * margin + x * length
    y1 = 2 * margin + y * length
    x2 = (x + 1) * length
    y2 = (y + 1) * length
    board.create_line(x1, y1, x2, y2, width=5, fill=configColorX)
    board.create_line(x1, y2, x2, y1, width=5, fill=configColorX)


def isGameOver():
    global gameOver, turn, boardData
    # Pour chaque joueur, on vérifie si l'un de ses symboles forme un alignement gagnant.
    for player in [-1, 1]:
        for j in range(columns - configWinSize.get() + 1):
            for i in range(rows):
                # On vérifie si l'alignement gagnant est horizontal.
                if all(boardData[i][j + k] == player for k in range(configWinSize.get())):
                    drawLine(i, j, i, j + configWinSize.get() - 1)
                    gameOver = True
                # On vérifie si l'alignement gagnant est vertical.
                if all(boardData[j + k][i] == player for k in range(configWinSize.get())):
                    drawLine(j, i, j + configWinSize.get() - 1, i)
                    gameOver = True
            for i in range(rows - configWinSize.get() + 1):
                # On vérifie si l'alignement gagnant est diagonal.
                if all(boardData[i + k][j + k] == player for k in range(configWinSize.get())):
                    drawLine(i, j, i + configWinSize.get() - 1, j + configWinSize.get() - 1)
                    gameOver = True
                # On vérifie si l'alignement gagnant est anti-diagonal.
                if all(boardData[i + k][j + configWinSize.get() - 1 - k] == player for k in range(configWinSize.get())):
                    drawLine(i, j + configWinSize.get() - 1, i + configWinSize.get() - 1, j)
                    gameOver = True
    # S'il n'y a pas de gagnant et que le nombre de coups joués est égal au nombre de cases, c'est un match nul.
    if not gameOver and numberPlays > rows * columns - 1:
        turn = 0
        gameOver = True
    # Si la partie est terminée, on débind le clic gauche de la souris sur le canvas afin d'éviter que le joueur ne joue après la fin de la partie et on met à jour les scores.
    if gameOver:
        board.unbind("<Button-1>")
        score = list(map(int, textScore.cget("text").split("-")))
        textScore.config(
            text="{}-{}".format(score[0] + 1 if turn == 1 else score[0], score[1] + 1 if turn == -1 else score[1]))


def drawLine(x1, y1, x2, y2):
    # On dessine une ligne en fonction des coordonnées de l'alignement gagnant.
    x1_pixel = margin + length * (x1 + 0.5)
    y1_pixel = margin + length * (y1 + 0.5)
    x2_pixel = margin + length * (x2 + 0.5)
    y2_pixel = margin + length * (y2 + 0.5)
    color = "#{:02X}{:02X}{:02X}".format(int(int((configColorO if numberPlays % 2 == 0 else configColorX)[1:3], 16) * (116/255)), int(int((configColorO if numberPlays % 2 == 0 else configColorX)[3:5], 16) * (116/255)), int(int((configColorO if numberPlays % 2 == 0 else configColorX)[5:7], 16) * (116/255)))
    board.create_line(x1_pixel, y1_pixel, x2_pixel, y2_pixel, width=5, fill=color)


def computerPlays():
    global numberPlays, turn, gameOver, boardData
    x, y = None, None
    if selectBot.get() == 2:
        # -1 sert à vérifier si le bot a un coup gagnant et 1 sert à vérifier si le bot a un coup qui bloque le joueur. Si aucun des deux, le bot joue aléatoirement.
        # L'ordre du -1 et du 1 est important puisqu'il faut que le bot vérifie d'abord s'il peut gagner avant de vérifier s'il peut bloquer le joueur.
        for player in [-1, 1]:
            for j in range(columns - configWinSize.get() + 1):
                for i in range(rows):
                    # On vérifie si le bot a un coup gagnant ou un coup qui bloque le joueur horizontal.
                    if sum(boardData[i][j + k] for k in range(configWinSize.get())) == player * (configWinSize.get() - 1):
                        x, y = next((i, j + k) for k in range(configWinSize.get()) if boardData[i][j + k] == 0)
                        break
                    # On vérifie si le bot a un coup gagnant ou un coup qui bloque le joueur vertical.
                    if sum(boardData[j + k][i] for k in range(configWinSize.get())) == player * (configWinSize.get() - 1):
                        x, y = next((j + k, i) for k in range(configWinSize.get()) if boardData[j + k][i] == 0)
                        break
                # Si x est défini, cela signifie que le bot a trouvé un coup gagnant ou un coup qui bloque le joueur.
                # Il est important de sortir de la boucle afin de ne pas écraser un possible coup gagnant trouvé par un possible coup trouvé qui bloque le joueur.
                if x is not None:
                    break
                for i in range(rows - configWinSize.get() + 1):
                    # On vérifie si le bot a un coup gagnant ou un coup qui bloque le joueur diagonal.
                    if sum(boardData[i + k][j + k] for k in range(configWinSize.get())) == player * (configWinSize.get() - 1):
                        x, y = next((i + k, j + k) for k in range(configWinSize.get()) if boardData[i + k][j + k] == 0)
                        break
                    # On vérifie si le bot a un coup gagnant ou un coup qui bloque le joueur anti-diagonal.
                    if sum(boardData[i + k][j + configWinSize.get() - 1 - k] for k in range(configWinSize.get())) == player * (configWinSize.get() - 1):
                        x, y = next((i + k, j + configWinSize.get() - 1 - k) for k in range(configWinSize.get()) if boardData[i + k][j + configWinSize.get() - 1 - k] == 0)
                        break
            if x is not None:
                break
    # Si x n'est pas défini, cela signifie que le bot n'a pas trouvé de coup gagnant ou de coup qui bloque le joueur. Il joue donc aléatoirement.
    if x is None:
        x, y = random.choice(list(filter(lambda pos: boardData[pos[0]][pos[1]] == 0, [(i, j) for i in range(rows) for j in range(columns)])))
    boardData[x][y] = turn
    numberPlays += 1
    if numberPlays % 2 == 1:
        drawCross(x, y)
    else:
        drawCircle(x, y)
    isGameOver()
    # On aurait pu changer le tour malgré la condition mais on a besoin de faire comme cela pour pouvoir gérer le texte de l'état de la partie.
    if not gameOver:
        turn *= -1
    updateState()


def updateState():
    global turn, gameOver, numberPlays
    if gameOver:
        # On met à jour le texte de l'état de la partie en fonction de qui a gagné ou si c'est un match nul.
        if selectOpponent.get() == 2:
            textState.bindtags((("textState." + ("player.win" if turn == 1 else "bot.win" if turn == -1 else "draw")),) + textState.bindtags()[1:])
        else:
            textState.bindtags((("textState." + ("player{}.win".format(str(int(1.5-0.5*turn))) if turn in [1, -1] else "draw")),) + textState.bindtags()[1:])
        # On réactive les boutons et les spinbox pour pouvoir changer les paramètres de la partie.
        pVSp.configure(state=NORMAL)
        pVSb.configure(state=NORMAL)
        botRandom.configure(state=NORMAL)
        botSmart.configure(state=NORMAL)
        spinboxSize.configure(state=NORMAL)
        spinboxWinSize.configure(state=NORMAL)
        buttonColorX.configure(state=NORMAL)
        buttonColorO.configure(state=NORMAL)
        optionLanguage.configure(state=NORMAL)
    else:
        # On met à jour le texte de l'état de la partie en fonction de qui doit jouer.
        if selectOpponent.get() == 2:
            textState.bindtags((("textState." + ("{}.turn".format("player" if turn == 1 else "bot"))),) + textState.bindtags()[1:])
        else:
            textState.bindtags((("textState." + ("player{}.turn".format(str(int(1.5-0.5*turn))))),) + textState.bindtags()[1:])
    update_widget(textState)


def toggle_widget(widget: Widget, **kwargs):
    # On affiche ou on cache le widget en fonction de la valeur de selectOpponent.
    if selectOpponent.get() == 2:
        widget.pack(kwargs)
        textName.bindtags(("textName.bots",) + textName.bindtags()[1:])
    else:
        widget.pack_forget()
        textName.bindtags(("textName.players",) + textName.bindtags()[1:])
    update_widget(textName)


def change_color(symbol: int, color: str):
    global configColorX, configColorO
    # On change la couleur du bouton en fonction de la couleur choisie.
    if symbol == 1:
        configColorX = color
        buttonColorX.config(bg=color, fg="#{:02X}{:02X}{:02X}".format(255 - int(configColorX[1:3], 16), 255 - int(configColorX[3:5], 16), 255 - int(configColorX[5:7], 16)))
    else:
        configColorO = color
        buttonColorO.config(bg=color, fg="#{:02X}{:02X}{:02X}".format(255 - int(configColorO[1:3], 16), 255 - int(configColorO[3:5], 16), 255 - int(configColorO[5:7], 16)))


def translate(key, language):
    # On traduit le texte en fonction de la langue choisie.
    with open(f"lang/{language}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get(key, key)


def update_widget(widget):
    # Si le widget a pour tag "noTranslation", on ne met pas à jour son texte.
    if widget.bindtags()[0] != "noTranslation":
        # On met à jour le texte des widgets en fonction de la langue choisie.
        if "text" in widget.config():
            widget.config(text=translate(widget.bindtags()[0], configLanguage.get()))
        if isinstance(widget, Tk):
            widget.title(translate(widget.bindtags()[0], configLanguage.get()))
    # On met à jour les widgets enfants du widget.
    if widget.winfo_children():
        for child in widget.winfo_children():
            update_widget(child)


win.title("title")
win.config(bg="bisque")
win.bindtags(("title",) + win.bindtags())
win.resizable(width=False, height=False)
textState = Label(win, font=("Helvetica", 20), bg="bisque")
textState.bindtags(("textState.newGame",) + textState.bindtags())
textState.pack(side=TOP, pady=20)
board = Canvas(win, width=lengthBoard, height=lengthBoard, bg="snow2")
board.pack(side=LEFT, padx=20, pady=5)
drawBoard()
textName = Label(win, font=("Helvetica", 12), bg="bisque")
textName.bindtags(("textName.players",) + textName.bindtags())
textName.pack(side=TOP, pady=5)
textScore = Label(win, text="0-0", font=("Helvetica", 20), bg="bisque")
textScore.bindtags(("noTranslation",) + textScore.bindtags())
textScore.pack(side=TOP, pady=5)
buttonRules = Button(win, command=lambda: showinfo((translate("buttonRules.button", configLanguage.get())), translate("buttonRules.rules", configLanguage.get())))
buttonRules.bindtags(("buttonRules.button",) + buttonRules.bindtags())
buttonRules.pack(side=TOP, pady=5)
buttonNewGame = Button(win, command=newGame)
buttonNewGame.bindtags(("buttonNewGame",) + buttonNewGame.bindtags())
buttonNewGame.pack(side=TOP, pady=5)
buttonAbout = Button(win, command=lambda: showinfo((translate("buttonAbout.button", configLanguage.get()) + "\n\n"), translate("buttonAbout.about", configLanguage.get())))
buttonAbout.bindtags(("buttonAbout.button",) + buttonAbout.bindtags())
buttonAbout.pack(side=TOP, pady=5)
frameOpponent = Frame(win, borderwidth=2, relief=GROOVE)
frameOpponent.pack(side=TOP, padx=5, pady=5)
frameBot = Frame(frameOpponent, borderwidth=2, relief=GROOVE)
textOpponent = Label(frameOpponent, font=("Helvetica", 9, "underline"))
textOpponent.bindtags(("textOpponent",) + textOpponent.bindtags())
textOpponent.pack(side=TOP)
textSmartness = Label(frameBot, font=("Helvetica", 9, "underline"))
textSmartness.bindtags(("textSmartness",) + textSmartness.bindtags())
textSmartness.pack(side=TOP)
pVSp = Radiobutton(frameOpponent, variable=selectOpponent, value=1,
                   command=lambda f=frameBot: toggle_widget(f))
pVSp.bindtags(("pVSp",) + pVSp.bindtags())
pVSp.pack(side=TOP, pady=3)
pVSb = Radiobutton(frameOpponent, variable=selectOpponent, value=2,
                   command=lambda f=frameBot: toggle_widget(f))
pVSb.bindtags(("pVSb",) + pVSb.bindtags())
pVSb.pack(side=TOP, pady=3)
botRandom = Radiobutton(frameBot, variable=selectBot, value=1)
botRandom.bindtags(("botRandom",) + botRandom.bindtags())
botRandom.pack(side=TOP, padx=20, pady=3)
botSmart = Radiobutton(frameBot, variable=selectBot, value=2)
botSmart.bindtags(("botSmart",) + botSmart.bindtags())
botSmart.pack(side=TOP, padx=20, pady=3)
frameVariants = Frame(win, borderwidth=2, relief=GROOVE)
frameVariants.pack(side=TOP, padx=5, pady=5)
textVariants = Label(frameVariants, font=("Helvetica", 9, "underline"))
textVariants.bindtags(("textVariants",) + textVariants.bindtags())
textVariants.pack(side=TOP)
textSize = Label(frameVariants, font=("Helvetica", 9))
textSize.bindtags(("textSize",) + textSize.bindtags())
textSize.pack(side=TOP)
spinboxSize = Spinbox(frameVariants, from_=2, to=10, textvariable=configSize, wrap=True, command=lambda: spinboxWinSize.config(to=configSize.get()))
spinboxSize.pack(side=TOP, padx=5, pady=5)
textWinSize = Label(frameVariants, font=("Helvetica", 9))
textWinSize.bindtags(("textWinSize",) + textWinSize.bindtags())
textWinSize.pack(side=TOP)
spinboxWinSize = Spinbox(frameVariants, from_=2, to=configSize.get(), textvariable=configWinSize, wrap=True)
spinboxWinSize.pack(side=TOP, padx=5, pady=5)
frameConfig = Frame(win, borderwidth=2, relief=GROOVE)
frameConfig.pack(side=TOP, padx=5, pady=5)
textConfig = Label(frameConfig, font=("Helvetica", 9, "underline"))
textConfig.bindtags(("textConfig",) + textConfig.bindtags())
textConfig.pack(side=TOP)
buttonColorX = Button(frameConfig, command=lambda: change_color(1, askcolor(title=translate("buttonColorX", configLanguage.get()), color=configColorX)[1]), bg=configColorX, fg="#00FFFF")
buttonColorX.bindtags(("buttonColorX",) + buttonColorX.bindtags())
buttonColorX.pack(side=TOP, padx=5, pady=5)
buttonColorO = Button(frameConfig, command=lambda: change_color(-1, askcolor(title=translate("buttonColorO", configLanguage.get()), color=configColorO)[1]), bg=configColorO, fg="#FFFF00")
buttonColorO.bindtags(("buttonColorO",) + buttonColorO.bindtags())
buttonColorO.pack(side=TOP, padx=5, pady=5)
buttonResetScore = Button(frameConfig, command=lambda: textScore.config(text="0-0"))
buttonResetScore.bindtags(("buttonResetScore",) + buttonResetScore.bindtags())
buttonResetScore.pack(side=TOP, padx=5)
textLanguage = Label(frameConfig, font=("Helvetica", 9))
textLanguage.bindtags(("textLanguage",) + textLanguage.bindtags())
textLanguage.pack(side=TOP)
optionLanguage = ttk.OptionMenu(frameConfig, configLanguage, "fr", "fr", "en", command=lambda _: update_widget(win))
optionLanguage.pack(side=TOP, padx=5)
update_widget(win)
win.mainloop()