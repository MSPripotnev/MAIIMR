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
    def placeObj(self, xMouse, yMouse):
        dx, dy=xMouse-self.p0[0], yMouse-self.p0[1]
        ix=max(0,min(self.nx-1, dx//self.w))
        iy=max(0,min(self.ny-1, dy//self.h))
        c=self.cells[iy][ix]
        c.obj="X"

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    tbl = Table([100, 100], 50, 50, 3, 3)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1: #LEFT BUTTON
                    tbl.placeObj(*ev.pos)
                    print(*ev.pos)

        dt=1/fps

        screen.fill((255, 255, 255))

        tbl.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()