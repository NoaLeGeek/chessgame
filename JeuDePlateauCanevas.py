#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from tkinter import *
from tkinter.messagebox import showinfo

rows, columns = 3, 3
lengthBoard = 550
margin = 20
length = (lengthBoard - 2 * margin) / rows
boardData = None
turn = None
numberPlays = 0
gameOver = False
win = Tk()
selectOpponent = IntVar()
selectBot = IntVar()
selectOpponent.set(1)
selectBot.set(1)


def init():
    global boardData, numberPlays, turn, gameOver
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


def drawBoard():
    y = 0
    for i in range(rows + 1):
        board.create_line(margin, y + margin, lengthBoard - margin, y + margin, width=4, fill="black")
        y += length
    x = 0
    for i in range(columns + 1):
        board.create_line(x + margin, margin, x + margin, lengthBoard - margin, width=4, fill="black")
        x += length


def click(event):
    global numberPlays, turn, boardData
    if gameOver or (turn == -1 and selectOpponent.get() == 2):
        return
    x, y = int((event.x - margin) // length), int((event.y - margin) // length)
    if x < 0 or x > columns - 1 or y < 0 or y > rows - 1 or boardData[x][y] in [-1, 1]:
        return
    boardData[x][y] = 1
    numberPlays += 1
    if numberPlays % 2 == 1:
        drawCross(x, y)
    else:
        drawCircle(x, y)
    isGameOver()
    print(gameOver)
    print(numberPlays)
    print("=====")
    for i in range(3):
        print([ligne[i] for ligne in boardData])
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
    board.create_oval(x1, y1, x2, y2, width=5, outline="blue")


def drawCross(x: int, y: int):
    x1 = 2 * margin + x * length
    y1 = 2 * margin + y * length
    x2 = (x + 1) * length
    y2 = (y + 1) * length
    board.create_line(x1, y1, x2, y2, width=5, fill="red")
    board.create_line(x1, y2, x2, y1, width=5, fill="red")
    pass


def isGameOver():
    global gameOver, turn, boardData
    for player in [-1, 1]:
        for i in range(rows):
            if all(boardData[i][j] == player for j in range(columns)):
                drawLine(i, 0, i, 2)
                gameOver = True
            if all(boardData[j][i] == player for j in range(columns)):
                drawLine(0, i, 2, i)
                gameOver = True
        if all(boardData[i][i] == player for i in range(columns)):
            drawLine(0, 0, 2, 2)
            gameOver = True
        if all(boardData[i][columns - 1 - i] == player for i in range(columns)):
            drawLine(0, 2, 2, 0)
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
    x1_pixel = margin + x1 * length + length / 2
    y1_pixel = margin + y1 * length + length / 2
    x2_pixel = margin + x2 * length + length / 2
    y2_pixel = margin + y2 * length + length / 2
    board.create_line(x1_pixel, y1_pixel, x2_pixel, y2_pixel, width=5, fill=("darkblue" if numberPlays % 2 == 0 else "darkred"))


def computerPlays():
    print("machinejoue")
    global numberPlays, turn, gameOver, boardData
    x, y = None, None
    if selectBot.get() == 2:
        for i in range(rows):
            if sum([boardData[i][j] for j in range(columns)]) == -2:
                x, y = i, [j for j in range(columns) if boardData[i][j] == 0][0]
            if sum([boardData[j][i] for j in range(columns)]) == -2:
                x, y = [j for j in range(columns) if boardData[j][i] == 0][0], i
        print("en haut vers en bas:", sum([boardData[i][i] for i in range(columns)]))
        if sum([boardData[i][i] for i in range(columns)]) == -2:
            x, y = [(i, i) for i in range(columns) if boardData[i][i] == 0][0]
        print("en bas vers en haut", sum([boardData[i][columns - 1 - i] for i in range(columns)]))
        if sum([boardData[i][columns - 1 - i] for i in range(columns)]) == -2:
            x, y = [(i, columns - 1 - i) for i in range(columns) if boardData[i][columns - 1 - i] == 0][0]
        if x is None:
            for i in range(rows):
                if sum([boardData[i][j] for j in range(columns)]) == 2:
                    x, y = i, [j for j in range(columns) if boardData[i][j] == 0][0]
                if sum([boardData[j][i] for j in range(columns)]) == 2:
                    x, y = [j for j in range(columns) if boardData[j][i] == 0][0], i
            #TODO IA doesn't work in diagonals            print(sum([boardData[i][i] for i in range(columns)]))
            if sum([boardData[i][i] for i in range(columns)]) == 2:
                x, y = [(i, i) for i in range(columns) if boardData[i][i] == 0][0]
            if sum([boardData[i][columns - 1 - i] for i in range(columns)]) == 2:
                x, y = [(i, columns - 1 - i) for i in range(columns) if boardData[i][columns - 1 - i] == 0][0]
    if x is None:
        x, y = random.choice(list(filter(lambda pos: boardData[pos[0]][pos[1]] == 0, [(i, j) for i in range(rows) for j in range(columns)])))
    print("x, y choosed", (x,y))
    boardData[x][y] = -1
    numberPlays += 1
    if numberPlays % 2 == 1:
        drawCross(x, y)
    else:
        drawCircle(x, y)
    isGameOver()
    if not gameOver:
        turn *= -1
    updateState()
    print("=====")
    for i in range(3):
        print([ligne[i] for ligne in boardData])


def updateState():
    global turn, gameOver, numberPlays
    if gameOver:
        gameState = "Joueur O a gagné!" if turn == 1 else "Joueur X a gagné!" if turn == -1 else "Égalité!"
        textState.config(text=gameState)
        pVSp.configure(state=NORMAL)
        pVSb.configure(state=NORMAL)
        botRandom.configure(state=NORMAL)
        botSmart.configure(state=NORMAL)
    else:
        textState.config(text="Tour des {}".format("X" if numberPlays % 2 == 0 else "O"))


def toggle_widget(widget: Widget, **kwargs):
    if selectOpponent.get() == 2:
        widget.pack(kwargs)
    else:
        widget.pack_forget()


# Renvoie -1 si le nombre elt n'est pas trouvé dans tab
def recherche(elt: int, tab: list[int]) -> int:
    if len(tab) == 0:
        return -1
    for i in range(len(tab)):
        if tab[i] == elt:
            return i
    return -1


win.title("Jeu de Noa OTTERMANN")
win.config(bg="bisque")
win.resizable(width=False, height=False)
textState = Label(win, text="", font=("Helvetica", 20), bg="bisque")
textState.pack(side=TOP, pady=20)
board = Canvas(win, width=lengthBoard, height=lengthBoard, bg="snow2")
board.pack(side=LEFT, padx=20, pady=5)
drawBoard()
textScore = Label(win, text="0-0", font=("Helvetica", 20), bg="bisque")
textScore.pack(side=TOP, pady=5)
aboutButton = Button(win, text="À propos", command=lambda: showinfo("A propos\n\n",
                                                                    "*** Programme écrit par Noa OTTERMANN ***\n Gilles Sellig et Carole Elorac \n1ère NSI - Lycée Louis Armand - Mulhouse \n"))
aboutButton.pack(side=TOP, padx=20, pady=30)
rulesButton = Button(win, text="Règles du jeu",
                     command=lambda: showinfo("Règles du jeu\n\n", "Premièrement : \nDeuxièmement : \n"))
rulesButton.pack(side=TOP, padx=20, pady=30)
newGameButton = Button(win, text="Nouvelle partie", command=newGame)
newGameButton.pack(side=TOP, padx=20, pady=30)
opponentFrame = Frame(win, borderwidth=2, relief=GROOVE)
opponentFrame.pack(side=TOP, padx=5, pady=5)
botFrame = Frame(win, borderwidth=2, relief=GROOVE)
pVSp = Radiobutton(opponentFrame, text="Joueur contre joueur", variable=selectOpponent, value=1,
                   command=lambda f=botFrame: toggle_widget(f))
pVSp.pack(side=TOP, padx=5, pady=5)
pVSb = Radiobutton(opponentFrame, text="Joueur contre bot", variable=selectOpponent, value=2,
                   command=lambda f=botFrame: toggle_widget(f))
pVSb.pack(side=TOP, padx=5, pady=5)
botRandom = Radiobutton(botFrame, text="Aléatoire", variable=selectBot, value=1)
botRandom.pack(side=TOP, padx=5, pady=5)
botSmart = Radiobutton(botFrame, text="Intelligent", variable=selectBot, value=2)
botSmart.pack(side=TOP, padx=5, pady=5)
win.mainloop()
