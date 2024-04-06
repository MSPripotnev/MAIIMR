#RRT, S. Diane, 2024
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

def contains(bb, p):
    return p[0]>bb[0] and p[0]<bb[0]+bb[2] and p[1]>bb[1] and p[1]<bb[1]+bb[3]

class World:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h=x, y, w, h
        self.objs=[]
    def draw(self, screen):
        pygame.draw.rect(screen, (0,0,0), self.getBB(), 2)
        for o in self.objs:
            o.draw(screen)
    def getBB(self):
        return (self.x, self.y, self.w, self.h)
class Obj:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h=x, y, w, h
    def draw(self, screen):
        pygame.draw.rect(screen, (0,0,255), self.getBB(), 2)
    def getBB(self):
        return (self.x, self.y, self.w, self.h)
class Graph:
    def __init__(self, p0, p1):
        self.p0=p0
        self.p1=p1
        self.nodes=[]
        self.nodes.append(Node(*p0))
        self.marker=(0,0)
    def draw(self, screen):
        pygame.draw.circle(screen, (0,0,255), self.p0, 7, 2)
        pygame.draw.circle(screen, (255,0,0), self.p1, 7, 2)
        pygame.draw.circle(screen, (0,255,0), self.marker, 5, 0)
        for n in self.nodes:
            n.draw(screen)
    def step(self, world, d=30):
        x=np.random.randint(world.x, world.x+world.w)
        y=np.random.randint(world.y, world.y+world.h)
        self.marker=(x,y)
        dd=[dist(n.getPos(), self.marker) for n in self.nodes]
        i=np.argmin(dd)
        node=self.nodes[i]
        v=np.subtract(self.marker, node.getPos())
        v=np.array(v, dtype=np.float64)
        v/=np.linalg.norm(v)
        pNew=np.add(node.getPos(), d * v)
        if any( contains(o.getBB(), pNew) for o in world.objs ):
            return False
        nodeNew=Node(*pNew)
        k=dist(node.getPos(), nodeNew.getPos())
        node.edges.append(Edge(node, nodeNew, k))
        nodeNew.edgesBack.append(Edge(nodeNew, node, k))
        self.nodes.append(nodeNew)
        return True
    def findRoute(self):
        nLast=self.nodes[-1]
        res=[nLast]

        while True:
            if len(nLast.edgesBack)==0:
                return res
            try:
                nPrev=nLast.edgesBack[0].n2
                nLast=nPrev
                res.append(nLast)
            except:
                return res

class Node:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.edges=[]
        self.edgesBack=[]
    def getPos(self):
        return (self.x, self.y)
    def draw(self, screen):
        pygame.draw.circle(screen, (0,100,0), self.getPos(), 3, 2)
        for e in self.edges:
            e.draw(screen)
class Edge:
    def __init__(self, n1, n2, k):
        self.n1=n1
        self.n2=n2
        self.k=k
    def draw(self, screen):
        pygame.draw.line(screen, (0,0,100), self.n1.getPos(), self.n2.getPos())

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    w=World(50,50,700, 500)
    w.objs.append(Obj(350, 170, 170, 80))
    w.objs.append(Obj(230, 380, 170, 80))

    graph=Graph((70, 500), (730, 70))
    route=[]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    graph.step(w)
                if ev.key == pygame.K_2:
                    while True:
                        graph.step(w)
                        p=graph.nodes[-1].getPos()
                        if dist(p, graph.p1)<50:
                            break
                if ev.key == pygame.K_3:
                    route=graph.findRoute()

        dt=1/fps        

        screen.fill((255, 255, 255))
        w.draw(screen)
        graph.draw(screen)
        for i in range(1, len(route)):
            pygame.draw.line(screen, (100,100,0), route[i-1].getPos(), route[i].getPos(), 3)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()