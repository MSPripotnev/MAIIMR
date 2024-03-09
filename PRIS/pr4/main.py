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

class World:
    def __init__(self):
        self.robot=Robot((30,30))
        self.obj=Obj((100,150))
        self.goal=(300,400)
        self.finishedObjs=[]
    def draw(self, screen):
        self.robot.draw(screen)
        if self.obj is not None:
            self.obj.draw(screen)
        for o in self.finishedObjs:
            o.draw(screen)
        pygame.draw.circle(screen, (0,0,255), self.goal, 5, 2)

    def sim(self, dt):
        self.robot.sim(dt, self)

class Mode:
    def __init__(self, robot):
        self.robot=robot
        self.state="Wait" #"Go","Take","Carry","Put"
    def control(self, world):
        if self.state=="Wait":
            self.robot.speed=(0,0)
            self.state="Go"
        elif self.state=="Go":
            o=world.obj
            d=dist(o.pos, self.robot.pos)
            if d<10:
                self.state="Take"
            else:
                v=np.subtract(o.pos, self.robot.pos)
                L=np.linalg.norm(v)
                self.robot.speed=v/L*50
        elif self.state=="Take":
            o=world.obj
            self.robot.attachedObj=o
            self.state="Carry"
        elif self.state=="Carry":
            self.robot.goal=world.goal
            d = dist(self.robot.goal, self.robot.pos)
            if d < 10:
                self.state = "Put"
            else:
                v = np.subtract(self.robot.goal, self.robot.pos)
                L = np.linalg.norm(v)
                self.robot.speed = v / L * 50
        elif self.state=="Put":
            self.robot.attachedObj.pos=self.robot.goal
            world.finishedObjs.append(self.robot.attachedObj)
            world.obj=None
            self.robot.attachedObj=None
            self.robot.speed=(0,0)
            self.state = "Stop"


class Robot:
    def __init__(self, pos):
        self.pos=pos
        self.speed=(0,0)
        self.goal=(0,0)
        self.attachedObj=None
        self.mode=Mode(self)
    def draw(self, screen):
        pygame.draw.circle(screen, (0,0,0), self.pos, 40, 2)
    def sim(self, dt, world):
        self.mode.control(world)
        self.pos=np.add(self.pos, np.array(self.speed)*dt)
        if self.attachedObj is not None:
            self.attachedObj.pos=self.pos
class Obj:
    def __init__(self, pos):
        self.pos=pos
    def draw(self, screen):
        sz=20
        bb=[self.pos[0]-sz/2, self.pos[1]-sz/2, sz, sz]
        pygame.draw.rect(screen, (0,0,0), bb, 2)

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    world=World()

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        dt=1/fps
        world.sim(dt)


        if world.obj==None:
            world.obj=Obj((
                np.random.randint(50,100),
                np.random.randint(50,100)))
            world.robot.mode.state="Wait"


        screen.fill((255, 255, 255))
        world.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()