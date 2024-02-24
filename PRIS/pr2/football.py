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
        self.collided = False

    def getPos(self):
        return np.array((self.x, self.y))
    def draw(self, screen, color):
        drawRotRect(screen, color, self.getPos(), self.L, self.W, self.ang)
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
            thr = 8
            if abs(d - d_) < thr and not self.collided:
                #поворачиваем систему координат
                alpha = math.atan2(self.normal[1], self.normal[0])
                vRot=rot((ball.vx, ball.vy), -alpha)
                vRot[0]*=-1 #отражаем x-компоненту скорости
                ball.vx, ball.vy=rot(vRot, alpha)
                self.collided=True
            elif abs(d - d_) > (thr + 5):
                self.collided = False

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

    def goToPos(self, pt):
        v = pt - self.getPos()
        aGoal = math.atan2(v[1], v[0])
        aRobot = self.ang
        dAng = limAng(aGoal - aRobot)

        k = 0.5
        self.wAng = k * dAng # П-регулятор
        self.vx = 20


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

class Team:
    def __init__(self, area, numRobots, step, isLeft = True) -> None:
        L = (numRobots-1) * step
        D = area.L / 4
        self.robots = []
        self.isLeft = isLeft
        for i in range(numRobots):
            p=(-D if isLeft else D, -L/2 + i * step)
            ang = 0 if isLeft else math.pi
            r = Robot(*area.getGlobalPt(p), ang, 45, 70)
            self.robots.append(r)
    def draw(self, screen):
        for r in self.robots:
            r.draw(screen, (170, 170, 0) if self.isLeft else (0,0,255))
    def sim(self, dt, ball):
        for r in self.robots:
            r.goToPos(ball.getPos())
            r.getNearestNormal(ball.getPos())
            r.sim(dt, ball)

class Area:
    def __init__(self, p0, W, L):
        self.p0 = p0
        self.W = W
        self.L = L

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 170, 0), (*self.p0, self.L, self.W), 2)
        p1 = (self.p0[0] + self.L / 2, self.p0[1])
        p2 = (p1[0], p1[1] + self.W)
        pygame.draw.line(screen, (0, 170, 0), p1, p2, 2)
    def isPtOutside(self, pt):
        return (pt[0] < self.p0[0] or
                pt[1] < self.p0[1] or
                pt[0] > self.p0[0] + self.L or
                pt[1] > self.p0[1] + self.W)

    def getGlobalPt(self, ptLocal): #точка относительно центра поля
        pc = np.add(self.p0, (self.L / 2, self.W / 2))
        return np.add(pc, ptLocal)

    def getLocalPt(self, ptLocal): #точка относительно центра поля
        pc = np.add(self.p0, (self.L / 2, self.W / 2))
        return np.subtract(pc, ptLocal)

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 30
    b, team1, team2 = None, None, None

    a = Area((25, 25), sz[1]-50, sz[0]-50)
    def initScene():
        nonlocal b, team1, team2
        p1 = a.getGlobalPt((200,0))
        p2 = a.getGlobalPt((-200, 0))
        team1 = Team(a, 3, 100, True)
        team2 = Team(a, 3, 100, False)
        ptRndx = np.random.randint(-10, 11)
        ptRndy = np.random.randint(-10, 11)
        b = Ball(*a.getGlobalPt((ptRndx, ptRndy)),70)
        b.vx = 0
        b.vy = 0
    initScene()
    score1, score2 = 0, 0

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    initScene()

        dt=1/fps
        b.sim(dt)
        team1.sim(dt, b)
        team2.sim(dt, b)

        screen.fill((255, 255, 255))
        team1.draw(screen)
        team2.draw(screen)
        b.draw(screen)
        a.draw(screen)

        outside = a.isPtOutside(b.getPos())
        if outside:
            ptLocal=a.getLocalPt(b.getPos())
            initScene()
            if ptLocal[0] < 0: score1 += 1
            else: score2 += 1

        drawText(screen, f"Score = {score1} : {score2}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()
