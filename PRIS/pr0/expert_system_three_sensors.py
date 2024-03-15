#S. Diane, 2024
import math

import pygame
import sys
import numpy as np

WIDTH, HEIGHT=800, 600

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, s, x, y):
    plane=font.render(s, False, (0,0,0))
    screen.blit(plane, (x,y))

def limAng(ang):
    while ang<=-math.pi: ang+=2*math.pi
    while ang>math.pi: ang-=2*math.pi
    return ang

def rot(v, ang):
    s,c=np.sin(ang), np.cos(ang)
    x=v[0]*c-v[1]*s
    y=v[0]*s+v[1]*c
    return (x,y)

def rotArr(vv, ang):
    return [rot(v, ang) for v in vv]

def dist(p1, p2):
    return np.linalg.norm(np.subtract(p2,p1))

class Obj:
    def __init__(self, x, y, sz=15):
        self.x=x
        self.y=y
        self.sz=sz
        self.color=(0,0,255)
        self.isDetected=False
    def getPos(self):
        return (self.x, self.y)
    def draw(self, screen):
        x_, y_=self.x-self.sz/2, self.y-self.sz/2
        bb=(x_, y_, self.sz, self.sz)
        w=4 if self.isDetected else 2
        pygame.draw.rect(screen, self.color, bb, w)

class Robot:
    def __init__(self, x, y, ang = 1, sz=70):
        self.x=x
        self.y=y
        self.ang=ang
        self.sz=sz
        self.vLin=0
        self.vRot=0
        self.coveredDist=0
        self.debugInfo=""
        v0=(sz, 0)
        self.sensors=[
            Sensor(self, *rot(v0, -45 / 180 * np.pi)),
                   Sensor(self, *v0),
           Sensor(self, *rot(v0, 45 / 180 * np.pi)) ]
    def getPos(self):
        return (self.x, self.y)
    def getObjs(self, ind, objs):
        return [o for o in objs if self.sensors[ind].contains(*o.getPos())]
    def goto(self, x, y):
        alpha=math.atan2(y-self.y, x-self.x)
        beta=self.ang
        gamma=limAng(alpha-beta)
        self.vRot=0.3*gamma
        self.vLin=50
    def control(self, objs):
        detections=[self.getObjs(0, objs), self.getObjs(1, objs), self.getObjs(2, objs)]
        nn=[len(d) for d in detections]
        s="; ".join([str(n) for n in nn])
        rule=-1

        if self.x<0 or self.x>WIDTH or self.y<0 or self.y>HEIGHT:
            # нужно двигаться к центру
            self.goto(WIDTH/2, HEIGHT/2)
            rule=0
        elif nn[0]==0: #двигаться вперед
            self.vRot, self.vLin=0, 50
            rule=1
        elif nn[1]>=nn[0] and nn[1]>=nn[2]: #нужна остановка
            self.vRot, self.vLin=0.5, 10
            rule=2
        elif nn[0]<(nn[1]+nn[2])/2: #нужно двигаться налево
            self.vRot, self.vLin = -0.5, 50
            rule=3
        elif nn[2]<(nn[0]+nn[1])/2: #нужно двигаться направо
            self.vRot, self.vLin = 0.5, 50
            rule=4
        else: #нужно двигаться вперед
            self.vRot, self.vLin = 0, 20
            rule=5

        self.debugInfo=f"nn = {s}, r = {rule}"

    def sim(self, dt):
        v=rot((self.vLin,0), self.ang) #вектор продольного направления
        self.x+=v[0]*dt
        self.y+=v[1]*dt
        self.ang+=self.vRot*dt
        self.coveredDist += np.linalg.norm(np.array(v)*dt)

    def draw(self, screen):
        x_, y_=self.x-self.sz/2, self.y-self.sz/2
        rect=[[x_, y_], [x_+self.sz, y_],
              [x_+self.sz, y_+self.sz], [x_, y_+self.sz]]
        rect_=rotArr(np.subtract(rect, self.getPos()), self.ang)
        rect_=rect_ + np.array(self.getPos())
        pygame.draw.lines(screen, (0,0,0), True, rect_, 3)
        for s in self.sensors:
            s.draw(screen)
    def contains(self, x, y):
        dx, dy=x-self.x, y-self.y
        dx, dy=rot((dx,dy), -self.ang)
        return -self.sz//2<dx<self.sz//2 and -self.sz//2<dy<self.sz//2


class Sensor:
    def __init__(self, robot, x, y, r=70):
        self.robot=robot
        self.x=x
        self.y=y
        self.r=r
    def getPos(self):
        return (self.x, self.y)
    def getGlobalPos(self):
        return np.array(self.robot.getPos()) + rot(self.getPos(), self.robot.ang)
    def contains(self, x, y):
        d=dist((x,y), self.getGlobalPos())
        return d<self.r
    def draw(self, screen):
        x,y=self.getGlobalPos()
        pygame.draw.circle(screen, (255,0,0), (x, y), self.r, 1)

def calcControlQuality(tSim, coveredDist, nColl, nDet):
    Q=nDet/30 / (tSim/60 + coveredDist/1000 + nColl/30 + 0.001)
    return Q

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    timer = pygame.time.Clock()

    r = Robot(130, 130)
    fps = 20
    tSim=0
    tInd=0
    nColl=0
    nDet=0

    objs=[]
    for i in range(20):
        x=np.random.randint(50, WIDTH-50)
        y=np.random.randint(50, HEIGHT-50)
        objs.append(Obj(x, y))

    logFile = None

    while True:
        if tSim>=60 and logFile is not None:
            Q=calcControlQuality(tSim, r.coveredDist, nColl, nDet)
            logFile.write(f"Q = {Q}")
            logFile.close()
            sys.exit(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logFile.write(f"Q = {Q}")
                logFile.close()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    arr=[f"{o.x} {o.y}" for o in objs]
                    text= "; ".join(arr)
                    with open("map.txt", "w") as f:
                        f.write(text)
                if event.key == pygame.K_l:
                    tSim=0
                    nColl=0
                    tInd = 0
                    nDet = 0
                    r = Robot(130, 130)
                    logFile= open("log.txt", "w")
                    with open("map.txt", "r") as f:
                        tokens=f.read().split("; ")
                        pts=[[float(x) for x in t.split(" ")] for t in tokens]
                        objs.clear()
                        for p in pts:
                            objs.append(Obj(*p))

        screen.fill( (255,255,255) )

        # аналитическое управление
        # r.vLin = 50
        # r.vRot = -0.2

        # экспертное управление
        r.control(objs)

        r.sim(1/fps)

        for o in objs:
            if r.contains(*o.getPos()):
                o.color = (255, 0, 0)
                nColl+=1
            else:
                for s in r.sensors:
                    if s.contains(*o.getPos()):
                        o.color=(0,200,200)
                        o.isDetected=True
                        break
                    else: o.color=(0,0,255)

        r.draw(screen)

        for o in objs:
            o.draw(screen)

        drawText(screen, r.debugInfo, 5, 5)
        drawText(screen, f"tSim={tSim:.2f}, d={r.coveredDist:.2f}", 5, 30)
        drawText(screen, f"nColl={nColl}", 5, 55)
        nDet=len([o for o in objs if o.isDetected])
        drawText(screen, f"nDet={nDet}", 5, 80)

        if logFile is not None:
            Q=calcControlQuality(tSim, r.coveredDist, nColl, nDet)
            drawText(screen, f"Q={Q:.3f}", 5, 105)

        if logFile is not None and tInd%fps==0:
            logFile.write(f"{tSim:.2f} {r.coveredDist:.2f} {nColl} {nDet}\n")

        pygame.display.flip()
        timer.tick(fps)
        tSim+=1/fps
        tInd+=1

main()