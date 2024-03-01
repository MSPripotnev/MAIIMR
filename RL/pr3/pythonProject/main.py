import sys, pygame
import numpy as np
import math

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, s, x, y):
    surf=font.render(s, True, (0,0,0))
    screen.blit(surf, (x,y))


sz = (800, 600)

def rot(v, ang): #функция для поворота на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def limAng(ang):
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rotArr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]

def dist(p1, p2):
    return np.linalg.norm(np.subtract(p1, p2))

def drawRotRect(screen, color, pc, w, h, ang): #точка центра, ширина высота прямоуг и угол поворота прямогуольника
    pts = [
        [- w/2, - h/2],
        [+ w/2, - h/2],
        [+ w/2, + h/2],
        [- w/2, + h/2],
    ]
    pts = rotArr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

class Cell:
    def __init__(self, p0, w, h):
        self.p0, self.w, self.h=p0, w, h
        self.obj=""

class Table:
    def __init__(self, p0, w, h, nx, ny):
        self.p0, self.w, self.h, self.nx, self.ny=p0, w, h, nx, ny
        def pCell(ix,iy): return np.array(self.p0)+[ix*self.w, iy*self.h]
        self.cells=[ [ Cell(pCell(ix, iy), w, h) for ix in range(self.nx)] for iy in range(self.ny) ]
    def draw(self, screen, color=(0,0,0)):
        for iy in range(self.ny):
            for ix in range(self.nx):
                c=self.cells[iy][ix]
                p=np.add(c.p0, [self.w/2, self.h/2])
                drawRotRect(screen, color, p, self.w, self.h, 0)
                p2=np.add(c.p0, [self.w/2*0.8, self.h/2*0.8])
                drawText(screen, c.obj, *p2)
    def placeObj(self, xMouse, yMouse, obj="X"):
        dx, dy=xMouse-self.p0[0], yMouse-self.p0[1]
        ix=max(0,min(self.nx-1, dx//self.w))
        iy=max(0,min(self.ny-1, dy//self.h))
        c=self.cells[iy][ix]
        c.obj=obj

    def getState(self, targetObj):
        s=[[ 1 if self.cells[iy][ix].obj==targetObj else 0
             for ix in range(self.nx)] for iy in range(self.ny)]
        return s

    def getScore(self, state):
        t1=[[1,0,0],[0,1,0],[0,0,1]]
        t2=[[0,0,1],[0,1,0],[1,0,0]]
        t3=[[0,1,0],[0,1,0],[0,1,0]]
        t4=[[0,0,0],[1,1,1],[0,0,0]]
        t5=[[1,1,1],[0,0,0],[0,0,0]]
        t6=[[0,0,0],[0,0,0],[1,1,1]]
        t7=[[1,0,0],[1,0,0],[1,0,0]]
        t8=[[0,0,1],[0,0,1],[0,0,1]]
        T=[t1, t2, t3, t4, t5, t6, t7, t8]
        score = 0
        for t in T:
            t_=np.ndarray.flatten(np.array(t))
            s_=np.ndarray.flatten(np.array(state))
            m=np.dot(t_,s_)
            v=np.sum(m)
            if v>score: score=v
        return score

    def getBestAction(self, stateX, state0, obj="X"): # state - это таблица 3*3, по которой можно определить выигрыш 1го игрока
        actions=[]
        for iy in range(self.ny):
            for ix in range(self.nx):
                if stateX[iy][ix]==0 and state0[iy][ix]==0:
                    actions.append([ix, iy])
        scores = []
        for a in actions:
            stateNew=np.array(stateX if obj=="X" else state0)
            stateNew[a[1]][a[0]]=1
            score=self.getScore(stateNew)
            scores.append(score)
        i = np.argmax(scores)
        return actions[i]

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    tbl = None
    def init():
        nonlocal tbl
        tbl = Table([100, 100], 50, 50, 3, 3)

    init()

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    init()
                if ev.key == pygame.K_a:
                    s1 = tbl.getState("X")
                    s2 = tbl.getState("0")
                    a=tbl.getBestAction(s1, s2)
                    tbl.cells[a[1]][a[0]].obj="0"
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1: #LEFT BUTTON
                    tbl.placeObj(*ev.pos, "X")
                if ev.button == 3: #RIGHT BUTTON
                    tbl.placeObj(*ev.pos, "0")
                print(*ev.pos)

        screen.fill((255, 255, 255))

        tbl.draw(screen)

        s=tbl.getState("X")
        score=tbl.getScore(s)
        s2=tbl.getState("0")
        score2=tbl.getScore(s2)

        drawText(screen, f"Score X = {score}, Score 0 = {score2}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()