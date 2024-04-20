import sys, pygame
import numpy as np
import math

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, s, x, y):
    surf=font.render(s, True, (0,0,0))
    screen.blit(surf, (x,y))

sz = (800, 600)
INF=1000000

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

def getRouteLen(pts, inds):
    L = 0
    for i in range(1, len(inds)):
        p1, p2 = pts[inds[i - 1]], pts[inds[i]]
        L += dist(p1, p2)
    return L
def findBestRoute(pts):
    LBest=100500
    inds=None
    for i in range(1000):
        inds2=list(range(len(pts)))
        np.random.shuffle(inds2)
        L=getRouteLen(pts, inds2)
        if L<LBest:
            LBest=L
            inds=inds2
    return inds, LBest

def calcMat(pts):
    M0=[]
    for p in pts:
        dd = [INF if p==q else dist(p,q) for q in pts]
        M0.append(dd)
    M0 = np.array(M0, dtype=int)
    return M0
def adjustMatRows(M0):
    M1=[]
    Q=0
    for row in M0:
        h=min(row)
        row2=row-h
        row2=[INF if v>INF/2 else v for v in row2]
        M1.append(row2)
        if h<INF: Q+=h
    M1 = np.array(M1, dtype=int)
    return M1, Q
def adjustMatCols(M0):
    M0_=M0.transpose()
    M1, Q=adjustMatRows(M0_)
    M1=M1.transpose()
    return M1, Q
def evaluateMat(M0):
    M1, Q1=adjustMatRows(M0)
    M2, Q2=adjustMatCols(M1)
    Q=Q1+Q2
    return Q

#TODO: запоминать какое ребро было вычеркнуто из колонок и строк матрицы
def getSubmatIJ(M, i, j): #получение подматрицы для маршрутов, содержащих ребро i,j
    res=[]
    for y in range(M.shape[0]):
        DEL1 = y==i
        row=[]
        for x in range(M.shape[1]):
            DEL2 = x==j
            v=INF if (DEL1 or DEL2) else M[y, x]
            row.append(v)
        res.append(row)
    res=np.array(res,dtype=int)
    return res

def getSubmatIJ_(M, i, j): #получение подматрицы для маршрутов, не содержащих ребро i,j
    res=np.array(M)
    res[i, j] = INF
    return res

def selectBestEdge(M): #выбор ребра для разбиения
    n=M.shape[0]
    bestIJ=None
    deltaQBest=0
    for i in range(n):
        for j in range(n):
            v=M[i,j]
            if v==INF: continue
            M_ij = getSubmatIJ(M, i, j)
            M_ij_ = getSubmatIJ_(M, i, j)
            Q=evaluateMat(M_ij) #предпочтительная половина разбиения
            Q_=evaluateMat(M_ij_) #остаточная половина разбиения
            if Q>Q_:
                delta=Q-Q_
                if delta>deltaQBest:
                    bestIJ = (i, j)
                    deltaQBest=deltaQBest
    return bestIJ, deltaQBest


class Node:
    def __init__(self, M):
        self.M=M
        self.i=-1
        self.j=-1
        self.childs=[]
        self.Q=0
    def split(self):
        ij, dq=selectBestEdge(self.M)
        if ij is not None:
            (self.i, self.j)=ij
            M_ij = getSubmatIJ(self.M, self.i, self.j)
            M_ij_ = getSubmatIJ_(self.M, self.i, self.j)
            n1=Node(M_ij)
            n1.Q = evaluateMat(M_ij)  # предпочтительная половина разбиения
            n2=Node(M_ij_)
            n2.Q = evaluateMat(M_ij_)  # остаточная половина разбиения
            self.childs.append(n1)
            self.childs.append(n2)
            n1.split()
            # n2.split()

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    pts=[
        [200,200],
        [200,300],
        [300,200],
        [400,250],
        [350,300],
        [400,150],
        [200,250],
        [500,500],
        [100,450],
        [600,350],
        [300,100],
        [200,400]
         ]
    route=list(range(len(pts)))

    indsBest, LBest=None, None

    M0, M1, M2=None, None, None
    node=None
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    indsBest, LBest=findBestRoute(pts)
                if ev.key == pygame.K_i:
                    M0=calcMat(pts)
                    print(M0)
                if ev.key == pygame.K_1:
                    M1, Q1=adjustMatRows(M0)
                    print("M1 = ", M1)
                    print("Q1 = ", Q1)
                if ev.key == pygame.K_2:
                    M2, Q2=adjustMatCols(M1)
                    print("M2 = ", M2)
                    print("Q2 = ", Q2)
                if ev.key == pygame.K_3:
                    Q=evaluateMat(M0)
                    print("Q = ", Q)
                if ev.key == pygame.K_4:
                    #для примера проведем разбиение по 2 строке и 3 столбцу
                    M_23=getSubmatIJ(M2, 2, 3)
                    M_23_=getSubmatIJ_(M2, 2, 3)
                    print("M_23=", M_23)
                    print("Q_23=", evaluateMat(M_23)) #матрица, содержащая ребро 2,3
                    print("M_23_=", M_23_)
                    print("Q_23_=", evaluateMat(M_23_)) #матрица, не содержащая ребро 2,3
                if ev.key == pygame.K_5:
                    #для примера проведем разбиение по 2 строке и 3 столбцу
                    M_52=getSubmatIJ(M2, 5, 2)
                    M_52_=getSubmatIJ_(M2, 5, 2)
                    print("M_52=", M_52)
                    print("Q_52=", evaluateMat(M_52)) #матрица, содержащая ребро 5,2
                    print("M_52_=", M_52_)
                    print("Q_52_=", evaluateMat(M_52_)) #матрица, не содержащая ребро 5,2
                if ev.key == pygame.K_6:
                    ij, dq=selectBestEdge(M2)
                    print(f"ij={ij}, dq={dq}")
                if ev.key == pygame.K_7:
                    node=Node(M2)
                    node.split()
                if ev.key == pygame.K_8:
                    s=""
                    n=node
                    while True:
                        if n.i>=0 and n.j>=0:
                            s+=f"({n.i}, {n.j}), "
                            if len(n.childs)>0:
                                n=n.childs[0]
                        else: break
                    print(s)




        dt=1/fps

        screen.fill((255, 255, 255))
        for p in pts:
            pygame.draw.circle(screen, (0,0,255), p, 3, 2)

        L=getRouteLen(pts, route)
        def drawRoute(route, color=(0,200,200)):
            for i in range(1, len(route)):
                p1,p2=pts[route[i-1]], pts[route[i]]
                pygame.draw.line(screen, color, p1, p2, 2)
            for i in range(len(route)):
                drawText(screen, str(i), *pts[route[i]])

        drawRoute(route)

        drawText(screen, f"inds = {route}", 5, 5)
        drawText(screen, f"L = {L:.2f}", 5, 25)
        if indsBest is not None:
            drawText(screen, f"indsBest = {indsBest}", 5, 55)
            drawText(screen, f"LBest = {LBest:.2f}", 5, 75)

            drawRoute(indsBest, (255, 0, 0))

        pygame.display.flip()
        timer.tick(fps)

main()