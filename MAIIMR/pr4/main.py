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
        self.target=None
    def getP0(self):
        return [self.x, self.y]
    def getP1(self):
        p0=self.getP0()
        p1=np.add(p0, [self.L1*math.cos(self.a1), self.L1*math.sin(self.a1)])
        return p1
    def getP2(self):
        p1=self.getP1()
        #TODO: check (changed a2 to a1+a2)
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
    def repell(self, obj, K=0.1):
        L=dist(obj.getPos(), self.getP2())
        v=np.subtract(self.getP2(), obj.getPos())
        v/=L

        F=v*100000 / L**2
        A=np.linalg.norm(F)

        A0 = np.linalg.norm(v * 100000 / obj.R ** 2)

        print(A)

        if L<obj.R:
            F*=A0/A
        else:
            if(A<10): F*=10/A
            if(A>100): F*=100/A

        delta=F #смещение вдоль силы
        self.target = np.add(self.getP2(), delta)

        J=self.getJacobianMat()
        J_=np.linalg.inv(J)
        dang=J_@delta

        self.a1+=K*dang[0]
        self.a2+=K*dang[1]
    def repellMulti(self, obj, N=10):
        #много итераций нужно чтоб побороть нелинейность манипулятора - кусочно-линейными
        #аппроксимациями (через матрицы Якоби)
        for i in range(30):
            self.repell(obj, 0.03)


class Obj:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.R=50
    def getPos(self):
        return [self.x, self.y]
    def draw(self, screen):
        pygame.draw.circle(screen, (0,0,0), self.getPos(), self.R, 2)

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    manip=Manipulator(400, 300, 180, 120)

    pTarget=[0,0]

    obj=Obj(480, 270)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
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


        dt=1/fps

        screen.fill((255, 255, 255))
        manip.draw(screen)
        obj.draw(screen)
        # manip.a1+=0.1
        # manip.a2+=-0.05
        p=pTarget
        # if manip.target is not None:
        #     p=pTarget - np.subtract(manip.target, manip.getP2())
        manip.coordDescent(p)
        manip.repellMulti(obj)



        pygame.draw.circle(screen, (255,0,0), pTarget, 3, 2)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()