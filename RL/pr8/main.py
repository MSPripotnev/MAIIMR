import sys, pygame
import numpy as np
import math

import helper
from am import AM

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
    pts = [[- w/2, - h/2], [+ w/2, - h/2], [+ w/2, + h/2], [- w/2, + h/2],]
    pts = rotArr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

def drawSegment(screen, p, ang, L, w):
    pp=[[p[0]-L/2, p[1]], [p[0]+L/2, p[1]]]
    c=np.mean(pp, axis=0)
    pp_=np.subtract(pp, c)
    pp=rotArr(pp_, ang)+c
    pygame.draw.line(screen, (0,0,255), *pp, w)

def findIntersection(sensor, robots):
    pi, pj=sensor.getSegment()
    pp=[]
    for r in robots:
        bb_=r.getBB()
        for i in range(len(bb_)):
            pa, pb=bb_[i-1], bb_[i]
            p=helper.find_intersection(pi, pj, pa, pb)
            if p is not None:
                d=dist(p, pi)
                if d>0.001:
                    pp.append(p)
    if len(pp)>0:
        dd = [dist(p, pi) for p in pp]
        i = np.argmin(dd)
        return pp[i]
    return None

class Sensor:
    def __init__(self, robot, x, y, ang, d=100):
        self.d = d
        self.x = x
        self.y = y
        self.ang = ang
        self.robot = robot

    def draw(self, screen):
        p, p2=self.getSegment()
        pygame.draw.circle(screen, (255,0,0), p, 8, 2)
        pygame.draw.line(screen, (255, 0, 0), p, p2, 2)
    def getPos(self):
        p = rot([self.x, self.y], self.robot.ang)
        p = [p[0] + self.robot.x, p[1] + self.robot.y]
        return p
    def getSegment(self):
        p = self.getPos()
        a = self.ang + self.robot.ang
        s, c = math.sin(a), math.cos(a)
        p2 = np.add(p, [c * self.d, s * self.d])
        return p, p2
    def getValue(self, cars):
        pInt=findIntersection(self, cars)
        if pInt is None: return 0
        return dist(self.getPos(),pInt)

class Car:
    def __init__(self, x, y, ang):
        self.x=x; self.y=y; self.ang=ang
        self.L=150; self.W=75
        self.vLin=0
        self.vSteer=0
        self.vBrake=0
        self.angSteer=0.1
        self.kWheels=0.7
        self.sens = [
            Sensor(self,self.L/2,0,0),
            Sensor(self,self.L/3,self.W/2,math.pi/2),
            Sensor(self,-self.L/3,self.W/2,math.pi/2),
            Sensor(self, -self.L / 2, 0, math.pi),
            Sensor(self, self.L/3, -self.W / 2, -math.pi / 2),
            Sensor(self, -self.L/3, -self.W / 2, -math.pi / 2)
        ]

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
        for s in self.sens:
            s.draw(screen)
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


def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    car1 = Car(200, 100, 0.1)
    car2 = Car(600, 100, -0.05)
    car3 = Car(150, 200, 3.14)

    assocMem=AM("log.txt", 6)

    modeAuto=False

    controlPlan=np.zeros((100,2))

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")
                elif ev.key == pygame.K_w:
                    car3.vLin=25
                    car3.vSteer=0
                    car3.vBrake=0
                elif ev.key == pygame.K_s:
                    car3.vLin=-25
                    car3.vSteer=0
                    car3.vBrake=0
                elif ev.key == pygame.K_a: car3.vSteer=-2
                elif ev.key == pygame.K_d: car3.vSteer=2
                elif ev.key == pygame.K_z:
                    car3.vBrake=1
                    car3.vSteer=0
                    car3.angSteer=0
                elif ev.key == pygame.K_1:
                    modeAuto=not modeAuto

        dt=1/fps

        cars=[car1, car2, car3]

        vv = [s.getValue(cars) for s in car3.sens]
        vv2 = [int(v) for v in vv]

        if modeAuto:
            #1 ищем индекс наиболее похожего воспоминания
            i = assocMem.findIndex(vv)
            #2 сдвиг плана управляющих воздействий на робота на 1 такт
            controlPlan2=np.zeros((100, 2))
            controlPlan2[:-1] = controlPlan[1:]
            controlPlan2[-1] = np.zeros((1, 2))
            #3 заполнение плана управляющих воздействий на робота
            for j in range(i, min(len(controlPlan), i+100)):
                u=assocMem.table[j][1]
                controlPlan[j-i]+=0.4*np.subtract(u, controlPlan[j-i])
            #4 выбор управления
            u=controlPlan[0]
            car3.vLin=u[0]
            car3.vSteer=u[1]

            # u=assocMem.findControl(vv)
            # car3.vLin=u[0]
            # car3.vSteer=u[1]

        car3.sim(dt)
        pp=[]
        for car in cars:
            for s in car.sens:
                pInt=findIntersection(s, cars)
                if pInt is not None:
                    pp.append(pInt)

        screen.fill((255, 255, 255))
        for car in cars:
            car.draw(screen)

        for p in pp:
            pygame.draw.circle(screen, (0,255,0), p, 3, 2)

        drawText(screen, f"Values = {vv2}", 5, 5)
        drawText(screen, f"AUTO = {modeAuto}", 5, 25)

        pygame.display.flip()
        timer.tick(fps)

main()