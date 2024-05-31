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


class Robot:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.vx=0
        self.vy=0
        self.sz=15
    def getPos(self):
        return [self.x, self.y]
    def draw(self, screen):
        pygame.draw.circle(screen, (0,0,0), self.getPos(), self.sz, 2)
    def sim(self, dt):
        self.x+=self.vx*dt
        self.y+=self.vy*dt


def drawLinks(screen, robots):
    for r in robots:
        robots_=[r2 for r2 in robots if r2!=r]
        dd=[dist(r.getPos(), r2.getPos()) for r2 in robots_]
        i = np.argmin(dd)
        r2=robots_[i]
        pygame.draw.line(screen, (255, 0, 0), r.getPos(), r2.getPos(),2)

#матрица связности, разрыв связи
def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    robots=[Robot(300,100), Robot(400,200), Robot(350,250) ]
    for r in robots:
        r.vx=np.random.normal(0,20)
        r.vy=np.random.normal(0,20)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        dt=1/fps
        for r in robots:
            r.sim(dt)
        screen.fill((255, 255, 255))
        for r in robots:
            r.draw(screen)

        drawLinks(screen, robots)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()