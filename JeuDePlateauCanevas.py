#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.colorchooser import askcolor

rows, columns = 3, 3
lengthBoard = 550
margin = 20
length = (lengthBoard - 2 * margin) / 3
boardData = None
turn = None
numberPlays = 0
gameOver = False
win = Tk()
selectOpponent = IntVar()
selectBot = IntVar()
configSize = IntVar()
configWinSize = IntVar()
configColorX = "#FF0000"
configColorO = "#0000FF"
selectOpponent.set(1)
selectBot.set(1)
configSize.set(3)
configWinSize.set(3)


def init():
    global boardData, numberPlays, turn, gameOver, rows, columns, length
    rows, columns = configSize.get(), configSize.get()
    length = (lengthBoard - 2 * margin) / rows
    board.delete("all")
    boardData = [[0] * columns for _ in range(rows)]
    turn = random.choice([1, -1])
    numberPlays = 0
    gameOver = False
    drawBoard()


def newGame():
    init()
    updateState()
    if turn == -1 and selectOpponent.get() == 2:
        computerPlays()
    board.bind("<Button-1>", click)
    pVSp.configure(state=DISABLED)
    pVSb.configure(state=DISABLED)
    botRandom.configure(state=DISABLED)
    botSmart.configure(state=DISABLED)
    spinboxSize.configure(state=DISABLED)
    spinboxWinSize.configure(state=DISABLED)
    buttonColorX.configure(state=DISABLED)
    buttonColorO.configure(state=DISABLED)


def drawBoard():
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
    x, y = int((event.x - margin) // length), int((event.y - margin) // length)
    if x < 0 or x > columns - 1 or y < 0 or y > rows - 1 or boardData[x][y] in [-1, 1]:
        return
    boardData[x][y] = turn
    numberPlays += 1
    if numberPlays % 2 == 1:
        drawCross(x, y)
    else:
        drawCircle(x, y)
    isGameOver()
    if not gameOver:
        turn *= -1
        if selectOpponent.get() == 2:
            computerPlays()
    updateState()


def drawCircle(x: int, y: int):
    x1 = 2 * margin + x * length
    y1 = 2 * margin + y * length
    x2 = (x + 1) * length
    y2 = (y + 1) * length
    board.create_oval(x1, y1, x2, y2, width=5, outline=configColorO)


def drawCross(x: int, y: int):
    x1 = 2 * margin + x * length
    y1 = 2 * margin + y * length
    x2 = (x + 1) * length
    y2 = (y + 1) * length
    board.create_line(x1, y1, x2, y2, width=5, fill=configColorX)
    board.create_line(x1, y2, x2, y1, width=5, fill=configColorX)
    pass


def isGameOver():
    global gameOver, turn, boardData
    for player in [-1, 1]:
        for i in range(rows):
            for j in range(columns - configWinSize.get() + 1):
                if all(boardData[i][j + k] == player for k in range(configWinSize.get())):
                    drawLine(i, j, i, j + configWinSize.get() - 1)
                    gameOver = True
                if all(boardData[j + k][i] == player for k in range(configWinSize.get())):
                    drawLine(j, i, j + configWinSize.get() - 1, i)
                    gameOver = True
        for i in range(rows - configWinSize.get() + 1):
            for j in range(columns - configWinSize.get() + 1):
                if all(boardData[i + k][j + k] == player for k in range(configWinSize.get())):
                    drawLine(i, j, i + configWinSize.get() - 1, j + configWinSize.get() - 1)
                    gameOver = True
                if all(boardData[i + k][j + configWinSize.get() - 1 - k] == player for k in range(configWinSize.get())):
                    drawLine(i, j + configWinSize.get() - 1, i + configWinSize.get() - 1, j)
                    gameOver = True
    if not gameOver and numberPlays > rows * columns - 1:
        turn = 0
        gameOver = True
    if gameOver:
        board.unbind("<Button-1>")
        score = list(map(int, textScore.cget("text").split("-")))
        textScore.config(
            text="{}-{}".format(score[0] + 1 if turn == 1 else score[0], score[1] + 1 if turn == -1 else score[1]))


def drawLine(x1, y1, x2, y2):
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
                    if sum(boardData[i][j + k] for k in range(configWinSize.get())) == player * (configWinSize.get() - 1):
                        x, y = next((i, j + k) for k in range(configWinSize.get()) if boardData[i][j + k] == 0)
                        break
                    if sum(boardData[j + k][i] for k in range(configWinSize.get())) == player * (configWinSize.get() - 1):
                        x, y = next((j + k, i) for k in range(configWinSize.get()) if boardData[j + k][i] == 0)
                        break
                # Si x est défini, cela signifie que le bot a trouvé un coup gagnant ou un coup qui bloque le joueur.
                # Il est important de sortir de la boucle afin de ne pas écraser un possible coup gagnant trouvé par un possible coup trouvé qui bloque le joueur.
                if x is not None:
                    break
                for i in range(rows - configWinSize.get() + 1):
                    if sum(boardData[i + k][j + k] for k in range(configWinSize.get())) == player * (configWinSize.get() - 1):
                        x, y = next((i + k, j + k) for k in range(configWinSize.get()) if boardData[i + k][j + k] == 0)
                        break
                    if sum(boardData[i + k][j + configWinSize.get() - 1 - k] for k in range(configWinSize.get())) == player * (configWinSize.get() - 1):
                        x, y = next((i + k, j + configWinSize.get() - 1 - k) for k in range(configWinSize.get()) if boardData[i + k][j + configWinSize.get() - 1 - k] == 0)
                        break
            if x is not None:
                break
    if x is None:
        x, y = random.choice(list(filter(lambda pos: boardData[pos[0]][pos[1]] == 0, [(i, j) for i in range(rows) for j in range(columns)])))
    boardData[x][y] = turn
    numberPlays += 1
    if numberPlays % 2 == 1:
        drawCross(x, y)
    else:
        drawCircle(x, y)
    isGameOver()
    if not gameOver:
        turn *= -1
    updateState()


def updateState():
    global turn, gameOver, numberPlays
    if gameOver:
        if selectOpponent.get() == 2:
            textState.config(text="Joueur a gagné !" if turn == 1 else "Ordinateur a gagné !" if turn == -1 else "Égalité !")
        else:
            textState.config(text="Joueur 1 a gagné !" if turn == 1 else "Joueur 2 a gagné !" if turn == -1 else "Égalité !")
        pVSp.configure(state=NORMAL)
        pVSb.configure(state=NORMAL)
        botRandom.configure(state=NORMAL)
        botSmart.configure(state=NORMAL)
        spinboxSize.configure(state=NORMAL)
        spinboxWinSize.configure(state=NORMAL)
        buttonColorX.configure(state=NORMAL)
        buttonColorO.configure(state=NORMAL)
    else:
        if selectOpponent.get() == 2:
            textState.config(text="Tour du {}".format("Joueur" if turn == 1 else "Ordinateur"))
        else:
            textState.config(text="Tour du {}".format("Joueur 1" if turn == 1 else "Joueur 2"))


def toggle_widget(widget: Widget, **kwargs):
    if selectOpponent.get() == 2:
        widget.pack(kwargs)
        textName.config(text="Joueur - Ordinateur")
    else:
        widget.pack_forget()
        textName.config(text="Joueur 1 - Joueur 2")


def change_color(symbol: int, color: str):
    global configColorX, configColorO
    if symbol == 1:
        configColorX = color
        buttonColorX.config(bg=color, fg="#{:02X}{:02X}{:02X}".format(255 - int(configColorX[1:3], 16), 255 - int(configColorX[3:5], 16), 255 - int(configColorX[5:7], 16)))
    else:
        configColorO = color
        buttonColorO.config(bg=color, fg="#{:02X}{:02X}{:02X}".format(255 - int(configColorO[1:3], 16), 255 - int(configColorO[3:5], 16), 255 - int(configColorO[5:7], 16)))


win.title("Jeu de Noa OTTERMANN")
win.config(bg="bisque")
win.resizable(width=False, height=False)
textState = Label(win, text="Appuyez sur Nouvelle partie pour commencer une partie", font=("Helvetica", 20), bg="bisque")
textState.pack(side=TOP, pady=20)
board = Canvas(win, width=lengthBoard, height=lengthBoard, bg="snow2")
board.pack(side=LEFT, padx=20, pady=5)
drawBoard()
textName = Label(win, text="Joueur 1 - Joueur 2", font=("Helvetica", 12), bg="bisque")
textName.pack(side=TOP, pady=5)
textScore = Label(win, text="0-0", font=("Helvetica", 20), bg="bisque")
textScore.pack(side=TOP, pady=5)
buttonRules = Button(win, text="Règles du jeu",
                     command=lambda: showinfo("Règles du jeu\n\n", "- Le premier joueur à aligner 3 symboles identiques gagne la partie.\n- Il y a égalité lorsque la grille est complétée sans vainqueur.\n- Le premier joueur commence toujours avec le symbole X.\n\nVariantes :\n- La taille de l'alignement peut être modifiée entre 2 et la taille de la grille.\n- La taille de la grille peut être modifiée entre 2 et 10.\n- Si la taille de l'alignement a été modifiée, alors le premier joueur à aligner la taille de l'alignement choisie gagne la partie.\n"))
buttonRules.pack(side=TOP, pady=5)
buttonNewGame = Button(win, text="Nouvelle partie", command=newGame)
buttonNewGame.pack(side=TOP, pady=5)
buttonAbout = Button(win, text="À propos", command=lambda: showinfo("A propos\n\n",
                                                                    "Programme écrit par Noa OTTERMANN\n1ère NSI - Lycée Louis Armand - Mulhouse \n"))
buttonAbout.pack(side=TOP, pady=5)
frameOpponent = Frame(win, borderwidth=2, relief=GROOVE)
frameOpponent.pack(side=TOP, padx=5, pady=5)
frameBot = Frame(frameOpponent, borderwidth=2, relief=GROOVE)
textOpponent = Label(frameOpponent, text="Adversaire", font=("Helvetica", 9, "underline"))
textOpponent.pack(side=TOP)
textSmartness = Label(frameBot, text="Intelligence du bot", font=("Helvetica", 9, "underline"))
textSmartness.pack(side=TOP)
pVSp = Radiobutton(frameOpponent, text="Joueur contre joueur", variable=selectOpponent, value=1,
                   command=lambda f=frameBot: toggle_widget(f))
pVSp.pack(side=TOP, pady=3)
pVSb = Radiobutton(frameOpponent, text="Joueur contre bot", variable=selectOpponent, value=2,
                   command=lambda f=frameBot: toggle_widget(f))
pVSb.pack(side=TOP, pady=3)
botRandom = Radiobutton(frameBot, text="Aléatoire", variable=selectBot, value=1)
botRandom.pack(side=TOP, padx=20, pady=3)
botSmart = Radiobutton(frameBot, text="Intelligent", variable=selectBot, value=2)
botSmart.pack(side=TOP, padx=20, pady=3)
frameVariants = Frame(win, borderwidth=2, relief=GROOVE)
frameVariants.pack(side=TOP, padx=5, pady=5)
textVariants = Label(frameVariants, text="Variantes", font=("Helvetica", 9, "underline"))
textVariants.pack(side=TOP)
textSize = Label(frameVariants, text="Taille de la grille", font=("Helvetica", 9))
textSize.pack(side=TOP)
spinboxSize = Spinbox(frameVariants, from_=2, to=10, textvariable=configSize, wrap=True, command=lambda: spinboxWinSize.config(to=configSize.get()))
spinboxSize.pack(side=TOP, padx=5, pady=5)
textWinSize = Label(frameVariants, text="Taille de l'alignement", font=("Helvetica", 9))
textWinSize.pack(side=TOP)
spinboxWinSize = Spinbox(frameVariants, from_=2, to=configSize.get(), textvariable=configWinSize, wrap=True)
spinboxWinSize.pack(side=TOP, padx=5, pady=5)
frameConfig = Frame(win, borderwidth=2, relief=GROOVE)
frameConfig.pack(side=TOP, padx=5, pady=5)
textConfig = Label(frameConfig, text="Paramètres", font=("Helvetica", 9, "underline"))
textConfig.pack(side=TOP)
buttonColorX = Button(frameConfig, text="Couleur des X", command=lambda: change_color(1, askcolor(title="Couleur des X", color=configColorX)[1]), bg=configColorX, fg="#00FFFF")
buttonColorX.pack(side=TOP, padx=5, pady=5)
buttonColorO = Button(frameConfig, text="Couleur des O", command=lambda: change_color(-1, askcolor(title="Couleur des O", color=configColorO)[1]), bg=configColorO, fg="#FFFF00")
buttonColorO.pack(side=TOP, padx=5, pady=5)
win.mainloop()