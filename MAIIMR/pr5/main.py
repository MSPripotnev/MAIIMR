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

class Object:
    def __init__(self, x, y, d):
        self.x=x
        self.y=y
        self.d=d

    def getPos(self):
        return (self.x, self.y)

    def draw(self, screen):
        pygame.draw.circle(screen, (0,0,255), self.getPos(), self.d/2)
class Robot:
    def __init__(self, x, y, ang):
        self.id=0
        self.x=x
        self.y=y
        self.ang=ang
        self.L=70
        self.W=45
        self.v=0
        self.w=0
        self.manipL=30 #длина манипулятора
    def getPos(self):
        return (self.x, self.y)
    def draw(self, screen, color=(0,0,0)):
        pp=[[-self.L/2,-self.W/2],[-self.L/2, +self.W/2],
            [+self.L/2,+self.W/2],[+self.L/2, -self.W/2]]
        pp=np.add(rotArr(pp,self.ang),  [self.x, self.y])
        pygame.draw.lines(screen, color, True, pp, 2 )

        d=self.W/4
        p1=np.add(rot([self.L/2, 0], self.ang), self.getPos())
        p2=np.add(rot([self.L/2+self.manipL, 0], self.ang), self.getPos())
        p3=np.add(rot([self.L/2+self.manipL, d], self.ang), self.getPos())
        p4=np.add(rot([self.L/2+self.manipL+d, d], self.ang), self.getPos())
        p5=np.add(rot([self.L/2+self.manipL, -d], self.ang), self.getPos())
        p6=np.add(rot([self.L/2+self.manipL+d, -d], self.ang), self.getPos())

        pygame.draw.line(screen, color, p1, p2, 2)
        pygame.draw.line(screen, color, p2, p3, 2)
        pygame.draw.line(screen, color, p3, p4, 2)
        pygame.draw.line(screen, color, p2, p5, 2)
        pygame.draw.line(screen, color, p5, p6, 2)
    def sim(self, dt):
        u=rot([self.v*dt, 0], self.ang)
        self.x+=u[0]
        self.y+=u[1]
        self.ang+=self.w*dt

def generateCofigurationSpace(sz, dx, dy, da):
    x, y, a = 0, 0, 0
    Y=[]
    i=0
    while y < sz[1]:
        x=0
        X=[]
        while x < sz[0]:
            a=0
            A=[]
            while a < math.pi*2:
                robot=Robot(x, y, a)
                robot.id=i
                i+=1
                A.append(robot)
                a+=da
            X.append(A)
            x+=dx
        Y.append(X)
        y+=dy
    return Y

def drawCofigurationSpace(screen, cs):
    for Y in cs:
        for X in Y:
            for A in X:
                A.draw(screen, (150,150,150))

def findNearestConfiguration(robot, cs):
    best=None
    dBest=100500
    for Y in cs:
        for X in Y:
            for A in X:
                d=dist(A.getPos(), robot.getPos())
                d+=abs(limAng(A.ang-robot.ang))
                if d<dBest:
                    dBest=d
                    best=A
    return best

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    robot = Robot(200, 200, 1)
    obj = Object(500, 500, 20)

    modeCS=True

    cs=generateCofigurationSpace(sz, 100, 100, math.pi / 4)

    lastInd=-1
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")
                if ev.key == pygame.K_c:
                    modeCS = not modeCS
                if ev.key == pygame.K_w:
                    robot.v=50
                if ev.key == pygame.K_s:
                    robot.v=0
                if ev.key == pygame.K_d:
                    robot.w=1
                if ev.key == pygame.K_a:
                    robot.w=-1

        dt=1/fps

        robot.sim(dt)

        screen.fill((255, 255, 255))

        if modeCS:
            drawCofigurationSpace(screen, cs)

        robot.draw(screen)

        match=findNearestConfiguration(robot, cs)
        match.draw(screen, (0,0,255))
        if match.id!=lastInd:
            lastInd=match.id
            print(match.id)

        drawText(screen, f"Test = {1}", 5, 5)

        obj.draw(screen)

        pygame.display.flip()
        timer.tick(fps)

main()