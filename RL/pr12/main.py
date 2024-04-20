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

class Obj:
    def __init__(self, x, y, w, h):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.vx=0
        self.vy=0
        self.isAgent=False
    def getBB(self):
        return [self.x, self.y, self.w, self.h]
    def draw(self, screen):
        pygame.draw.rect(screen, (255,0,0) if self.isAgent else (0,0,255), self.getBB(), 2)
    def sim(self, dt, room):
        self.x+=self.vx*dt
        self.y+=self.vy*dt
        if self.x<room.x or self.x+self.w>room.x + room.w:
            self.vx*=-1
        if self.y<room.y or self.y+self.h>room.y + room.h:
            self.vy*=-1

class Room:
    def __init__(self, x, y, w, h):
        self.x=x
        self.y=y
        self.w=w
        self.h=h

    def getBB(self):
        return [self.x, self.y, self.w, self.h]
    def draw(self, screen):
        pygame.draw.rect(screen, (0,0,0), self.getBB(), 3)

#Пример игры:
#https://avenerussia.ru/1/igra.php
def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    room=Room(50,50,650, 520)
    objs=[
        Obj(70,70,80, 110),
        Obj(370,470,130, 60)
    ]
    agent=Obj(300,350,70, 70)
    agent.isAgent=True

    for o in objs:
        o.vx=np.random.normal(0, 30)
        o.vy=np.random.normal(0, 30)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        dt=1/fps
        for o in objs:
            o.sim(dt, room)
        agent.sim(dt, room)

        screen.fill((255, 255, 255))
        room.draw(screen)
        for o in objs:
            o.draw(screen)
        agent.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()