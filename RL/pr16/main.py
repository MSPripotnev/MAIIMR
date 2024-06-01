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

class Asteroid:
    def __init__(self, x, y, n, sz):
        self.x=x
        self.y=y
        self.vx=0
        self.vy=0
        self.n=n
        self.sz=sz
        self.isTarget=False
        self.isFinished=False
    def draw(self, screen):
        pts=[]
        r=self.sz/2
        for i in range(self.n):
            alpha=i*math.pi*2/(self.n)
            x, y=r*math.cos(alpha), r*math.sin(alpha)
            pts.append([x+self.x, y+self.y])
        color=(255, 0, 0) if self.isTarget else (0,0,0)
        pygame.draw.polygon(screen, color, pts, 2)
        m=self.getMass()
        drawText(screen, f"{m:.0f}", self.x, self.y)
        if self.isFinished:
            pygame.draw.circle(screen, color, self.getPos(), 2)
    def getPos(self):
        return [self.x, self.y]
    def getMass(self):
        r=self.sz/2
        alpha = math.pi * 2 / (self.n)
        h=r*math.sin(alpha)
        return 0.5*r*h*self.n

class Robot:
    def __init__(self, x, y, sz):
        self.x=x
        self.y=y
        self.sz=sz
        self.vx = 0
        self.vy = 0
        self.traj = []
    def getPos(self):
        return [self.x, self.y]
    def draw(self, screen):
        pygame.draw.circle(screen, (0,0,255), [self.x, self.y], self.sz/2, 2)
        if len(self.traj)>1:
            pygame.draw.lines(screen, (0,255,0), False, self.traj, 1)

def repell(asteroids, dt):
    for ast in asteroids:
        aa = [a for a in asteroids if a!=ast]
        dd=[dist(a.getPos(), ast.getPos()) for a in aa]
        i = np.argmin(dd)
        r=np.subtract(ast.getPos(), aa[i].getPos())
        r=np.array(r, dtype=np.float64)
        L=np.linalg.norm(r)
        k=0
        if L<min(ast.sz, aa[i].sz): k=20
        r/=L
        ast.vx+=k*r[0]*dt
        ast.vy+=k*r[1]*dt
    for ast in asteroids:
        ast.x+=ast.vx*dt
        ast.y+=ast.vy*dt

def control(robot, asteroids, dt):
    aa=[a for a in asteroids if not a.isFinished]

    # функционал выбора цели
    # можно менять для повышения эффективности робота
    def Q(r, a):
        d=dist(a.getPos(), r.getPos()) #10...500, ~250
        z=np.dot([a.vx, a.vx], [r.vx, r.vy]) #-2500 ... 2500, ~1250
        q=d/250 + z/1250
        return q

    dd=[dist(a.getPos(), robot.getPos()) for a in aa] #v1 dist
    # dd=[Q(a, robot) for a in aa] #v2 dist and speed

    if len(dd)==0:
        return 0

    i=np.argmin(dd)
    a=aa[i]
    a.isTarget=True

    r=np.subtract(a.getPos(), robot.getPos())
    r = np.array(r, dtype=np.float64)
    L = np.linalg.norm(r)

    dScore=0
    if L<robot.sz:
        a.isFinished=True
        dScore=a.getMass()

    k = 5 #безопасный режим движения
    if L > a.sz: k = 20 #стандартный режим движения
    r /= L
    robot.vx += k * r[0] * dt
    robot.vy += k * r[1] * dt

    if np.linalg.norm([robot.vx, robot.vy])>20:
        robot.vx *= 0.95
        robot.vy *= 0.95

    robot.x += robot.vx * dt
    robot.y += robot.vy * dt
    p=robot.getPos()
    if len(robot.traj)==0 or dist(robot.traj[-1], p)>10:
        robot.traj.append(p)
    return dScore

def main():
    np.random.seed(1)
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    simTime=0
    score=0
    FINISHED=False

    robot=Robot(100, 400, 50)

    asteroids=[]
    for i in range(10):
        ast=Asteroid(np.random.randint(50, 750), np.random.randint(50, 550),
                     np.random.randint(3, 7+1), np.random.randint(50, 100))
        ast.vx=np.random.randint(-5, 5+1)
        ast.vy=np.random.randint(-5, 5+1)
        asteroids.append(ast)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        dt=1/fps

        for ast in asteroids: ast.isTarget=False
        score += control(robot, asteroids, dt)

        repell(asteroids, dt)
        for ast in asteroids:
            if ast.x>sz[0]: ast.x=0
            if ast.y>sz[1]: ast.y=0
            if ast.x<0: ast.x=sz[0]
            if ast.y<0: ast.y=sz[1]

            ast.draw(screen)

        screen.fill((255, 255, 255))
        for ast in asteroids:
            ast.draw(screen)

        robot.draw(screen)

        drawText(screen, f"Time = {simTime:.2f}", 5, 5)
        drawText(screen, f"Score = {score:.0f}", 5, 25)
        drawText(screen, f"kEff = {score/max(1, simTime):.2f}", 5, 45)

        if not FINISHED and simTime>=60:
            print(f"Time = {simTime:.2f}, Score = {score:.0f}, kEff = {score/simTime:.2f}")
            FINISHED=True

        pygame.display.flip()
        timer.tick(fps)
        simTime+=dt

main()