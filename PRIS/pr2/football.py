import sys, pygame
import numpy as np
import math

sz = (800, 600)

def rot(v, ang): #функция для поворота на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def rotArr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]


def dist(p1, p2):
    return np.linalg.norm(np.subtract(p1, p2))

def drawRotRect(screen, pc, w, h, ang): #точка центра, ширина высота прямоуг и угол поворота прямогуольника
    pts = [
        [- w/2, - h/2],
        [+ w/2, - h/2],
        [+ w/2, + h/2],
        [- w/2, + h/2],
    ]
    pts = rotArr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, (0, 0, 255), pts, 2)
    # for i in range(len(pts)):
    #    pygame.draw.line(screen, (0,0,255),pts[i-1], pts[i], 2)

class Robot:
    def __init__(self, x, y, ang, W, L):
        #координаты
        self.x = x
        self.y = y
        self.ang = ang
        #скорости
        self.vx = 0
        self.vy = 0
        self.wAng = 0
        #габариты
        self.W = W
        self.L = L
        self.normal = None

    def getPos(self):
        return np.array((self.x, self.y))
    def draw(self, screen):
        drawRotRect(screen, self.getPos(),self.L, self.W, self.ang)
        if self.normal is not None:
            pc=self.getPos()
            pygame.draw.line(screen, (255,0,0), pc, pc+self.normal, 2)
    def sim(self, dt, ball):
        v=rot((self.vx,0), self.ang)
        self.x+=v[0]*dt
        self.y+=v[1]*dt
        self.ang+=self.wAng*dt

        if self.normal is not None:
            d=dist(self.getPos(), ball.getPos())
            d_=np.linalg.norm(self.normal)+ball.D/2
            thr = 5
            if abs(d - d_)<thr and not ball.collided:
                #поворачиваем систему координат
                alpha = math.atan2(self.normal[1], self.normal[0])
                vRot=rot((ball.vx, ball.vy), -alpha)
                vRot[0]*=-1 #отражаем x-компоненту скорости
                ball.vx, ball.vy=rot(vRot, alpha)
                ball.collided=True
            elif abs(d - d_)>2*thr:
                ball.collided = False

    def getNearestNormal(self, ballPt):
        pts = [
            [-self.L / 2, -self.W / 2],
            [+self.L / 2, -self.W / 2],
            [+self.L / 2, +self.W / 2],
            [-self.L / 2, +self.W / 2]
        ]
        pts=rotArr(pts, self.ang)
        vv = []
        for i in range(len(pts)):
            vv.append(np.mean((pts[i-1], pts[i]), axis= 0))
        vBall = np.subtract(ballPt, self.getPos())
        dotProducts = [np.dot(v, vBall) for v in vv]
        i = np.argmax(dotProducts)
        self.normal = vv[i]
        return vv[i]

class Ball:
    def __init__(self, x, y, D):
        #координаты
        self.x = x
        self.y = y
        #скорости
        self.vx = 0
        self.vy = 0
        #габариты
        self.D = D
        self.collided=False

    def getPos(self):
        return np.array((self.x,self.y))
    def draw(self, screen):
        pygame.draw.circle(screen, (0,170,0), self.getPos(),self.D/2, 2)
    def sim(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    r = Robot(350, 350, 1, 45, 60)
    r.vx = 50
    r.wAng = -1
    b = Ball(200,200,70)
    b.vx = 30
    b.vy = 20

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)

        dt=1/fps
        r.sim(dt, b)
        b.sim(dt)
        n=r.getNearestNormal(b.getPos())

        screen.fill((255, 255, 255))
        r.draw(screen)
        b.draw(screen)
        pygame.display.flip()
        timer.tick(fps)

main()
