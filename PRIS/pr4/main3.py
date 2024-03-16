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
        self.robots=[ Robot((30,30)), Robot((200,30))]
        self.objs=[ ]
        self.goal=(300,400)
        self.finishedObjs=[]
    def draw(self, screen):
        for robot in self.robots:
            robot.draw(screen)
        if len(self.objs)>0:
            for o in self.objs:
                o.draw(screen)
        for o in self.finishedObjs:
            o.draw(screen)
        pygame.draw.circle(screen, (0,0,255), self.goal, 5, 2)

    def sim(self, dt):
        for robot in self.robots:
            robot.sim(dt, self)

    def getFreeObj(self, robot):
        oo = [o for o in self.objs if o.state=="Free"]
        if len(oo)==0: return None
        dd = [dist(o.pos, robot.pos) for o in oo]
        i = np.argmin(dd)
        return oo[i]

class Mode:
    def __init__(self, robot):
        self.robot=robot
        self.state="Wait" #"Go","Take","Carry","Put"
        self.obj=None
    def control(self, world):

        if self.state == "Stop":
            o = world.getFreeObj(self.robot)
            if o is not None:
                self.obj=o
                self.state="Go"
                self.obj.state = "Taken"

        if self.state=="Wait":
            self.robot.speed=(0,0)
            if self.obj==None:
                self.obj=world.getFreeObj(self.robot)
                if self.obj is not None:
                    self.obj.state="Taken"
                    self.state = "Go"

        elif self.state=="Go":
            d=dist(self.obj.pos, self.robot.pos)
            if d<10:
                self.state="Take"
            else:
                v=np.subtract(self.obj.pos, self.robot.pos)
                L=np.linalg.norm(v)
                self.robot.speed=v/L*50
        elif self.state=="Take":
            # o=world.obj
            self.robot.attachedObj=self.obj
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
            # world.obj=None
            self.obj.state="Finised"
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
        self.state="Free" #Free, Taken, Finished
    def draw(self, screen):
        sz=20
        bb=[self.pos[0]-sz/2, self.pos[1]-sz/2, sz, sz]
        pygame.draw.rect(screen, (0,0,0), bb, 2)

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    time=0
    dtNewObj=2
    lastTimeNewObj=0

    world=World()

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        dt=1/fps

        if time-lastTimeNewObj>dtNewObj:
            world.objs.append(Obj((
                np.random.randint(50, 750),
                np.random.randint(50, 550))))
            lastTimeNewObj=time

        world.sim(dt)

        screen.fill((255, 255, 255))
        world.draw(screen)

        drawText(screen, f"Time = {time:.2f}", 5, 5)
        drawText(screen, f"Num objs = {len(world.objs)}", 5, 25)
        drawText(screen, f"Num finished = {len(world.finishedObjs)}", 5, 45)
        timePerObj=0 if len(world.finishedObjs) == 0 else time/len(world.finishedObjs)
        drawText(screen, f"Time per obj = {timePerObj:.2f}", 5, 65)

        pygame.display.flip()
        timer.tick(fps)
        time+=dt

main()