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

def drawTraj(screen, traj, color=(0,0,255)):
    for i in range(1, len(traj)):
        pygame.draw.line(screen, color, traj[i - 1], traj[i], 1)

def getNearestSegmPt(pt, A, B):

    AB = (B[0] - A[0], B[1] - A[1])
    Apt = (pt[0] - A[0], pt[1] - A[1])
    AD = AB * np.dot(AB,Apt) / np.dot(AB,AB)
    ptF = ((B[0] - A[0]) * (pt[0] - A[0]) + (B[1] - A[1]) * (pt[1] - A[1])) / ((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2)
    D[0] = A[0] + (B[0] - A[0]) * ptF
    D[1] = A[1] + (B[1] - A[1]) * ptF


class Robot:
    def __init__(self, pos, ang, L, W):
        self.pos, self.ang, self.L, self.W=pos, ang, L, W
        self.vRot=0
        self.vLin=0
        self.traj=[]
    def draw(self, screen):
        drawRotRect(screen, (0,0,0), self.pos, self.L, self.W, self.ang)
        drawTraj(screen, self.traj, (0,0,255))
    def goto(self, posGoal, thr=10):
        L = dist(posGoal, self.pos)
        if L<thr: return False
        d = np.subtract(posGoal, self.pos)
        asimuth=math.atan2(d[1], d[0])
        delta=limAng(asimuth-self.ang)
        #многоканальное ПИД-регулирование
        self.vRot=0.5*delta
        self.vLin=min(50, 0.5*L)
        return True

    def sim(self, dt):
        self.ang+=self.vRot*dt
        d=[self.vLin*dt, 0]
        self.pos=np.add(self.pos, rot(d, self.ang))
        p=[*self.pos]
        if len(self.traj)==0 or dist(p, self.traj[-1])>5:
            self.traj.append(p)
def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    path=[[100, 300], [500, 400]]
    indPt=0

    r=Robot((100,100), 1, 70, 40)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        dt=1/fps

        # r.vRot=0.5
        # r.vLin=20
        if indPt<len(path) and not r.goto(path[indPt]):
            indPt+=1
            if indPt>=len(path):
                r.vLin=0
                r.vRot=0

        r.sim(dt)

        screen.fill((255, 255, 255))
        r.draw(screen)
        drawTraj(screen, path, (0, 150, 0))

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()