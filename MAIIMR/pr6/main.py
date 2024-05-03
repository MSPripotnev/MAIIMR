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

def getRouteLen(p0, pts, inds):
    L = 0
    for i in range(1, len(inds)):
        p1, p2 = pts[inds[i - 1]], pts[inds[i]]
        L += dist(p1, p2)
    return L + dist(p0, pts[inds[0]])
def findBestRouteRandom(p0, pts):
    LBest=100500
    inds=None
    for i in range(1000):
        inds2=list(range(len(pts)))
        np.random.shuffle(inds2)
        L=getRouteLen(p0, pts, inds2)
        if L<LBest:
            LBest=L
            inds=inds2
    return inds, LBest

def findBestRouteFullSearch(p0, pts):
    routeBest=None
    LBest=100500
    import itertools
    z = itertools.permutations(list(range(len(pts))))
    i=0
    for ii in z:
        if i% 100000==0: print(i)
        L = getRouteLen(p0, pts, ii)
        if L<LBest:
            LBest=L
            routeBest=ii
        i+=1

    return routeBest, LBest


class Creature:
    def __init__(self, inds):
        self.inds=inds
        self.fitness=0
    def evaluate(self, p0, pts):
        self.fitness= - getRouteLen(p0, pts, self.inds)

class GA:
    def __init__(self, numCreatures, numPoints):
        self.creatures=[]

        for i in range(numCreatures):
            inds=list(range(numPoints))
            np.random.shuffle(inds)
            self.creatures.append(Creature(inds))
    def evaluate(self, p0, pts):
        for c in self.creatures:
            c.evaluate(p0, pts)

    def selectBest(self):
        self.creatures = sorted(self.creatures, key=lambda c:-c.fitness)
        self.creatures = self.creatures[:len(self.creatures)//2]

    def crossing(self):
        i1=np.random.randint(0, len(self.creatures)-1)
        i2=np.random.randint(i1, len(self.creatures))

        AB=self.creatures[i1].inds
        CD=self.creatures[i2].inds
        N=len(AB)

        j = np.random.randint(0, N)
        A, B = AB[:j], AB[j:]
        C, D = CD[:j], CD[j:]

        AD=[*A, *D]
        CB=[*C, *B]
        I=list(range(N))

        #устранение коллизий за счет подстановок
        def fixCollisions(c, alphabet):
            for i in range(len(c)):
                v=c[i]
                if c.count(v)>1:
                    for v in alphabet: #подстановка для устранения коллизии
                        if v not in c:
                            c[i]=v
                            break

        #fixCollisions() TODO:...



def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    p0=[100, 100]
    pts=[
        [200,200],
        [200,300],
        [300,200],
        [400,250],
        [350,300],
        [400,150],
        [200,250],
        [500,500],
        [100,450]
         ]
    route=list(range(len(pts)))

    ga=GA(10, len(pts))
    ga.evaluate(p0, pts)

    indsBest, LBest=None, None

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    indsBest, LBest=findBestRouteRandom(p0, pts)
                if ev.key == pygame.K_t:
                    indsBest, LBest=findBestRouteFullSearch(p0, pts)

        dt=1/fps

        screen.fill((255, 255, 255))
        for p in pts:
            pygame.draw.circle(screen, (0,0,255), p, 3, 2)

        L=getRouteLen(p0, pts, route)
        def drawRoute(screen, p0, route, color=(0,200,200)):
            pygame.draw.circle(screen, color, p0, 3, 2)
            pygame.draw.line(screen, color, p0, pts[route[0]], 2)
            for i in range(1, len(route)):
                p1,p2=pts[route[i-1]], pts[route[i]]
                pygame.draw.line(screen, color, p1, p2, 2)

        drawRoute(screen, p0, route)

        drawText(screen, f"inds = {route}", 5, 5)
        drawText(screen, f"L = {L:.2f}", 5, 25)
        if indsBest is not None:
            drawText(screen, f"indsBest = {indsBest}", 5, 55)
            drawText(screen, f"LBest = {LBest:.2f}", 5, 75)

            drawRoute(screen, p0, indsBest, (255, 0, 0))

        pygame.display.flip()
        timer.tick(fps)

main()