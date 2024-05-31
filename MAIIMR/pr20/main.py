import sys, pygame
import numpy as np
import math

D_MAX=150

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


class Message:
    def __init__(self, x, y, r1, r2):
        self.x = x
        self.y = y
        self.r1 = r1 #robot
        self.r2 = r2 #robot
        self.v = 70
        self.sz = 5
        self.L = 0
        self.lost = False
    def getPos(self):
        return [self.x, self.y]
    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 255), self.getPos(), self.sz, 2)

    def sim(self, dt):
        d=dist(self.r1.getPos(), self.r2.getPos())
        if d>D_MAX or self.L>d or self.r1.connected!=self.r2:
            self.lost=True
            self.L=0
        u=np.subtract(self.r2.getPos(), self.r1.getPos())
        u/=d
        self.x=self.r1.x+u[0]*self.L
        self.y=self.r1.y+u[1]*self.L
        self.L+=self.v*dt

class Robot:
    def __init__(self, id, x, y):
        self.id=id
        self.x=x
        self.y=y
        self.vx=0
        self.vy=0
        self.sz=15
        self.connected=None #подсоединенный ближайший робот
    def getPos(self):
        return [self.x, self.y]
    def draw(self, screen):
        pygame.draw.circle(screen, (0,0,0), self.getPos(), self.sz, 2)
        drawText(screen, f"{self.id}", self.x+20, self.y)
    def sim(self, dt):
        self.x+=self.vx*dt
        self.y+=self.vy*dt
        if self.x<0: self.x=sz[0]
        elif self.x>sz[0]: self.x=0
        if self.y>sz[1]: self.y=0
        elif self.y<0: self.y=sz[1]

def simLinks(robots):
    for r in robots:
        r.connected=None
        robots_=[r2 for r2 in robots if r2!=r]
        dd=[dist(r.getPos(), r2.getPos()) for r2 in robots_]
        i = np.argmin(dd)
        r2=robots_[i]
        if dist(r.getPos(), r2.getPos()) < D_MAX:
            r.connected=r2

def drawLinks(screen, robots):
    for r in robots:
        if r.connected is not None:
            pygame.draw.line(screen, (255, 0, 0), r.getPos(), r.connected.getPos(),2)

def calcMatrix(robots, dMax):
    N=len(robots)
    mat=np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            d=dist(robots[i].getPos(), robots[j].getPos())
            mat[i, j] = 1 if d<dMax else 0
    return mat

def checkConnectivity(r1, r2):
    route=[]
    node=r1
    while True:
        route.append(node)
        if node==r2:
            return True, route
        if node.connected is not None and not node.connected in route:
            node=node.connected
        else: break
    return False, None

#матрица связности, разрыв связи
#хранить ближайшего робота

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    robots=[]
    for i in range(100):
        r=Robot(i, np.random.randint(50,750),np.random.randint(50,550))
        robots.append(r)

    msgs=[]

    foundRoutes=[]

    for r in robots:
        r.vx=np.random.normal(0,20)
        r.vy=np.random.normal(0,20)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    mat=calcMatrix(robots, D_MAX)
                    print(mat)
                if ev.key == pygame.K_2:
                    msg=Message(*robots[0].getPos(), robots[0], robots[1])
                    msgs.append(msg)
                if ev.key == pygame.K_3:
                    res=set()
                    for r in robots:
                        if r.connected is not None:
                            res.add(f"{r.id}, {r.connected.id}")
                    print(res)

        dt=1/fps
        for r in robots:
            r.sim(dt)
        for m in msgs:
            m.sim(dt)

        simLinks(robots)

        msgs=[m for m in msgs if not m.lost]


        i_=np.random.randint(0, len(robots)-1)
        if robots[i_].connected is not None:
            j_=robots.index(robots[i_].connected)
            msg = Message(*robots[i_].getPos(), robots[i_], robots[j_])
            msgs.append(msg)

        a = np.random.randint(0, len(robots) - 1)
        b = np.random.randint(a, len(robots))

        b, route=checkConnectivity(robots[a], robots[b])
        if b and len(route)>=2:
            pp=[r.getPos() for r in route]
            # pygame.draw.lines(screen, (190,190,0), False, pp, 5)
            print(f"Found route {pp}")
            foundRoutes.append(pp)

        screen.fill((255, 255, 255))

        for route in foundRoutes:
            pygame.draw.lines(screen, (190, 190, 0), False, route, 4)

        for r in robots:
            r.draw(screen)
        for m in msgs:
            m.draw(screen)

        drawLinks(screen, robots)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()