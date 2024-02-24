import pygame
import sys
import numpy as np

sz=(800,600)
p0 = np.array(sz)/2 #центр экрана
scale=sz[1]/5 #масштаб для точек лидара, чтоб уместить их на экране

def tr(p):
    return np.array(p)*scale + p0

pts=[] #точки с лидара

def render():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()

    fps = 20

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        screen.fill( (255,255,255) )
        for p in pts:
            pygame.draw.circle(screen, (255,0,0), tr(p), 3)
            print(tr(p))

        pygame.draw.circle(screen, (0,0,0), p0, 5)

        pygame.display.flip()
        timer.tick(fps)
