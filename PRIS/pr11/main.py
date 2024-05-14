import sys, pygame
import numpy as np
import math
from parse import parse

from manip import *

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
    def __init__(self, pos, L, W):
        self.pos, self.L, self.W=pos, L, W
        self.vLin=0
        self.manip=Manipulator(0,0, 70, 45)
    def draw(self, screen, color=(0,0,0)):
        drawRotRect(screen, color, self.pos, self.L, self.W, 0)
        p1=np.add(self.pos, [-self.L/3, 0.8*self.W])
        p2=np.add(self.pos, [self.L/3, 0.8*self.W])
        pygame.draw.circle(screen, color, p1, self.L/4, 2)
        pygame.draw.circle(screen, color, p2, self.L/4, 2)
        self.manip.draw(screen)
    def sim(self, dt):
        d=[self.vLin*dt, 0]
        self.pos=np.add(self.pos, d)
        self.manip.x=self.pos[0]+self.L/2
        self.manip.y=self.pos[1]-self.W/2
class Obj:
    def __init__(self, pos, sz):
        self.pos, self.sz=pos, sz
        self.robot=None
    def draw(self, screen, color=(0,0,0)):
        pygame.draw.circle(screen, (0,0,0), self.pos, self.sz/2, 2)

    def sim(self, dt):
        if self.robot is not None:
            self.pos=self.robot.getEndpoint()

def loadMemory(file_path):
    am = {}
    with open(file_path, "r") as f:
        while True:
            str = f.readline()
            if not str: break
            res = parse("{}_{}_{}", str)
            distance_to_object = float(res[0])
            # фильтрация
            for i in range(round(distance_to_object)-5, round(distance_to_object)+5):
                if float(i) in am:
                    distance_to_object = round(float(i))
                    break
            am[distance_to_object] = [float(res[1]), float(res[2][:-1])]
    return am

def drawFloor(screen, sz, y):
    pygame.draw.line(screen, (0,0,0), [0, y], [sz[0], y], 2)
def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    robot=Robot([200,400], 70, 45)
    yFloor=400+robot.W/2+30
    obj=Obj([300,yFloor-8], 15)
    asm = loadMemory("catch.log")

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_s:
                    robot.vLin=0
                if ev.key == pygame.K_d:
                    robot.vLin=10
                if ev.key == pygame.K_a:
                    robot.vLin=-10
                if ev.key == pygame.K_q:
                    robot.manip.a1+=0.1
                if ev.key == pygame.K_w:
                    robot.manip.a1-=0.1
                if ev.key == pygame.K_e:
                    robot.manip.a2+=0.1
                if ev.key == pygame.K_r:
                    robot.manip.a2-=0.1
                if ev.key == pygame.K_m:
                    robot.manip.coordDescent(obj.pos)
                if ev.key == pygame.K_l:
                    with open("catch.log", "a") as f:
                        f.write(f"{dist(obj.pos, robot.pos)}_{robot.manip.a1}_{robot.manip.a2}\n")
                    loadMemory("catch.log")
                if ev.key == pygame.K_f:
                    d = round(dist(obj.pos, robot.pos))
                    print(d)
                    if d not in asm:
                        rs, rsi = [], []
                        for i in asm.keys():
                            rs.append(abs(i-d))
                            rsi.append(i)
                        d = rsi[rs.index(min(rs))]
                    print(d)
                    robot.manip.a1 = asm[d][0]
                    robot.manip.a2 = asm[d][1]


        dt=1/fps

        robot.sim(dt)

        screen.fill((255, 255, 255))
        drawFloor(screen, sz, yFloor)
        robot.draw(screen)
        obj.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()