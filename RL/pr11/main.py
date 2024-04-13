#S. Diane, 2024
#Probabilistic FSM for robot control
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
    def containsObj(self, objs):
        for o in objs:
            if self.contains(*o.getPos()):
              return True
        return False
    def draw(self, screen):
        x,y=self.getGlobalPos()
        pygame.draw.circle(screen, (255,0,0), (x, y), self.r, 1)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    timer = pygame.time.Clock()

    r = Robot(230, 230)
    fps = 20
    tSim=0
    tInd=0
    nColl=0
    nDet=0

    objs=[]
    step=50
    margin=150
    nx=(WIDTH-margin*2)//step
    ny=(HEIGHT-margin*2)//step
    for i in range(nx): objs.append(Obj(margin+i*step, margin))
    for i in range(nx): objs.append(Obj(WIDTH-margin-i*step, HEIGHT-margin))
    for i in range(ny): objs.append(Obj(margin, margin+i*step))
    for i in range(ny): objs.append(Obj(WIDTH-margin, HEIGHT-margin-i*step))

    logFile = None

    experience=[]
    #TODO: построить 2д табличку апостериорных вероятностей столкновения робота - например P("C" | "F", "Mf")
    test=['R', 'S', '_', 'Z', 'Ml', '_', 'L', 'Ml', '_', 'F', 'Mr', '_', 'F', 'Mr', 'C', 'F', 'Mr', 'C', 'F', 'Mr', '_', 'L', 'Ml', '_', 'L', 'Mf', '_', 'Z', 'Mf', '_', 'F', 'Mf', '_', 'Z', 'Mr', '_', 'Z', 'Mr', '_', 'Z', 'Mr', '_', 'Z', 'Mr', '_', 'R', 'Mf', '_', 'R', 'Mf', '_', 'R', 'Mr', '_', 'F', 'Mf', 'C', 'F', 'Mf', 'C', 'L', 'Mr', '_', 'F', 'Mr', '_', 'L', 'Mr', '_', 'Z', 'Mf', '_', 'F', 'Mf', '_', 'F', 'Ml', '_', 'F', 'Ml', 'C', 'F', 'Ml', 'C', 'F', 'Ml', 'C', 'F', 'Mf', '_', 'Z', 'Mf', '_', 'L', 'Mf', '_', 'F', 'Mr', '_', 'F', 'Mr', 'C', 'F', 'Mr', 'C', 'F', 'Mr', 'C', 'L', 'Mf', '_', 'Z', 'Mf', '_', 'F', 'Mf', '_', 'F', 'Mf', 'C']

    lastT=0

    while True:
        if tSim>=60 and logFile is not None:
            logFile.close()
            sys.exit(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logFile.close()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    arr=[f"{o.x} {o.y}" for o in objs]
                    text= "; ".join(arr)
                    with open("map.txt", "w") as f:
                        f.write(text)
                if event.key == pygame.K_w:
                    r.vLin=100
                    r.vRot=0
                if event.key == pygame.K_s:
                    r.vLin=0
                if event.key == pygame.K_a:
                    r.vRot=-1
                if event.key == pygame.K_d:
                    r.vRot=1
                if event.key == pygame.K_i:
                    print(experience)

        screen.fill( (255,255,255) )

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

        if tSim-lastT>1:

            if r.sensors[1].containsObj(objs):
                experience.append("F")
            elif r.sensors[0].containsObj(objs):
                experience.append("L")
            elif r.sensors[2].containsObj(objs):
                experience.append("R")
            else:
                experience.append("Z")

            if r.vLin>5 and abs(r.vRot)<0.1:
                experience.append("Mf")
            elif r.vLin>5 and r.vRot<0:
                experience.append("Ml")
            elif r.vLin>5 and r.vRot>0:
                experience.append("Mr")
            elif r.vLin<=5:
                experience.append("S")

            C=any(r.contains(*o.getPos()) for o in objs)

            if C:
                experience.append("C")
            else:
                experience.append("_")
            lastT=tSim

        drawText(screen, r.debugInfo, 5, 5)
        drawText(screen, f"tSim={tSim:.2f}, d={r.coveredDist:.2f}", 5, 30)
        drawText(screen, f"nColl={nColl}", 5, 55)
        nDet=len([o for o in objs if o.isDetected])
        drawText(screen, f"nDet={nDet}", 5, 80)

        if logFile is not None and tInd%fps==0:
            logFile.write(f"{tSim:.2f} {r.coveredDist:.2f} {nColl} {nDet}\n")

        pygame.display.flip()
        timer.tick(fps)
        tSim+=1/fps
        tInd+=1

main()