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

class Manipulator:
    def __init__(self, x, y, L1, L2):
        self.x=x
        self.y=y
        self.L1=L1
        self.L2=L2
        self.a1=0
        self.a2=0
    def getP0(self):
        return [self.x, self.y]
    def getP1(self):
        p0=self.getP0()
        p1=np.add(p0, [self.L1*math.cos(self.a1), self.L1*math.sin(self.a1)])
        return p1
    def getP2(self):
        p1=self.getP1()
        p2=np.add(p1, [self.L2*math.cos(self.a2), self.L2*math.sin(self.a2)])
        return p2
    def draw(self, screen):
        p0, p1, p2=self.getP0(), self.getP1(), self.getP2()
        pygame.draw.circle(screen, (0,0,0), p0,5, 2)
        pygame.draw.line(screen, (0,0,0), p0, p1,2)
        pygame.draw.line(screen, (0,0,0), p1, p2,2)
        pygame.draw.circle(screen, (0,0,255), p2,3, 2)

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


def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    manip=Manipulator(400, 300, 180, 120)

    pTarget=[0,0]

    f=open("samples.txt", "w")

    WAIT_FOR_SAMPLE=False

    net=None
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                f.close()
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")
                if ev.key == pygame.K_n:
                    import model
                    net = model.make_net()
                    net.load_weights("net.h5")
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    pTarget = ev.pos
                    WAIT_FOR_SAMPLE = True
                if ev.button == 3:
                    if net is not None:
                        inps=(np.array(np.subtract(ev.pos, manip.getP0()), dtype=np.float64))
                        inps/=100
                        y=net.predict(np.reshape(inps, (1,2)))[0]
                        manip.a1=y[0]
                        manip.a2=y[1]

        dt=1/fps

        screen.fill((255, 255, 255))
        manip.draw(screen)
        # manip.a1+=0.1
        # manip.a2+=-0.05
        if net is None:
            manip.coordDescent(pTarget)

        if WAIT_FOR_SAMPLE and dist(manip.getP2(), pTarget)<10:
            f.write(f"{pTarget[0]-manip.x}, {pTarget[1]-manip.y}, {limAng(manip.a1):.2f}, {limAng(manip.a2):.2f}\n")
            WAIT_FOR_SAMPLE=False

        pygame.draw.circle(screen, (255,0,0), pTarget, 3, 2)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()