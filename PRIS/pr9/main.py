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

    def controlFSM(self, fsm):
        if fsm.getState("Left").isActive:
            self.vRot, self.vLin = -0.5, 50
        elif fsm.getState("Stay").isActive:
            self.vRot, self.vLin = 0, 0
        elif fsm.getState("Right").isActive:
            self.vRot, self.vLin = 0.5, 50
        else:
            self.vRot, self.vLin = 0, 0
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
    def containsObj(self, objs):
        for o in objs:
            if self.contains(*o.getPos()):
              return True
        return False
    def draw(self, screen):
        x,y=self.getGlobalPos()
        pygame.draw.circle(screen, (255,0,0), (x, y), self.r, 1)

def calcControlQuality(tSim, coveredDist, nColl, nDet):
    Q=nDet/30 / (tSim/60 + coveredDist/1000 + nColl/30 + 0.001)
    return Q


def getProbS(tt):
    p = np.random.rand()
    r = 0
    for t in tt:
        r+=t[1]
        if r > p:
            return t[0]

def getProbArgmax(arr):
    p = np.random.rand()
    r = 0
    for i,a in enumerate(arr):
        r+=a
        if r > p:
            return i

class State:
    def __init__(self, x, y, name):
        self.x=x
        self.y=y
        self.name=name
        self.transitions={}
        self.isActive=False
    def getPos(self):
        return (self.x, self.y)
    def draw(self, screen, dx=0, dy=0):
        p = np.add(self.getPos(), [dx, dy])
        pygame.draw.circle(screen, (0, 0, 0), p, 20, 2)
        if self.isActive:
            pygame.draw.circle(screen, (0, 255, 0), p, 20, 0)
        drawText(screen, self.name, *p)


class FSM: #Finite State Machine
    def __init__(self):
        self.states=[
            State(0, -50, "S0"),
            State(-50, 0, "S1"),
            State(0, 0, "S2"),
            State(50, 0, "S3"),
            State(-50, 50, "Left"),
            State(0, 50, "Stay"),
            State(50, 50, "Right")
        ]

        def P(r,s,l):
            return [["Right", r], ["Stay", s], ["Left", l]]
        def Q(s):
            return [[s,1]]

        #таблица переходов конечного автомата
        self.getState("S0").transitions={"S0":P(0.5, 0, 0.5), "S1":Q("S1"), "S2":Q("S2"), "S3":Q("S3")}
        self.getState("S1").transitions={"S0":Q("S0"), "S1":P(0.7, 0.2, 0.1), "S2":Q("S2"), "S3":Q("S3")}
        self.getState("S2").transitions={"S0":Q("S0"),"S1":Q("S1"), "S2":P(0.1, 0.8, 0.1), "S3":Q("S3")}
        self.getState("S3").transitions={"S0":Q("S0"),"S1":Q("S1"), "S2":Q("S2"), "S3":P(0.1, 0.2, 0.7)}
        self.getState("Left").transitions={"S0":Q("S0"),"S1":Q("S1"), "S2":Q("S2"), "S3":Q("S3")}
        self.getState("Stay").transitions={"S0":Q("S0"),"S1":Q("S1"), "S2":Q("S2"), "S3":Q("S3")}
        self.getState("Right").transitions={"S0":Q("S0"),"S1":Q("S1"), "S2":Q("S2"), "S3":Q("S3")}

    def getState(self, name):
        return [s for s in self.states if s.name==name][0]

    def draw(self, screen, dx=0, dy=0):
            for s in self.states:
                s.draw(screen, dx, dy)
                for k in s.transitions.keys():
                    s1=s

                    tt=s.transitions[k]
                    state=getProbS(tt)

                    s2=self.getState(state)

                    p1=np.add(s1.getPos(), [dx, dy])
                    p2=np.add(s2.getPos(), [dx, dy])
                    pygame.draw.line(screen, (255, 0, 0), p1, p2)

    def makeTransition(self, signal):
        for s in self.states:
            if s.isActive:
                s.isActive=False
                tt = s.transitions[signal]
                state = getProbS(tt)
                s2=self.getState(state)
                s2.isActive=True
                break

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

    fsm=FSM()
    fsm.getState("Stay").isActive=True
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

        fsm.draw(screen, 300, 60)

        signals=["S0", "S1", "S2", "S3"]
        ind=-1
        pp=np.zeros(3)
        for i in range(3):
            if r.sensors[i].containsObj(objs):
                ind=i
                pp[i]=1

        if sum(pp)>0:
            pp/=sum(pp)
            ind=getProbArgmax(pp)
        ind+=1

        fsm.makeTransition(signals[ind])

        # аналитическое управление
        # r.vLin = 50
        # r.vRot = -0.2

        # экспертное управление
        # r.control(objs)
        r.controlFSM(fsm)

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