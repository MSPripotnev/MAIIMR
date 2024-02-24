import math

import pygame
import numpy as np
import sys

pygame.font.init()
font=pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, str, x, y):
    surf=font.render(str, False, (0,0,0))
    screen.blit(surf, (x,y))

sz=(800,600)

def rot(v, ang):
    s,c=math.sin(ang),math.cos(ang)
    return [v[0]*c-v[1]*s, v[0]*s+v[1]*c]

def limAng(ang):
    while ang>math.pi: ang-=2*math.pi
    while ang<=-math.pi: ang+=2*math.pi
    return ang

def rotArr(vv, ang):
    return [rot(v, ang) for v in vv]

def dist(p1, p2):
    return np.linalg.norm(np.subtract(p1, p2))

def drawRotRect(screen, pc, w, h, ang, color=(0,0,255)):
    pts=[
        [-w/2,-h/2],
        [+w/2,-h/2],
        [+w/2,+h/2],
        [-w/2,+h/2]
         ]
    pts=rotArr(pts,ang)
    pts=np.add(pts, pc)
    pygame.draw.polygon(screen, color,pts,2)

class Ball:
    def __init__(self, x, y, D):
        # координаты
        self.x = x
        self.y = y
        # скорости
        self.vx = 0
        self.vy = 0
        # габариты
        self.D = D


    def getPos(self):
        return np.array((self.x, self.y))

    def draw(self, screen):
        pygame.draw.circle(screen, (0,170,0), self.getPos(), self.D/2, 2)

    def sim(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
class Robot:
    def __init__(self, x, y, ang, W, L):
        #координаты
        self.x=x
        self.y=y
        self.ang=ang
        #скорости
        self.vx=0
        self.vy=0
        self.wAng=0
        #габариты
        self.W=W
        self.L=L

        self.normal=None
        self.collided=False
    def getPos(self):
        return np.array((self.x, self.y))
    def getVec(self):
        return rot((1,0), self.ang)
    def draw(self, screen, color=(0,0,255)):
        drawRotRect(screen, self.getPos(), self.L, self.W, self.ang, color)
        if self.normal is not None:
            pc=self.getPos()
            pygame.draw.line(screen, (255,0,0), pc, pc+self.normal, 2)

    def goToPos(self, pt):
        v=pt-self.getPos()
        aGoal=math.atan2(v[1], v[0])
        aRobot=self.ang
        dAng=limAng(aGoal-aRobot)
        self.wAng=0.5*dAng #П-регулятор
        self.vx=30

    def stayInPlace(self):
        self.wAng = 0
        self.vx = 0


    def sim(self, dt, ball):
        v=rot((self.vx,0), self.ang)
        self.x+=v[0]*dt
        self.y+=v[1]*dt
        self.ang+=self.wAng*dt

        #расчет отталкивания мяча
        if self.normal is not None:
            d=dist(self.getPos(), ball.getPos())
            d_=np.linalg.norm(self.normal)+ball.D/2
            thr = 10
            if abs(d - d_)<thr:
                if not self.collided:
                    #поворачиваем систему координат
                    alpha = math.atan2(self.normal[1], self.normal[0])
                    vRot=rot((ball.vx-v[0], ball.vy-v[1]), -alpha)
                    vRot[0]*=-1 #отражаем x-компоненту скорости
                    ball.vx, ball.vy=rot(vRot, alpha)
                    self.collided=True
                elif abs(d - d_)>(thr+5):
                    self.collided = False

    def getNearestNormal(self, ballPt):
        pts = [
            [-self.L / 2, -self.W / 2],
            [+self.L / 2, -self.W / 2],
            [+self.L / 2, +self.W / 2],
            [-self.L / 2, +self.W / 2]
        ]
        pts=rotArr(pts, self.ang)
        vv=[]
        for i in range(len(pts)):
            vv.append(np.mean((pts[i-1],pts[i]), axis=0))

        vBall=np.subtract(ballPt,self.getPos())
        dotProducts=[np.dot(v, vBall) for v in vv]
        i = np.argmax(dotProducts)
        self.normal=vv[i]
        return vv[i]

class Team:
    def __init__(self, area, numRobots, step, isLeft=True):
        L=(numRobots-1)*step
        D=area.L/4
        self.robots=[]
        self.isLeft=isLeft
        for i in range(numRobots):
            p=[-D if isLeft else D, -L/2+i*step]
            iDelta=abs(i-(numRobots-1)/2)
            p[0]*=0.5*(1+iDelta)
            ang=0 if isLeft else math.pi
            r=Robot(*area.getGlobalPt(p), ang, 45, 70)
            self.robots.append(r)
    def draw(self, screen):
        for r in self.robots:
            r.draw(screen, (170, 170, 0) if self.isLeft else (0,0,255))

    def control1(self, ball):
        g = (1,0) if self.isLeft else (-1,0) #вектор в сторону команды противника
        # векторы собственного направления роботов
        vv=[r.getVec() for r in self.robots]
        dotProducts=[np.dot(g, v) for v in vv]
        iBest = np.argmax(dotProducts)
        for i,r in enumerate(self.robots):
            if i==iBest: r.goToPos(ball.getPos())
            else: r.stayInPlace()

    def control2(self, ball):
        # расстояния от робота до мяча
        dd = [dist(r.getPos(), ball.getPos()) for r in self.robots]
        iBest = np.argmin(dd)
        for i, r in enumerate(self.robots):
            if i == iBest:
                r.goToPos(ball.getPos())
            else:
                r.stayInPlace()
    def control3(self, ball):
        # вектор в сторону команды противника
        g = (1, 0) if self.isLeft else (-1, 0)
        # векторы собственного направления роботов
        vv = [r.getVec() for r in self.robots]
        dotProducts1 = [np.dot(g, v) for v in vv]
        iBest1 = np.argmax(dotProducts1)
        # расстояния от робота до мяча
        dd = [dist(r.getPos(), ball.getPos()) for r in self.robots]
        iBest2 = np.argmin(dd)
        # векторы от роботов до мяча
        uu=[np.subtract(r.getPos(), ball.getPos()) for r in self.robots]
        dotProducts3 = [np.dot(g, u) for u in uu]
        iBest3 = np.argmax(dotProducts3)

        zz=np.add(dotProducts1,dotProducts3)/dd
        iBest = np.argmax(zz)

        for i, r in enumerate(self.robots):
            if i == iBest:
                r.goToPos(ball.getPos())
            else:
                r.stayInPlace()

    def sim(self, dt, ball, controlType):
        if controlType==1:self.control1(ball)
        if controlType==2:self.control2(ball)
        if controlType==3:self.control3(ball)
        for r in self.robots:
            # r.goToPos(ball.getPos())
            r.getNearestNormal(ball.getPos())
            r.sim(dt, ball)
class Area:
    def __init__(self, p0, W, L):
        self.p0=p0
        self.W=W
        self.L=L
    def draw(self, screen):
        pygame.draw.rect(screen, (0,170,0), (*self.p0, self.L, self.W), 2)
        p1=(self.p0[0]+self.L/2, self.p0[1])
        p2=(p1[0], p1[1]+self.W)
        pygame.draw.line(screen, (0,170,0), p1, p2, 2)
    def isPtInside(self,pt):
        if pt[0]<self.p0[0]: return False
        if pt[1]<self.p0[1]: return False
        if pt[0]>self.p0[0]+self.L: return False
        if pt[1]>self.p0[0]+self.W: return False
        return True

    def getGlobalPt(self, ptLocal):
        pc=np.add(self.p0, (self.L/2,self.W/2))
        return np.add(pc, ptLocal)
    def getLocalPt(self, ptGlobal):
        pc=np.add(self.p0, (self.L/2,self.W/2))
        return np.subtract(ptGlobal, pc)

def main():
    screen=pygame.display.set_mode(sz)
    timer=pygame.time.Clock()
    fps=60

    a=Area((25, 25), W=sz[1]-50, L=sz[0]-50)
    b=None
    team = None
    team2 = None

    score1 = 0
    score2 = 0

    def initScene():
        nonlocal b
        nonlocal team, team2
        team=Team(a, 3, 70, True)
        team2=Team(a, 3, 70, False)
        p1=a.getGlobalPt((-200,0))
        p2=a.getGlobalPt((+200,0))

        ptRnd=(np.random.randint(-10,10+1), np.random.randint(-10,10+1))
        b=Ball(*a.getGlobalPt(ptRnd),70)
        # b.vx=30
        # b.vy=20

    initScene()

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_r:
                    initScene()

        dt=1/fps

        team.sim(dt, b, 1)
        team2.sim(dt, b, 3)
        b.sim(dt)

        ok = a.isPtInside(b.getPos())
        if not ok:#мяч вылетел за пределы
            ptLocal=a.getLocalPt(b.getPos())
            if ptLocal[0]>0: score1+=1
            else: score2+=1
            initScene()

        screen.fill((255,255,255))
        drawText(screen, f"Status = {ok}", 5,5)
        drawText(screen, f"Score 1 = {score1}", 5,35)
        drawText(screen, f"Score 2 = {score2}", 5,65)
        # pygame.draw.circle(screen, (255,0,0), (200,200),5, 2)
        # drawRotRect(screen, (400,400), 100, 70, 2)
        team.draw(screen)
        team2.draw(screen)
        b.draw(screen)
        a.draw(screen)

        pygame.display.flip()
        timer.tick(fps)

main()