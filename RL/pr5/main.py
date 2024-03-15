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

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    pts=[] #x, y, label
    centroids=[]

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
                    with open("pts1.txt", "r") as f:
                        pts=eval(f.read())
                if ev.key == pygame.K_1:
                    for i in range(3):
                        x=np.random.randint(0,sz[0])
                        y=np.random.randint(0,sz[1])
                        centroids.append([x,y, len(centroids)])

                if ev.key == pygame.K_2:
                    for p in pts:
                        dd=[dist(p, c) for c in centroids]
                        label=np.argmin(dd)
                        p[2]=label

                if ev.key == pygame.K_3:
                    for c in centroids:
                        #подмножество точек с равными метками
                        pp=[p for p in pts if p[-1]==c[-1]]
                        center=pp[0] if len(pp)==1 else np.mean(pp, axis=0)
                        c[:2]=center[:2]

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

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()