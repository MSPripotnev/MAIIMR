import math
import pygame
import numpy as np

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, s, x, y):
    plane=font.render(s, False, (0,0,0))
    screen.blit(plane, (x,y))

def limAng(ang):
    while ang<=-math.pi: ang+=2*math.pi
    while ang>math.pi: ang-=2*math.pi
    return ang

def rot(v, ang):
    s,c=np.sin(ang), np.cos(ang)
    x=v[0]*c-v[1]*s
    y=v[0]*s+v[1]*c
    return (x,y)

def rotArr(vv, ang):
    return [rot(v, ang) for v in vv]

def dist(p1, p2):
    return np.linalg.norm(np.subtract(p2,p1))