import math
import numpy as np
import pygame

def dist(p1, p2):
    return np.linalg.norm(np.subtract(p1, p2))

class Manipulator:
    def __init__(self, x, y, L1, L2):
        self.x=x
        self.y=y
        self.L1=L1
        self.L2=L2
        self.a1=0
        self.a2=0
        self.target=None
    def getP0(self):
        return [self.x, self.y]
    def getP1(self):
        p0=self.getP0()
        p1=np.add(p0, [self.L1*math.cos(self.a1), self.L1*math.sin(self.a1)])
        return p1
    def getP2(self):
        p1=self.getP1()
        p2=np.add(p1, [self.L2*math.cos(self.a1+self.a2), self.L2*math.sin(self.a1+self.a2)])
        return p2
    def draw(self, screen):
        p0, p1, p2=self.getP0(), self.getP1(), self.getP2()
        pygame.draw.circle(screen, (0,0,0), p0,5, 2)
        pygame.draw.line(screen, (0,0,0), p0, p1,2)
        pygame.draw.line(screen, (0,0,0), p1, p2,2)
        pygame.draw.circle(screen, (0,0,255), p2,3, 2)
        if self.target is not None:
            pygame.draw.circle(screen, (0,255,0), self.target,3, 2)
    def getJacobianMat(self):
        dxda1=-self.L1*math.sin(self.a1)-self.L2*math.sin(self.a1+self.a2)
        dxda2=-self.L2*math.sin(self.a1+self.a2)
        dyda1=self.L1*math.cos(self.a1)+self.L2*math.cos(self.a1+self.a2)
        dyda2=self.L2*math.cos(self.a1+self.a2)
        return np.array([[dxda1, dxda2],[dyda1, dyda2]])

    def coordDescent(self, pTarget):
        def go1(delta):
            dPrev = dist(self.getP2(), pTarget)
            while True:
                self.a1+=delta
                d=dist(self.getP2(), pTarget)
                if d>dPrev:
                    self.a1 -= delta
                    break
                dPrev=d
        def go2(delta):
            dPrev = dist(self.getP2(), pTarget)
            while True:
                self.a2+=delta
                d=dist(self.getP2(), pTarget)
                if d>dPrev:
                    self.a2 -= delta
                    break
                dPrev=d
        go1(0.01)
        go1(-0.01)
        go2(0.01)
        go2(-0.01)