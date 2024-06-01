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


class Bullet:
    def __init__(self, x, y, ang):
        self.x = x
        self.y = y
        self.ang = ang
        self.vx = 200
        self.L = 10
        self.exploded = False
    def getPos(self):
        return [self.x, self.y]
    def draw(self, screen):
        p0 = self.getPos()
        p1 = [-self.L/2, 0]
        p1=rot(p1, self.ang)
        p2 = [+self.L/2, 0]
        p2=rot(p2, self.ang)
        pygame.draw.line(screen, (0, 0, 0), np.add(p0, p1), np.add(p0, p2), 3)
    def sim(self, dt):
        vec=[self.vx, 0]
        vec=rot(vec, self.ang)
        self.x+=vec[0]*dt
        self.y+=vec[1]*dt

class Explosion:
    def __init__(self, x, y, rMax):
        self.x=x
        self.y=y
        self.rMax=rMax
        self.r=0
        self.exploded = False

    def getPos(self):
        return [self.x, self.y]

    def sim(self, dt):
        if not self.exploded:
            self.r+=50*dt
            if self.r>self.rMax:
                self.exploded=True

    def draw(self, screen):
        w=5*(1-self.r/self.rMax)
        w=max(1, round(w))
        pygame.draw.circle(screen, (200,200,0), self.getPos(), self.r, w)
class Tank:
    def __init__(self, id, x, y, ang):
        self.id=id
        self.x=x
        self.y=y
        self.ang=ang
        self.angGun=0
        self.L=70
        self.W=45
        self.vx=0
        self.vy=0
        self.va=0
        self.vaGun=0
        self.health=100
        self.fireDelay=1
        self.lastFireDelay=0
    def fire(self):
        self.lastFireDelay=0
        r = self.W / 2.3
        LGun = self.L / 2
        p2 = rot([r + LGun, 0], self.ang + self.angGun)
        p2=np.add(self.getPos(), p2)
        b=Bullet(*p2, self.ang + self.angGun)
        return b
    def control(self, tanks, bullets):
        tanks_=[t for t in tanks if t!=self]
        if len(tanks_)==0:
            return
        dd=[dist(t.getPos(), self.getPos()) for t in tanks_]
        i = np.argmin(dd)
        target=tanks_[i]
        dx=target.x-self.x
        dy=target.y-self.y
        angTarget=math.atan2(dy, dx)
        daGun=limAng(angTarget-(self.ang+self.angGun))
        self.vaGun=15*daGun
        if self.lastFireDelay>=self.fireDelay and abs(daGun)<0.1:
            bullets.append(self.fire())

        da=limAng(angTarget-self.ang)
        self.va=1*da

    def getPos(self):
        return [self.x, self.y]
    def draw(self, screen):
        pts=[[self.L/2, self.W/2], [self.L/2, -self.W/2], [-self.L/2, -self.W/2], [-self.L/2, self.W/2]]
        pts=rotArr(pts, self.ang)
        pts=np.add(pts, self.getPos())
        pygame.draw.polygon(screen, (0,0,0), pts, 2)
        if self.health<=0:
            pygame.draw.polygon(screen, (0, 0, 0), pts, 0)
        r=self.W/2.3
        pygame.draw.circle(screen, (0,0,0), self.getPos(), r, 2)
        LGun=self.L/2
        p0=self.getPos()
        p1=rot([r, 0], self.ang+self.angGun)
        p2=rot([r+LGun, 0], self.ang+self.angGun)
        pygame.draw.line(screen, (0,0,0), np.add(p0, p1), np.add(p0, p2), 3)
        drawText(screen, f"{self.id} ({self.health})", self.x, self.y - self.L/2 - 12)
    def sim(self, dt, allTanks):
        if self.health<=0:
            self.vx=self.vy=self.va=self.vaGun=0
        vec=[self.vx, self.vy]
        vec=rot(vec, self.ang)
        self.x+=vec[0]*dt
        self.y+=vec[1]*dt
        self.ang+=self.va*dt
        self.angGun+=self.vaGun*dt
        self.lastFireDelay+=dt

        vecMin=np.zeros(2)
        LMin=100500
        tanks_=[t for t in allTanks if t!=self]
        for t in tanks_:
            vec=np.subtract(self.getPos(), t.getPos())
            L=np.linalg.norm(vec)
            if L<LMin:
                vecMin=vec
                LMin=L
        if LMin<self.L:
            vecMin=20*vecMin/np.linalg.norm(vecMin)
            self.x+=vecMin[0]*dt
            self.y+=vecMin[1]*dt


#class Explosion
#obstacles
#tank obstacles
#чет столкновений для потери здоровья танков


def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    np.random.seed(0)

    tanks=[]
    tanksExploded=[]


    for i in range(8):
        tank = Tank(i, np.random.randint(50, 750),
                    np.random.randint(50, 550),
                    np.random.random()*math.pi*2)
        tank.vx = 20
        tank.va = -1
        tank.vaGun = -0.5
        tanks.append(tank)

    bullets=[]
    explosions=[]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    b=tanks[0].fire()
                    bullets.append(b)

        dt=1/fps
        for e in explosions:
            e.sim(dt)
        explosions = [e for e in explosions if not e.exploded]

        for t in tanks:
            t.control(tanks, bullets)
        for t in tanks:
            t.sim(dt, [*tanks, *tanksExploded])
        for b in bullets:
            b.sim(dt)
            if dist(b.getPos(), [sz[0] / 2, sz[1] / 2]) > sz[0]:
                b.exploded=True
            for t in tanks:
                if dist(t.getPos(), b.getPos())<t.W/2:
                    b.exploded = True
                    t.health=max(0, t.health-10)
                    expl=Explosion(*b.getPos(), 35)
                    explosions.append(expl)
                    break

        bullets=[b for b in bullets if not b.exploded]

        #перенос подбитых танков
        tanksExploded.extend([t for t in tanks if t.health<=0])
        tanks=[t for t in tanks if t.health>0]


        screen.fill((255, 255, 255))
        # tank.draw(screen)


        for b in bullets:
            b.draw(screen)
        for t in tanks:
            t.draw(screen)
        for t in tanksExploded:
            t.draw(screen)
        for e in explosions:
            e.draw(screen)

        drawText(screen, f"NBullets = {len(bullets)}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()