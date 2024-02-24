import pygame
import sys
import math
import numpy as np

hyst_g = math.pi/10
### Q-learning
# Q(s,a) = sum(gamma^t[t] * R[t], t, 0, +oo)
# gamma = 0.7
# gamma^t[0] = 1, gamma^t[1]=0.7, gamma^t[2] = 0.49, ...
# Q = 1*73 + 0.7 * 20 + 0.49 * 37 + ...

class History:
    def __init__(self) -> None:
        self.records = []

    def add(self, cart):
        S = 0 if cart.gamma < -hyst_g else 2 if cart.gamma > hyst_g else 1
        a = 0 if cart.a < -1 else 2 if cart.a > 1 else 1
        r = -abs(cart.gamma)
        self.records.append([len(self.records),S,a,r])

    def calcQi(self, i0, G = 0.7, N_max = 10):
        return sum(self.records[i][3] * math.pow(G, i-i0) for i in range(i0, min(len(self.records), N_max)))
        #for i in range(i0, min(len(self.records), N_max)):
        #    t = i - i0
        #    Qi += self.records[i][3] * math.pow(G, t)
        #return Qi

    def calcQ(self, indS, indA):
        records = [r for r in self.records if r[1] == indS and r[2] == indA]
        qq = [self.calcQi(r[0], 0.7, 10) for r in records]
        return 0 if len(qq) == 0 else np.mean(qq)

    def calcSATable(self):
        res = np.zeros((3,3))
        for iS in range(3):
            for iA in range(3):
                res[iS, iA] = self.calcQ(iS, iA)
        return res

class Quality:
    def __init__(self) -> None:
        pass

class Cart:
    def __init__(self):
        self.x=0
        self.v=0
        self.a=0
        self.gamma=0.01
    def draw(self, screen, sz):
        p0=(sz[0]/2+self.x, sz[1]/2)
        w,h = 100, 30
        bb = [p0[0]-w/2, p0[1]-h/2, w, h]
        pygame.draw.rect(screen,(0,0,255), bb, 2)
        pygame.draw.circle(screen,(0,0,255),(p0[0]-h, p0[1]+h/2), 15, 2)
        pygame.draw.circle(screen,(0,0,255),(p0[0]+h, p0[1]+h/2), 15, 2)

        L=100
        dx, dy = L * math.sin(self.gamma), - L * math.cos(self.gamma)
        p1 = p0[0], p0[1]-h/2
        p2 = p1[0]+dx, p1[1]+dy
        pygame.draw.line(screen, (0,255,0),p1,p2,10)

    def sim(self, dt):
        self.v += self.a * dt
        self.x += self.v * dt
        self.gamma += (0.01*self.gamma-0.15*self.v) * dt
        if self.gamma < -math.pi/5:
            self.gamma = -math.pi/5
        elif self.gamma > math.pi/5:
            self.gamma = math.pi/5

    def makeDesicion(self, SATable):
        S = 0 if self.gamma < -hyst_g else 2 if self.gamma > hyst_g else 1
        row = SATable[S,:]
        return np.argmax(row) # iA


def main():
    sz=(800, 600)
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    cart = Cart()
    history = History()
    fps = 30
    max_a = 10
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    cart.a = -max_a
                elif event.key == pygame.K_d:
                    cart.a = max_a
                else:
                    cart.a = 0

        screen.fill( (255,255,255) )
        pygame.draw.circle(screen,(255,0,0),(sz[0]/2, sz[1]/2), 3, 2)
        cart.sim(1/fps)
        history.add(cart)
        if len(history.records) > 200:
            SA = history.calcSATable()
            iA = cart.makeDesicion(SA)
        else:
            cart.a = history.add(cart)
            np.random.normal(0, max_a)

        cart.a = -max_a if iA == 0 else 0 if iA == 1 else max_a if iA == 2

        cart.draw(screen, sz)
        pygame.display.flip()
        timer.tick(fps)
main()
