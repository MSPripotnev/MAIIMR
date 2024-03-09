import pygame.draw
from helper import *

class Mode:
    def __init__(self, robot):
        self.name="Unknown"
        self.robot=robot
        self.state="Wait"
        self.time=0
    def sim(self, dt): #аргументы - массив объектов и целевая точка
        if self.state=="Wait":
            self.state = "Running"

        self.time+=dt
        if self.time>5:
            self.state = "End"
    def draw(self, screen): #отрисовка режима на экране
        pygame.draw.rect(screen, (0,0,0), (self.time*50,0, 100, 30), 1)
        drawText(screen, self.name+" "+self.state, 5+self.time*50, 5)

class ModeGoTo (Mode):
    def __init__(self, robot, x, y):
        super().__init__(robot)
        self.name="GoTo"
        self.x=x
        self.y=y
    def sim(self, dt):
        if dist(self.robot.getPos(), (self.x, self.y))<10:
            self.state="End"
            self.robot.vRot=0
            self.robot.vLin=0
            return
        else:
            self.state="Running"

        self.robot.goto(self.x, self.y)
        self.time += dt

    def draw(self, screen):  # отрисовка режима на экране
        super().draw(screen)
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), 3, 2)
class ModeAvoid (Mode):
    def __init__(self, robot, objs):
        super().__init__(robot)
        self.objs=objs
    def sim(self, dt):

        if any(dist(self.robot.getPos(), (o.x, o.y))<10 for o in self.objs):
            self.state="Running"
        else:
            self.state="End"
            return

        self.robot.vRot=0
        self.robot.vLin=-50
        self.time += dt
class ModeRotation (Mode):
    def __init__(self, robot, rotTime):
        super().__init__(robot)
        self.rotTime=rotTime
    def sim(self, dt):
        if self.time > self.rotTime:
            self.state = "End"
            self.robot.vRot=0
            return

        if self.state == "Wait":
            self.state = "Running"

        self.robot.vRot=1
        self.time += dt


