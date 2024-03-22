import re
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


class NGon: #многоугольник
    def __init__(self, pts):
        self.pts=pts
    def draw(self, screen):
        for i in range(len(self.pts)):
            pygame.draw.line(screen,(0,0,255), self.pts[i-1], self.pts[i], 2)
    def inflate(self, r):
        c=np.mean(self.pts, axis=0)
        res=[]
        for p in self.pts:
            v=np.subtract(p,c)
            L=np.linalg.norm(v)
            v=v/L*(L+r)
            res.append(c+v)
        return NGon(res)

class Edge:
    def __init__(self, n1, n2):
        self.n1=n1
        self.n2=n2
        self.w=0

class Node:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.edges=[]
    def getPos(self):
        return [self.x, self.y]
    def getWeight(self, start):
        return dist(np.array([self.x, self.y]), np.array([start.x, start.y]))
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), self.getPos(), 3, 2)
        for e in self.edges:
            pygame.draw.line(screen, (150,0,150), e.n1.getPos(), e.n2.getPos(), 1)
    def __hash__(self) -> int:
        return hash(self.x * (self.y + 10))

def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def ok_segment(A, B, objects):
    for o in objects:
        for i in range(len(o.pts)):
            C, D=o.pts[i-1], o.pts[i]
            if intersect(A, B, C, D):
                return False
    return True

class Graph:
    def __init__(self):
        self.nodes=[]
    def draw(self, screen):
        for n in self.nodes:
            n.draw(screen)
    def connectAll(self):
        for n1 in self.nodes:
            for n2 in self.nodes:
                if n1!=n2:
                    n1.edges.append(Edge(n1, n2))
    def connect(self, objects):
        for n1 in self.nodes:
            for n2 in self.nodes:
                if n1!=n2:
                    if ok_segment(n1.getPos(), n2.getPos(), objects):
                        n1.edges.append(Edge(n1, n2))

    def findBestFrontNode(self, front, dist_old):
        res = None
        min = sys.float_info.max
        for i in range(len(front)):
            n = front[i]
            d = dist_old[n]
            if (d < min):
                min = d
                res = n
            return res

    def findWay(self, Start, End):
        Dist_old = {}
        Dist_new = {}
        Dist_old[Start] = Dist_new[Start] = 0
        prev = {}
        for n in self.nodes:
            n.visited = False
            Dist_old[n] = sys.float_info.max
            if (n == Start): Dist_old[n] = 0
            Dist_new[n] = 0

        front = [Start]
        while(len(front) > 0):
            curr = self.findBestFrontNode(front, Dist_old)
            curr.visited = True
            front.remove(curr)

            for i in range(len(curr.edges)):
                next = curr.edges[i].n2
                if (next.visited):
                    continue
                if (next not in front):
                    front.append(next)

                Dist_new[next] = Dist_old[curr] + curr.getWeight(next)
                if (Dist_new[next] < Dist_old[next]):
                    Dist_old[next] = Dist_new[next]
                    prev[next] = curr

        Res = []
        if (End not in prev.keys()):
            return None

        curr = prev[End]
        Res.append(End)
        while (True):
            if (curr == Start):
                break
            Res.append(curr)
            if (End not in prev.keys()):
                return None
            curr = prev[curr]

        Res.append(Start)
        Res.reverse()

        return Res

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    graph=Graph()

    with open("robot.txt", "r") as f:
        lines = f.readlines()
        pts=[re.split(r":\s+", line)[1] for line in lines]
        ptA, ptB = [[float(s) for s in v.strip("\n").split(" ")] for v in pts]

    with open("scene.txt", "r") as f:
        lines=f.readlines()
        def parseObj(s):
            pairs=re.split(r";\s+", s)
            return [[float(s) for s in pair.split(" ")] for pair in pairs]
        vals=[parseObj(line) for line in lines]
        objs=[NGon(v) for v in vals]

    R=30
    obstacles=[]
    for o in objs:
        o2=o.inflate(R)
        obstacles.append(o2)
        for p in o2.pts:
            graph.nodes.append(Node(*p))

    nStart = Node(*ptA)
    nEnd = Node(*ptB)
    graph.nodes.append(nStart)
    graph.nodes.append(nEnd)
    graph.connect(obstacles)
    way = graph.findWay(nStart, nEnd)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")
        dt=1/fps
        screen.fill((255, 255, 255))

        for p in [ptA,ptB]:
            pygame.draw.circle(screen, (255,255,0), p, 5, 2)

        for o in objs:
            o.draw(screen)
            o2=o.inflate(R)
            o2.draw(screen)

        for i in range(0, len(way)-1):
            pygame.draw.line(screen, (150,0,0), (way[i].x, way[i].y), (way[i+1].x, way[i+1].y), 10)

        graph.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()