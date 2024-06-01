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
def sigmoid(x):
  return 1 / (1 + math.exp(-x))
class Node:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.val=0
        self.valNew=0
        self.prevNodes=[]
        self.weight=0

    def calc(self):
        vv=[n.weight*n.val for n in self.prevNodes]
        s=sum(vv)
        #TODO: нормализация
        res=sigmoid(self.weight*s)
        return res

    def getPos(self):
        return [self.x, self.y]
    def draw(self, screen):
        pygame.draw.circle(screen, (0,200,0), self.getPos(), 10, 2)
        drawText(screen, f"v={self.val:.2f}", self.x, self.y-12)
        drawText(screen, f"w={self.weight:.2f}", self.x, self.y+5)
        for n in self.prevNodes:
            p1=self.getPos()
            p2=n.getPos()
            pygame.draw.line(screen, (170, 170, 170), p1, p2, 2)

def getNearestNodes(nodes, currNode, nMax):
    nodes_=[n for n in nodes if n!=currNode]
    dd=[dist(n.getPos(), currNode.getPos()) for n in nodes_]
    z=zip(nodes_, dd)
    z=sorted(z, key=lambda x: x[1])
    z=z[:min(nMax, len(nodes_))]
    return [x[0] for x in z]
def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    nodes=[]
    for i in range(10):
        n=Node(np.random.randint(50, 750), np.random.randint(50, 550))
        n.val=np.random.normal(0, 0.4)
        n.weight=np.random.normal(0, 0.4)
        nodes.append(n)

    # for i in range(len(nodes)):
    #     for j in range(i+1, len(nodes)):
    #         if np.random.rand()<0.2:
    #             nodes[i].prevNodes.append(nodes[j])

    for i in range(len(nodes)):
        nearest=getNearestNodes(nodes, nodes[i], 5)
        nodes[i].prevNodes.extend(nearest)


    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    for n in nodes:
                        n.valNew=n.calc()
                    for n in nodes:
                        n.val = n.valNew

        dt=1/fps

        screen.fill((255, 255, 255))
        for n in nodes:
            n.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()