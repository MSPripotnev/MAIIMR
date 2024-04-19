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


class Landmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def getPos(self):
        return (self.x, self.y)
    def draw(self, screen):
        p=self.getPos()
        pygame.draw.circle(screen, (0,150,0), p, 5, 0)
class Particle:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.q=0
    def getPos(self):
        return (self.x, self.y)
    def draw(self, screen):
        p=self.getPos()
        pygame.draw.circle(screen, (0,0,255), p, 3, 2)

class Robot:
    def __init__(self, x, y, ang):
        self.x=x
        self.y=y
        self.ang=ang
        self.L=70
        self.W=45
        self.v=0
        self.w=0
        self.particles=[]

    #1 этап
    def generateParticles(self, N):
        for i in range(N):
            p0=self.getPos()
            self.particles.append(Particle(np.random.normal(p0[0], 30), np.random.normal(p0[1], 30)))
    #2 этап
    def shiftParticles(self, dt):
        u = rot([self.v * dt, 0], self.ang)
        for p in self.particles:
            p.x+=u[0]
            p.y+=u[1]
    #3 этап
    #noisyMeasurement - растояние от робота до ориентира
    def evalParticles(self, pLandmark, noisyMeasurement):
        for p in self.particles:
            L=dist(p.getPos(), pLandmark) #гипотеза о расстоянии
            p.q=np.exp(-(L-noisyMeasurement)**2) #оценка
    #4 фильтрация частиц
    def filterParticles(self):
        lst=list(sorted(self.particles, key=lambda p:-p.q))
        lst2=[]
        for i in range(len(lst)):
            q_=1-i/(len(lst)-1)
            if np.random.rand()<q_:
                lst2.append(lst[i])
        if len(lst2)==0: lst2=[lst[0]]
        self.particles = lst2
        # self.particles=lst[:len(lst)//2]

    #5 репопуляция частиц
    def repopulateParticles(self, N):
        while len(self.particles)<N:
            i = np.random.randint(0, len(self.particles))
            p=self.particles[i]
            p2=Particle(*p.getPos())
            self.particles.append(p2)

    def getPos(self):
        return (self.x, self.y)
    def draw(self, screen):
        pp=[[-self.L/2,-self.W/2],[-self.L/2, +self.W/2],
            [+self.L/2,+self.W/2],[+self.L/2, -self.W/2]]
        pp=np.add(rotArr(pp,self.ang),  [self.x, self.y])
        pygame.draw.lines(screen, (0,0,0), True, pp, 2 )
        for p in self.particles:
            p.draw(screen)
    def sim(self, dt):
        u=rot([self.v*dt, 0], self.ang)
        self.x+=u[0]
        self.y+=u[1]
        self.ang+=self.w*dt

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    r=Robot(200, 300, 1)
    landmark=Landmark(400, 100)
    NParticles=50

    ind=0
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")
                if ev.key == pygame.K_w:
                    r.v=50
                if ev.key == pygame.K_s:
                    r.v=0
                if ev.key == pygame.K_d:
                    r.w=1
                if ev.key == pygame.K_a:
                    r.w=-1
                if ev.key == pygame.K_f:
                    r.generateParticles(NParticles)

        dt=1/fps

        r.sim(dt)

        if ind%10==0 and len(r.particles)>0:
            r.shiftParticles(dt)
            err=20
            measurment=dist(landmark.getPos(), r.getPos()) + np.random.normal(0, err)
            r.evalParticles(landmark.getPos(), measurment)
            r.filterParticles()
            r.repopulateParticles(NParticles)

        screen.fill((255, 255, 255))
        r.draw(screen)
        landmark.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)
        ind+=1

main()