import sys, pygame
from pygame.locals import *
import math

pygame.font.init()
font = pygame.font.SysFont("Comic Sans MS", 20)
def drawText(screen, str, x,y):
    surf = font.render(str,False, (0,0,0))
    screen.blit(surf,(x,y))

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.V = 0
        self.w = 50
        self.h = 50
        self.neighbours = []
        self.isGoal = False
        self.isObst = False

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255), ((self.x + self.w / 2), (self.y + self.h / 2), self.w, self.h),
                         0 if self.isObst else 2)
        if self.isGoal: pygame.draw.circle(screen, (0,0,0), (self.x, self.y), 3, 2)
        drawText(screen, str(round(self.V)), (self.x + self.w / 2), (self.y + self.h / 2))
        #for c in self.neighbours:
        #    pygame.draw.line(screen, (255,0,0), ((self.x + self.w), (self.y + self.h)),
        #                     ((c.x + c.w), (c.y + c.h)))

class Table:
    def __init__(self, nx, ny, w, h):
        self.nx = nx
        self.ny = ny
        res = []
        for iy in range(ny):
            row = []
            for ix in range(nx):
                row.append(Cell(ix * w, iy * h))
            res.append(row)
        self.cells = res

    def draw(self, screen):
        for r in self.cells:
            for c in r:
                c.draw(screen)

    def connect(self):
        for iy in range(self.ny):
            for ix in range(self.nx):
                c = self.cells[iy][ix]
                for jy in range(max(0, iy-1), min(self.ny, iy+2)):
                    for jx in range(max(0, ix-1), min(self.nx, ix+2)):
                        c2 = self.cells[jy][jx]
                        c.V = 100 if c.isGoal else -100 if c.isObst else 0
                        c.neighbours.append(c2)

    def valueIteration(self, m = 0.3):
        for iy in range(self.ny):
            for ix in range(self.nx):
                c = self.cells[iy][ix]
                if c.isGoal or c.isObst: continue
                #for c2 in c.neighbours:
                    # c.V = (1-m)*c.V + m * c2.V ### эта формула основа данной науки, остальное - всего лишь практика
                vv = [c2.V for c2 in c.neighbours]
                v_max = max(vv)
                c.V = (1-m)*c.V + m * v_max

def main():
    sz=(800, 600)
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    r = 10; x = 130; y = 130;
    fps = 30
    table = Table(5,5,50,50)
    table.cells[1][1].isObst = table.cells[1][3].isObst = table.cells[3][3].isObst = True
    table.cells[2][4].isGoal = True
    table.connect()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v: table.valueIteration()

        screen.fill( (255,255,255) )
        x += 1
        y += 1
        table.draw(screen)

        pygame.display.flip()
        timer.tick(fps)

main()