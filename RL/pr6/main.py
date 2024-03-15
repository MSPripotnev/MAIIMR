import sys, pygame
import numpy as np
import math

#TODO: сделать дерево кластеризации с ветвлением равным не 2 дочерним узлам, а 3, 4, ...

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


def getNodes(pts):
    res=[]
    for p in pts:
        n=Node()
        n.pt=p
        res.append(n)
    return res

#в соответствии с агломеративным подходом данная функция состыкует близкие к др др узлы
def aggregateNodes(nodes):
    res=[]
    visited=set()
    #пробегаемся по всем узлам
    for n in nodes:
        #ищем расстояния от каждого узла до других узлов
        dd=[dist(n.getCenter(), n2.getCenter()) if (n2!=n and not n2 in visited) else 100500 for n2 in nodes]
        i = np.argmin(dd)
        n2=nodes[i]

        if n in visited or n2 in visited:
            continue

        visited.add(n)
        visited.add(n2)

        nNew=Node()
        nNew.childNodes=[n, n2]
        n.parent=n2.parent=nNew
        res.append(nNew)

    #дораспределение неиспользованных узлов
    nn=[n for n in nodes if n.parent is None]
    visited=list(visited)
    for n in nn:
        dd = [dist(n.getCenter(), n2.getCenter()) for n2 in visited]
        i = np.argmin(dd)
        n2 = visited[i]
        n.parent = n2.parent
        n.parent.childNodes.append(n)

    return res

class Node:
    def __init__(self):
        self.pt=None
        self.childNodes=[]
        self.parent=None
    def getCenter(self):
        if self.pt is not None:
            return self.pt[:2]
        pp=[n.getCenter() for n in self.childNodes]
        return np.mean(pp, axis=0)
    def draw(self, screen):
        if self.pt is not None:
            pygame.draw.circle(screen, (0,0,255), self.pt[:2], 3, 2)
        else:
            c=self.getCenter()
            r=3
            x,y=c[0]-r, c[1]-r
            pygame.draw.rect(screen, (0, 0, 255), [x, y, r*2, r*2], 2)
            for n in self.childNodes:
                pygame.draw.line(screen, (0, 0, 100), c, n.getCenter())

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    pts=[] #x, y, label
    centroids=[]

    levels=[]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")
                if ev.key == pygame.K_s: #save
                    with open("pts.txt", "w") as f:
                        f.write(str(pts))
                if ev.key == pygame.K_l: #load
                    with open("pts3.txt", "r") as f:
                        pts=eval(f.read())
                if ev.key == pygame.K_1:
                    if len(levels)==0:
                        nodes=getNodes(pts)
                    else:
                        nodes = aggregateNodes(levels[-1])
                    levels.append(nodes)
                    ll=[len(l) for l in levels]
                    print(f"Level lengths = {ll}")

                if ev.key == pygame.K_2:
                    pass

                if ev.key == pygame.K_3:
                    pass

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    pts.append([*ev.pos, -1])

        dt=1/fps

        screen.fill((255, 255, 255))

        colors=[
            [255,0,0],
            [0,255,0],
            [0,0,255],
            [150,150,0],
            [0,150,150],
            [150,0,150],
            [0,0,0]
        ]

        for p in pts:
            label=p[2]
            c=colors[label]
            pygame.draw.circle(screen, c, p[:2], 5, 2)

        for p in centroids:
            pygame.draw.circle(screen, colors[p[-1]], p[:2], 5, 0)

        for l in levels:
            for n in l:
                n.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()