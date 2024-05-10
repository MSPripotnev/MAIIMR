import sys, pygame
import numpy as np
import math
from fuz import Term, calcFuzzy

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

def drawSegment(screen, p, ang, L, w):
    pp=[[p[0]-L/2, p[1]], [p[0]+L/2, p[1]]]
    c=np.mean(pp, axis=0)
    pp_=np.subtract(pp, c)
    pp=rotArr(pp_, ang)+c
    pygame.draw.line(screen, (0,0,255), *pp, w)
class Car:
    def __init__(self, x, y, ang):
        self.x=x; self.y=y; self.ang=ang
        self.L=150; self.W=75
        self.vLin=0
        self.vSteer=0
        self.vBrake=0
        self.angSteer=0.1
        self.kWheels=0.7
        self.goal=None

    def getBB(self):
        bb = [[+self.L / 2, -self.W / 2], [+self.L / 2, +self.W / 2], [-self.L / 2, +self.W / 2],
              [-self.L / 2, -self.W / 2]]
        bb_ = np.add(rotArr(bb, self.ang), [self.x, self.y])
        return bb_
    def draw(self, screen):
        bb_=self.getBB()
        c=np.mean(bb_, axis=0)
        bbWheels=(bb_-c)*self.kWheels+c
        pygame.draw.polygon(screen, (0,0,255), bb_, 2)
        for p in bbWheels[:2]: drawSegment(screen, p, self.ang+self.angSteer, 30,4)
        for p in bbWheels[2:]: drawSegment(screen, p, self.ang, 30,4)
        if self.goal is not None:
            pygame.draw.circle(screen, (0,0,0), self.goal, 4, 2)
    def sim(self, dt):
        self.angSteer+=self.vSteer*dt
        if self.vBrake!=0:
            self.vLin*=math.pow(0.9, self.vBrake)

        if self.angSteer>1: self.angSteer=1
        if self.angSteer<-1: self.angSteer=-1

        vx, vy=rot((self.vLin,0), self.ang)
        self.x+=vx*dt
        self.y+=vy*dt

        if self.angSteer!=0:
            R = self.L*self.kWheels / (2 * self.angSteer*dt)
            w = self.vLin / R
            self.ang+=w

    def control(self, dt):
        if self.goal==None: return

        t1 = Term("Small", 0, 1000)
        t2 = Term("Mid", 500, 1000)
        t3 = Term("Big", 1000, 1000)

        p=[self.x,self.y]
        d=dist(self.goal, p)

        # тестовая база правил, отображающая нечеткие значения сами в себя
        R = [[0, 0], [1, 2], [2, 1]]
        # массив термов
        terms = [t1, t2, t3]
        self.vLin = calcFuzzy(d, terms, R) / 10

        s1 = Term("Neg", -90, 180)
        s2 = Term("Zero", 0, 180)
        s3 = Term("Pos", 90, 180)

        vec=np.subtract(self.goal, p)
        dang=limAng(math.atan2(vec[1], vec[0]) - self.ang)
        dang*=180/math.pi

        # тестовая база правил, отображающая нечеткие значения сами в себя
        R2 = [[0, 0], [1, 2], [2, 1]]
        # массив термов
        terms2 = [s1, s2, s3]
        vSteer= calcFuzzy(dang, terms2, R2)
        self.vSteer = vSteer * math.pi / 180


def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    car = Car(100,100,20)
    car.goal = [400,400]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        dt=1/fps
        car.control(dt)
        car.sim(dt)

        screen.fill((255, 255, 255))
        car.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()