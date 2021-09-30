import cv2
from time import sleep
import os, copy

import HandTrackingModule as htm
import time
import random
import numpy as np


n = 6
z = (n - 2) // 2
dirx = [-1, 0, 1, -1, 1, -1, 0, 1]
diry = [-1, -1, -1, 0, 0, 1, 1, 1]
depth = 4
board = [['0' for y in range(n)] for x in range(n)]


board[z][z] = '2'
board[n - 1 - z][z] = '1'        
board[z][n - 1 - z] = '1'
board[n - 1 - z][n - 1 - z] = '2'
def PrintBoard():
    m = len(str(n - 1))
    for x in range(n):
        row = ''
        for y in range(n):
            row += board[x][y]
            row += ' ' * m
        print(row + ' ' + str(x))
    #print
    row = ''
    for y in range(n):
        row += str(y).zfill(m) + ' '
    print(row + '\n')
PrintBoard()


def MakeMove(board, x, y, player): # assuming valid move
    taken = 0 # total number of opponent pieces taken
    board[x][y] = player
    
    for d in range(8): # 8 directions
        ctr = 0
        for i in range(n):
            dx = x + dirx[d] * (i + 1)
            dy = y + diry[d] * (i + 1)
            if dx < 0 or dx > n - 1 or dy < 0 or dy > n - 1:
                ctr = 0; break
            elif board[dx][dy] == player:
                break
            elif board[dx][dy] == '0':
                ctr = 0; break
            else:
                ctr += 1
        for i in range(ctr):
            dx = x + dirx[d] * (i + 1)
            dy = y + diry[d] * (i + 1)
            board[dx][dy] = player
        taken += ctr
    return (board, taken)



def ValidMove(board, x, y, player):
    #print(x, y)
    if x < 0 or x > n - 1 or y < 0 or y > n - 1:
        return False
    if board[x][y] != '0':
        return False
    (boardTemp, taken) = MakeMove(copy.deepcopy(board), x, y, player)
    if taken == 0:
        return False
    return True

minEvalBoard = -1 # min - 1
maxEvalBoard = n * n + 4 * n + 4 + 1 # max + 1

def EvalBoard(board, player):
    tot = 0
    for x in range(n):
        for y in range(n):
            if board[x][y] == player:
                if (x == 0 or x == n - 1) and (y == 0 or y == n - 1):
                    tot += 4 # corner(more points)
                elif (x == 0 or x == n - 1) or (y == 0 or y == n - 1):
                    tot += 2 # side
                else:
                    tot += 1
    return tot


def IsTerminalNode(board, player):
    for x in range(n):
        for y in range(n):
            if ValidMove(board, x, y, player):
                return False
    return True


def GetSortedNodes(board, player):
    sortedNodes = []
    for x in range(n):
        for y in range(n):
            if ValidMove(board, x, y, player):
                (boardTemp, taken) = MakeMove(copy.deepcopy(board), x, y, player)
                sortedNodes.append((boardTemp, EvalBoard(boardTemp, player)))
    sortedNodes = sorted(sortedNodes, key = lambda node: node[1], reverse = True)
    sortedNodes = [node[0] for node in sortedNodes]
    return sortedNodes

def Minimax(board, player, depth, maximizingPlayer):
    if depth == 0 or IsTerminalNode(board, player):
        return EvalBoard(board, player)
    if maximizingPlayer:
        bestValue = minEvalBoard
        for x in range(n):
            for y in range(n):
                if ValidMove(board, x, y, player):
                    (boardTemp, taken) = MakeMove(copy.deepcopy(board), x, y, player)
                    v = Minimax(boardTemp, player, depth - 1, False)
                    bestValue = max(bestValue, v)
    else: 
        bestValue = maxEvalBoard
        for x in range(n):
            for y in range(n):
                if ValidMove(board, x, y, player):
                    (boardTemp, taken) = MakeMove(copy.deepcopy(board), x, y, player)
                    v = Minimax(boardTemp, player, depth - 1, True)
                    bestValue = min(bestValue, v)
    return bestValue


def BestMove(board, player):
    maxPoints = 0
    mx = -1; my = -1
    for x in range(n):
        for y in range(n):
            if ValidMove(board, x, y, player):
                (boardTemp, taken) = MakeMove(copy.deepcopy(board), x, y, player)
                points = Minimax(boardTemp, player, depth, True)
                if points > maxPoints:
                    maxPoints = points
                    mx = x
                    my = y
    return (mx, my)





def draw_text(frame, text, x, y, color=(255,0,255), thickness=4, size=3):
    if x is not None and y is not None:
        cv2.putText(frame, text, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness)


def drawAll(img, buttonList = [], button1=None):
    for circle,button in zip(circleList, buttonList):
        x, y = button.pos
        w, h = button.size
        center_coordinates = circle.coor
        cv2.rectangle(img, button.pos, (x + w, y + h), (8, 102, 5), cv2.FILLED)
        if (int(button.column) == z and int(button.row) == z) or (int(button.column) == n - 1 - z and int(button.row) == n - 1 - z):
            cv2.circle(img, center_coordinates, 100, (0,0,0), -1)
        elif (int(button.column) == z and int(button.row) == n - 1 - z) or (int(button.column) == n - 1 - z and int(button.row) == z):
            cv2.circle(img, center_coordinates, 100, (255,255,255), -1)
        else:
            cv2.circle(img, center_coordinates, 100, (255,255,0), -1)
    if button1:
        button2 = button1
        x1, y1 = button2.pos
        w1, h1 = button2.size
        cv2.rectangle(img, button2.pos, (x1 + w1, y1 + h1), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, button2.text, (x1 + 50, y1 + 70),cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 128), 4)
    return img

class Button():
    def __init__(self, pos, row,column,text,size=[230, 230]):
        self.pos = pos
        self.size = size
        self.row = row
        self.column = column
        self.text = text
class DoneButton():
    def __init__(self, pos, text, size=[230, 230]):
        self.pos = pos
        self.size = size
        self.text = text

class Circle():
    def __init__(self, coor, text):
        self.coor = coor
        self.text = text


buttonList = []

num=1
for i in range(6):
    for j in range(6):
        if (i == 0 and j == 0):
            buttonList.append(Button([300 * j + 400, 50 * i + 50], str(i), str(j), str(num)))
        elif j>=0 and i != 0:
            buttonList.append(Button([300 * j + 400, 250 * i + 50], str(i), str(j), str(num)))
        else:
            buttonList.append(Button([300 * j + 400, 250 * i + 50], str(i), str(j), str(num)))
        num += 1
doneButton = DoneButton([2500, 900], "Done", size = [400, 100])

circleList = []       
for _,button in enumerate(buttonList):
    x, y = button.pos
    w, h = button.size
    center_coordinates = (x+w//2, y+h//2)
    circleList.append(Circle(center_coordinates, button.text))



cap = cv2.VideoCapture(0)


show = False
detector = htm.handDetector(detectionCon=0.8)

flag1 = False
circles1 = []
circles2 = []
done = False
flag2 = False


gameOver = False
win = -1
timer = 5
tip = True
while True:
    success, img = cap.read()
    
    img = cv2.resize(img,(3000,1900),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)


    
    img = cv2.flip(img, 1)
    
    _, img = detector.findHands(img)
    center_x = int(img.shape[0]/2)
    center_y = int(img.shape[0]/2)
    lmList, bboxInfo = detector.findPosition(img)
    img = drawAll(img, buttonList, doneButton)
    if lmList:
        if done == False:
            for button in buttonList:
                x1, y1 = button.pos
                w, h = button.size

                if x1 < lmList[8][1] < x1 + w and y1 < lmList[8][2] < y1 + h: 

                    cv2.rectangle(img, (x1 - 5, y1 - 5), (x1 + w + 5, y1 + h + 5), (250, 206, 135), cv2.FILLED)
                    l, _, _ = detector.findDistance(8, 12, img)

                    if l < 100:
                        #cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        
                        x = int(button.row)
                        y = int(button.column)
                        
                        if IsTerminalNode(board, '1'):
                            cv2.rectangle(img, button.pos, (x1 + w, y1 + h), (0, 255, 0), cv2.FILLED)
                            
                            print('Score of player: ' + str(EvalBoard(board, '1')))
                            print('Score of AI  : ' + str(EvalBoard(board, '2')))
                            gameOver = True
                            tip = False
                        if ValidMove(board, x, y, '1'):
                            cv2.rectangle(img, button.pos, (x1 + w, y1 + h), (0, 255, 0), cv2.FILLED)
                            (board, taken) = MakeMove(board, x, y, '1')
                            print('No of pieces taken: ' + str(taken))
                            sleep(0.15)
                            break
                        else:
                            cv2.rectangle(img, button.pos, (x1 + w, y1 + h), (0, 0, 255), cv2.FILLED)
                            print('Invalid move! Try again!')


            x1, y1 = doneButton.pos
            w1, h1 = doneButton.size
            if x1 < lmList[8][1] < x1 + w1 and y1 < lmList[8][2] < y1 + h1:

                cv2.rectangle(img, (x1 - 5, y1 - 5), (x1 + w1 + 5, y1 + h1 + 5), (193, 182, 255), cv2.FILLED)
                l, _, _ = detector.findDistance(8, 12, img)
                
                
                if l < 100:
                    cv2.rectangle(img, doneButton.pos, (x1 + w1, y1 + h1), (0, 255, 0), cv2.FILLED)
                    done = True


        if done == True:
            PrintBoard()
            (x3, y3) = BestMove(board, '2')
            if IsTerminalNode(board, '2'):
                tip = False
                print('Score of player: ' + str(EvalBoard(board, '1')))
                print('Score of AI  : ' + str(EvalBoard(board, '2')))
                gameOver = True
            if not (x3 == -1 and y3 == -1):
                
                (board, taken) = MakeMove(board, x3, y3, '2')
                print('AI played (x y): ' + str(x3) + ' ' + str(y3))
                print('No of pieces taken: ' + str(taken))

            done = False




    for button in buttonList:
        for rows in range(n):
            for columns in range(n):
                if board[rows][columns] == '1' and rows == int(button.row) and columns == int(button.column):
                    x, y = button.pos
                    w, h = button.size
                    center_coordinates = (x+w//2, y+h//2)
                    cv2.circle(img, center_coordinates, 100, (0,0,0), -1)
                if board[rows][columns] == '2' and rows == int(button.row) and columns == int(button.column):
                    x, y = button.pos
                    w, h = button.size
                    center_coordinates = (x+w//2, y+h//2)
                    cv2.circle(img, center_coordinates, 100, (255,255,255), -1)

                        
    if gameOver:
        
        if EvalBoard(board, '1') > EvalBoard(board, '2'):
            draw_text(img, "You WIN!!", center_x+1300, center_y-600,color = (0,255,255), thickness = 12, size = 4)
            draw_text(img, str(EvalBoard(board, '1')) , center_x+1300, center_y-500,color = (0,255,255), thickness = 12, size = 4)
        elif EvalBoard(board, '1') < EvalBoard(board, '2'):
            draw_text(img, "AI WINS!!", center_x+1300, center_y-600,color = (0,255,255), thickness = 12, size= 3)
            draw_text(img, str(EvalBoard(board, '2')) , center_x+1300, center_y-500,color = (0,255,255), thickness = 12, size = 4)
        else:
            draw_text(img, "DRAW", center_x+1300, center_y-600,color = (0,255,255), thickness = 12, size= 3)
            draw_text(img, "Your score: "+str(EvalBoard(board, '1')) , center_x+1300, center_y-500,color = (0,255,255), thickness = 12, size = 4)
            draw_text(img, "AI's score: "+str(EvalBoard(board, '2')) , center_x+1300, center_y-500,color = (0,255,255), thickness = 12, size = 4)

    if tip:
        draw_text(img, "Red Blink means", center_x+1400, center_y-800,color = (0, 255, 200), thickness = 10, size = 2)
        draw_text(img, "invalid move", center_x+1400, center_y-700,color = (0, 255, 200), thickness = 10, size = 2)
        draw_text(img, "Your score: "+str(EvalBoard(board, '1')), center_x+1400, center_y-600,color = (0, 255, 180), thickness = 10, size = 2)
        draw_text(img, "AI's score: "+str(EvalBoard(board, '2')), center_x+1400, center_y-500,color = (0, 255, 180), thickness = 10, size = 2)

    cv2.imshow("Image", img)
    
    if (cv2.waitKey(1) & 0xFF == ord('q')):
        break
    
cap.release()
cv2.destroyAllWindows()

