import sys, pygame
import numpy as np
import math

import helper

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

def distPtLine(p, pA, pB):
    L1=dist(p, pA)
    v1=np.subtract(p, pA)
    v2=np.subtract(pB, pA)
    d=np.dot(v1, v2)/np.linalg.norm(v2)
    return math.sqrt(L1**2-d**2)
def projPtLine(p, pA, pB):
    v1=np.subtract(p, pA)
    v2=np.subtract(pB, pA)
    d=np.dot(v1, v2)/np.linalg.norm(v2)
    if d<0 or d>dist(pA, pB):
        return None
    v=v2/np.linalg.norm(v2)
    return np.add(v*d, pA)


def getSegmNormal(segm):
    n = rotArr(np.subtract(segm, segm[0]), -math.pi / 2)
    n /= np.linalg.norm(n)
    return n

def getTorque(f, p, c):
    r=np.subtract(c,p)
    d=np.dot(f, r)/np.linalg.norm(r)
    f_=np.linalg.norm(f)
    f__=math.sqrt(f_**2-d**2)
    z=np.cross(f, r)
    return np.sign(z)*f__*np.linalg.norm(r)

class Bike:
    def __init__(self, x, y, ang, L=100, D=30):
        self.L=L
        self.D=D
        self.m=1
        self.p=np.array((x,y), dtype=float)
        self.a=np.zeros(2, dtype=float)
        self.v=np.zeros(2, dtype=float)

        self.J=1
        self.eps=0
        self.w=0

        self.ang=ang
        self.forces=[]
        self.contactPts=[]

    def getP1P2(self):
        p1=[-self.L/2, 0]
        p2=[+self.L/2, 0]
        p1, p2 = rotArr([p1, p2], self.ang)
        p1, p2 = np.add([p1, p2], self.p)
        return p1, p2
    def draw(self, screen):
        p1, p2 = self.getP1P2()
        pygame.draw.line(screen, (0,100,100), p1, p2, 2)
        pygame.draw.circle(screen, (0,100,100), p1, self.D/2, 2)
        pygame.draw.circle(screen, (0,100,100), p2, self.D/2, 2)
    def sim(self, dt):
        F=self.m * np.array([0, 9.8])
        R=np.array(F)
        for f in self.forces:
            f_=np.array(f)
            R=R+f_*100 #TODO: сделать пропорционально глубине погружения
        self.a = R/self.m
        self.v+=self.a*dt
        self.p+=self.v*dt

        Q=0
        for p, f in zip(self.contactPts, self.forces):
            q=getTorque(f, p, self.p)
            Q+=q*0.1 #TODO: сделать пропорционально глубине погружения

        self.eps=Q/self.J
        self.w+=self.eps*dt
        self.ang+=self.w*dt

    def findPointsAndNormals(self, terrain):
        res=[]
        for i in range(1, len(terrain.pts)):
            segm=[terrain.pts[i-1], terrain.pts[i]]
            p1, p2 = self.getP1P2()
            if distPtLine(p1, *segm)<self.D/2:
                p=projPtLine(p1, *segm)
                n=getSegmNormal(segm)[1]
                if p is not None:
                    res.append([p, n])
            if distPtLine(p2, *segm) < self.D/2:
                p=projPtLine(p2, *segm)
                n = getSegmNormal(segm)[1]
                if p is not None:
                    res.append([p, n])
        return res

class Terrain:
    def __init__(self, pts):
        self.pts=pts
    def draw(self, screen):
        for i in range(1, len(self.pts)):
            pygame.draw.line(screen, (0,0,255), self.pts[i-1], self.pts[i], 2)

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    terrain=Terrain([[100, 400],[200, 300], [300, 400], [400, 390], [500, 300], [600, 380], [700, 250]])
    bike = Bike(300, 200, 0)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        dt=1/fps

        pns=bike.findPointsAndNormals(terrain)
        bike.contactPts = [x[0] for x in pns]
        bike.forces = [x[1] for x in pns]

        bike.sim(dt)


        screen.fill((255, 255, 255))
        terrain.draw(screen)
        bike.draw(screen)
        for pn in pns:
            pygame.draw.circle(screen, (255, 0, 0), pn[0], 3, 2)

        drawText(screen, f"Values = {0}", 5, 5)


        pygame.display.flip()
        timer.tick(fps)

main()