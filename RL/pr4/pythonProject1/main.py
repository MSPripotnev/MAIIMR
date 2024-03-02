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
    k = (((B[0] - A[0]) * (pt[0] - A[0]) + (B[1] - A[1]) * (pt[1] - A[1])) /
         ((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2))
    if k<0: return [*A]
    if k>1: return [*B]
    x = A[0] + (B[0] - A[0]) * k
    y = A[1] + (B[1] - A[1]) * k
    return [x,y]

def getNearestPathPt(pt, path):
    qq=[getNearestSegmPt(pt, path[i-1], path[i]) for i in range(1, len(path))]
    dd=[dist(pt, q) for q in qq]
    i = np.argmin(dd)
    return qq[i]

def calcTrajErr(traj, path): #MSE
    res, cnt = 0, 0
    for p in traj:
        q=getNearestPathPt(p, path)
        res+=dist(p,q)**2
        cnt+=1
    return math.sqrt(res/cnt)
class Robot:
    def __init__(self, pos, ang, L, W):
        self.pos, self.ang, self.L, self.W=pos, ang, L, W
        self.vRot=0
        self.vLin=0
        self.traj=[]
    def draw(self, screen, color=(0,0,0)):
        drawRotRect(screen, color, self.pos, self.L, self.W, self.ang)
        drawTraj(screen, self.traj, (0,0,255))
    def goto(self, posGoal, thr=10):
        L = dist(posGoal, self.pos)
        if L<thr: return False
        d = np.subtract(posGoal, self.pos)
        asimuth=math.atan2(d[1], d[0])
        delta=limAng(asimuth-self.ang)
        #многоканальное ПИД-регулирование
        self.vRot=0.8*delta
        self.vLin=min(50, 0.5*L)
        return True

    def forecast(self, vLin, vRot, dt, nSteps):
        res=[]
        r=Robot(self.pos, self.ang, self.L, self.W) #копия робота
        for i in range(nSteps):
            r.vLin=vLin
            r.vRot=vRot
            r.sim(dt)
            tmp=Robot(r.pos, r.ang, r.L, r.W) #копия робота
            res.append(tmp)
        return res

    #model predictive control
    def gotoMPC(self, dt, nSteps, path, posGoal, thr=10):
        L = dist(posGoal, self.pos)
        if L < thr: return False

        #один из возможных подходов к прогнозу: 1
        #(1 - дискретные детерминированные варианты, 2 - непрерывные варианты, 3 - случайные варианты)
        actions=[[50, -2],[50, -1],[50, 0],[50, 1],[50, 2]]
        errors=[]
        for a in actions:
            #промежуточные прогнозы положения робота
            ff = self.forecast(*a, dt, nSteps)
            #ошибки отклонения от маршрута длявсех промежуточных прогнозов
            ee = [dist(f.pos, getNearestPathPt(f.pos, path)) for f in ff]
            #учет ошибки до текущей точки маршрута добавить
            eAvg=np.mean(ee)
            eNode=dist(ff[-1].pos, posGoal)
            errors.append(eAvg+eNode)
        i=np.argmin(errors)
        self.vLin, self.vRot = actions[i]

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

    path=[[100, 300], [500, 400], [600, 500], ]
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
        def control(r):
            # return r.goto(path[indPt])
            return r.gotoMPC(dt, nSteps=15, path=path, posGoal=path[indPt], thr=50)

        L=dist(r.pos, path[-1])
        if L<10:
            r.vLin, r.vRot = 0, 0
        else:
            if indPt<len(path) and not control(r):
                indPt+=1
                if indPt>=len(path):
                    r.vLin, r.vRot=0,0

        r.sim(dt)

        vRot=np.random.normal(0, 2)
        ff=r.forecast(50, vRot, dt, 15)

        screen.fill((255, 255, 255))
        r.draw(screen)

        for p in r.traj:
            q=getNearestPathPt(p, path)
            pygame.draw.circle(screen, (255,0,0), q, 3, 1)

        for f in ff:
            f.draw(screen, (0,255,0))

        drawTraj(screen, path, (0, 150, 0))

        drawText(screen, f"MSE = {calcTrajErr(r.traj, path):.2f}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()