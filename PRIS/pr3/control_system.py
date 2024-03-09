import numpy as np
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
        pygame.draw.rect(screen, (0,0,0), (self.time*10,0, 100, 30), 1)
        drawText(screen, self.name+" "+self.state, 5+self.time*10, 5)

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
    def __init__(self, robot, objs, tMin):
        super().__init__(robot)
        self.name="Avoid"
        self.objs=objs
        self.tMin=tMin
    def sim(self, dt):
        dd=[dist(self.robot.getPos(), (o.x, o.y)) for o in self.objs]
        if any(d<100 for d in dd):
            self.state="Running"
        elif self.time>self.tMin:
            self.state="End"
            return

        self.robot.vRot=0
        self.robot.vLin=-50
        self.time += dt
class ModeRotation (Mode):
    def __init__(self, robot, rotTime):
        super().__init__(robot)
        self.name="Rotation"
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

#супервизорный режим для выполнения протяженных во времени действий
class SupervisorMode (Mode):
    def __init__(self, robot, objs, x, y):
        super().__init__(robot)
        self.name="Supervisor"
        self.modes=[ModeGoTo(robot, x, y), ModeAvoid(robot, objs, 3), ModeRotation(robot, 3)]
        self.childMode=None #текущий режим
        self.poses=[]
        self.modesHistory=["None"]
    def sim(self, dt):

        #переменные разрешения режимов
        allowFlags=[True, True, True]

        self.poses.append(self.robot.getPos())
        N=int(5*1/dt)
        if len(self.poses)>N:
            #определение факта зацикленности робота
            dPose=np.subtract(self.poses[-1], self.poses[-1-N])
            if np.linalg.norm(dPose)<100 and self.modesHistory[-1]!="Rotation":
                allowFlags=[False, False, True]

        found=False
        modeName="None"

        #TODO: отладить удержание режима поворота на протяжениии 3 секунд

        #уклонение от препятствий, приоритет высокий
        m=self.modes[1]
        if allowFlags[1] and not found and m.state!="End":
            m.sim(dt)
            if m.state=="Running":
                found=True
                modeName=m.name
                self.childMode=m
        else:
            m.state="Wait"
            m.time=0

        #движение к цели, приоритет средний
        m=self.modes[0]
        if allowFlags[0] and not found and m.state!="End":
            m.sim(dt)
            if m.state=="Running":
                found=True
                modeName=m.name
                self.childMode=m

        #вращение на месте, приоритет низкий
        m=self.modes[2]
        if allowFlags[2] and not found and m.state!="End":
            m.sim(dt)
            if m.state=="Running":
                found=True
                modeName=m.name
                self.childMode=m
        else:
            m.state="Wait"
            m.time=0

        # if self.childMode.state=="End" or len(self.modesHistory)==0:
        self.modesHistory.append(modeName)

        if not found:
            self.state = "End"
            self.robot.vRot=0
            return

        if self.state == "Wait":
            self.state = "Running"

        self.time += dt

    def draw(self, screen): #отрисовка режима на экране
        super().draw(screen)
        pygame.draw.rect(screen, (0,0,0), (self.time*10+20,30, 100, 30), 1)
        drawText(screen, self.childMode.name+" "+self.state, 5+self.time*10+20, 5+30)
        n=len(self.modesHistory)
        drawText(screen, "; ".join(self.modesHistory[max(0,n-5):n-1]), 5, 550)

