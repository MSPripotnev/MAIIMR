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

def limAngDeg(ang):
    while ang > 180: ang -= 360
    while ang <= -180: ang += 360
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

def ptInside(p, poly):
    x,y=p
    n = len(poly)
    inside = False
    p2x = 0.0
    p2y = 0.0
    xints = 0.0
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def drawSegment(screen, p, ang, L, w):
    pp=[[p[0]-L/2, p[1]], [p[0]+L/2, p[1]]]
    c=np.mean(pp, axis=0)
    pp_=np.subtract(pp, c)
    pp=rotArr(pp_, ang)+c
    pygame.draw.line(screen, (0,0,255), *pp, w)
class Car:
    def __init__(self, pos, ang):
        self.pos=pos; self.ang=ang
        self.L=75; self.W=40
        self.vLin=0
        self.vSteer=0
        self.vBrake=0
        self.angSteer=0.1
        self.kWheels=0.7
        self.goal=None
        self.FOV=math.pi/4
        self.viewDist=150

    def getBB(self):
        bb = [[+self.L / 2, -self.W / 2], [+self.L / 2, +self.W / 2], [-self.L / 2, +self.W / 2],
              [-self.L / 2, -self.W / 2]]
        bb_ = np.add(rotArr(bb, self.ang), self.pos)
        return bb_
    def draw(self, screen):
        bb_=self.getBB()
        c=np.mean(bb_, axis=0)
        bbWheels=(bb_-c)*self.kWheels+c
        pygame.draw.polygon(screen, (0,0,255), bb_, 2)
        for p in bbWheels[:2]: drawSegment(screen, p, self.ang+self.angSteer, self.L/5,4)
        for p in bbWheels[2:]: drawSegment(screen, p, self.ang, self.L/5,4)
        if self.goal is not None:
            pygame.draw.circle(screen, (0,0,0), self.goal, 4, 2)
        v0 = np.array(rot([1, 0], self.ang))
        v1 = np.array(rot(v0, self.FOV / 2))
        v2 = np.array(rot(v0, -self.FOV / 2))

        # pygame.draw.line(screen, (255, 0, 0), self.pos, self.pos + self.L*v0, 1)
        pygame.draw.line(screen, (200, 200, 200), self.pos, self.pos + self.viewDist * v1, 1)
        pygame.draw.line(screen, (200, 200, 200), self.pos, self.pos + self.viewDist * v2, 1)
        pygame.draw.line(screen, (200, 200, 200), self.pos + self.viewDist * v1, self.pos + self.viewDist * v2, 1)

    def sim(self, dt):
        if self.vSteer*self.angSteer<=0:
            self.angSteer += self.vSteer * dt
        else:
            self.angSteer+=self.vSteer*dt/(1+10*self.angSteer**2)

        if self.vBrake!=0:
            self.vLin*=math.pow(0.9, self.vBrake)

        if self.angSteer>1: self.angSteer=1
        if self.angSteer<-1: self.angSteer=-1

        vx, vy=rot((self.vLin,0), self.ang)
        self.pos[0]+=vx*dt
        self.pos[1]+=vy*dt

        if self.angSteer!=0:
            R = self.L*self.kWheels / (2 * self.angSteer*dt)
            w = self.vLin / R
            self.ang+=w

    def control(self, dt):
        if self.goal==None: return
        d=dist(self.goal, self.pos)
        vec=np.subtract(self.goal, self.pos)
        dang=limAng(math.atan2(vec[1], vec[0]) - self.ang)
        # self.vSteer = 0
        # self.vLin = 0

    def getFOV(self):
        v0 = np.array(rot([1, 0], self.ang))
        v1 = np.array(rot(v0, self.FOV / 2))
        v2 = np.array(rot(v0, -self.FOV / 2))
        p0=self.pos
        p1=self.pos + self.viewDist * v1
        p2=self.pos + self.viewDist * v2
        return [p0, p1, p2]


class Obj:
    def __init__(self, pos):
        self.pos=pos
        self.observations=[]
    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), self.pos, 4, 2)
        if len(self.observations)>0:
            drawText(screen, f"{self.observations}", self.pos[0]+3, self.pos[1])

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20
    simTime=0

    car = Car([70, 70], 0.5)
    objs =[ Obj([150, 150]),
            Obj([350, 200]),
            Obj([450, 450])
            ]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

                if ev.key == pygame.K_w:
                    car.vLin = 50
                if ev.key == pygame.K_s:
                    car.vLin = -50
                if ev.key == pygame.K_a:
                    car.vSteer = -5
                if ev.key == pygame.K_d:
                    car.vSteer = 5

        dt=1/fps
        car.sim(dt)
        screen.fill((255, 255, 255))
        car.draw(screen)
        for o in objs:
            o.draw(screen)

        a = limAng(car.ang) * 180 / math.pi
        baseAngles = [0, 90, 180, 270]
        da = [abs(limAngDeg(a - b)) for b in baseAngles]
        i = np.argmin(da)
        a_ = baseAngles[i]

        N=0
        for o in objs:
            if ptInside(o.pos, car.getFOV()):
                N+=1
                if a_ not in o.observations:
                    o.observations.append(a_)
                    o.observations=sorted(o.observations)

        F=0
        for o in objs:
            F+= len(o.observations)
        F/=len(baseAngles)
        F/=len(objs)

        drawText(screen, f"N = {N}", 5, 5)

        drawText(screen, f"ang = {int(a)}", 5, 25)
        drawText(screen, f"ang* = {a_}", 5, 45)
        drawText(screen, f"F = {F:.2f}", 5, 65)
        drawText(screen, f"time = {simTime:.2f}", 5, 85)

        pygame.display.flip()
        timer.tick(fps)
        simTime+=dt

main()