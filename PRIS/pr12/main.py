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

class Box:
    def __init__(self, pos, w, h):
        self.pos=pos
        self.w=w
        self.h=h
    def draw(self, screen):
        pygame.draw.rect(screen, (0,0,0), [*self.pos, self.w, self.h], 2)

class Obj:
    def __init__(self, pos, w, h):
        self.pos=pos
        self.w=w
        self.h=h
    def draw(self, screen, color=(0,0,0)):
        pygame.draw.rect(screen, color, [*self.pos, self.w, self.h], 2)

def calcIntersectionArea(r1, r2):
    dx,dy=0,0
    if r1.pos[0] <= r2.pos[0] <= r1.pos[0]+r1.w:
        dx=r1.pos[0]+r1.w-r2.pos[0]
    elif r2.pos[0] <= r1.pos[0] <= r2.pos[0]+r2.w:
        dx=r2.pos[0]+r2.w-r1.pos[0]
    if r1.pos[1] <= r2.pos[1] <= r1.pos[1]+r1.h:
        dy=r1.pos[1]+r1.h-r2.pos[1]
    elif r2.pos[1] <= r1.pos[1] <= r2.pos[1]+r2.h:
        dy=r2.pos[1]+r2.h-r1.pos[1]
    dx=min(dx, min(r1.w, r2.w))
    dy=min(dy, min(r1.h, r2.h))
    return dx*dy

def calcCollisions(obj, objs):
    s=0
    for o in objs:
        if o!=obj:
            s+=calcIntersectionArea(o, obj)
    return s
def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    box = Box([100,100], 250, 250)

    objs=[
        Obj([500,50], 150, 100),
        Obj([500,200], 110, 70),
        Obj([500,350], 160, 80),
        Obj([500,500], 90, 70) ]

    ind=0

    while True:
        o=objs[ind]
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_x:
                    ind+=1
                    ind%=len(objs)
                if ev.key == pygame.K_z:
                    ind-=1
                    ind%=len(objs)
                if ev.key == pygame.K_w:
                    o.pos[1]-=10
                if ev.key == pygame.K_s:
                    o.pos[1]+=10
                if ev.key == pygame.K_a:
                    o.pos[0]-=10
                if ev.key == pygame.K_d:
                    o.pos[0]+=10

        dt=1/fps

        screen.fill((255, 255, 255))
        box.draw(screen)
        for i in range(len(objs)):
            color=(255,0,0) if i==ind else (0,0,255)
            objs[i].draw(screen, color)

        s=sum(calcIntersectionArea(box, o) for o in objs)
        s2=sum(calcCollisions(o, objs) for o in objs)/2

        drawText(screen, f"S = {s}", 5, 5)
        drawText(screen, f"S2 = {s2}", 5, 25)

        pygame.display.flip()
        timer.tick(fps)

main()