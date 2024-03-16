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
        if self.canStart():
            self.state="Running"
        self.time+=dt
        if self.time>5:
            self.state = "End"
    def draw(self, screen): #отрисовка режима на экране
        pygame.draw.rect(screen, (0,0,0), (self.time*10,0, 100, 30), 1)
        drawText(screen, self.name+" "+self.state, 5+self.time*10, 5)
    def canStart(self):# new
        return self.state!="End"

class ModeGoTo (Mode):
    def __init__(self, robot, x, y):
        super().__init__(robot)
        self.name="GoTo"
        self.x=x
        self.y=y
    def sim(self, dt):
        if self.canStart():
            self.state="Running"
        if dist(self.robot.getPos(), (self.x, self.y))<10:
            self.state="End"
            self.robot.vRot=0
            self.robot.vLin=0
            return

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
        if self.canStart():
            self.state="Running"
        elif self.time>self.tMin:
            self.state="End"
            return

        self.robot.vRot=0
        self.robot.vLin=-50
        self.time += dt

    def canStart(self): #new
        if not super().canStart(): return False
        dd = [dist(self.robot.getPos(), (o.x, o.y)) for o in self.objs]
        return any(d < 100 for d in dd)

class ModeRotation (Mode):
    def __init__(self, robot, supervisor, rotTime, rotV=1):
        super().__init__(robot)
        self.name="Rotation"
        self.rotTime=rotTime
        self.rotV=rotV
        self.supervisor=supervisor
        self.dt=None
    def sim(self, dt):
        if self.dt is None: self.dt=dt

        if self.time > self.rotTime:
            self.state = "End"
            self.robot.vRot=self.rotV
            return

        if self.state == "Wait":
            self.state = "Running"

        self.robot.vRot=1
        self.time += dt

    def canStart(self):# new
        if not super().canStart(): return False
        if self.supervisor is None or self.dt is None: return True
        N = int(5 * 1 / self.dt)
        if len(self.supervisor.poses) > N:
            # определение факта зацикленности робота
            dPose = np.subtract(self.supervisor.poses[-1], self.supervisor.poses[-1 - N])
            if np.linalg.norm(dPose) < 50:
                return True
        return False

#супервизорный режим для выполнения протяженных во времени действий
class SupervisorMode (Mode):
    def __init__(self, robot, objs, x, y):
        super().__init__(robot)
        self.name="Supervisor"

        self.MR=ModeRotation(robot, self, 3, 1)
        self.MA=ModeAvoid(robot, objs, 1.5)
        self.MG=ModeGoTo(robot, x, y)

        #new
        #0 вращение на месте, приоритет высокий, длительность большая
        #1 уклонение от препятствий, приоритет средний, длительность большая
        #2 движение к цели, приоритет низкий, длительность малая
        self.modes=[self.MR,self.MA,self.MG]

        self.defaultMode=self.MG

        self.childMode=None #текущий режим
        self.poses=[]
        self.modesHistory=["None"]

    def sim(self, dt):

        self.poses.append(self.robot.getPos())

        found=False

        m=None

        # new
        busy=self.MR.state == "Running" or self.MA.state == "Running"

        if not busy:#new
            for i in range(len(self.modes)): #new
                m=self.modes[i]
                if m.canStart():
                    found = True
                    break

        if not busy and not found: #new
            m = self.defaultMode #GoTo
            found=True

        if found and self.childMode!=m:#new
            if len(self.modesHistory)==0 or self.modesHistory[-1]!=m.name: #new
                self.modesHistory.append(m.name) #new

                for m2 in self.modes:
                    if m2.name=="GoTo": pass
                    else:
                        m2.state = "Wait"
                        m2.time = 0

                if m.name=="Rotation":
                    m.time=max(0.5, np.random.normal(1,1))
                    m.rotV=np.random.normal(0,1)

                self.childMode=m #new

        self.childMode.sim(dt) #new

        if self.state == "Wait":
            self.state = "Running"

        self.time += dt

    def draw(self, screen): #отрисовка режима на экране
        super().draw(screen)
        pygame.draw.rect(screen, (0,0,0), (self.time*10+20,30, 100, 30), 1)
        drawText(screen, self.childMode.name+" "+self.state, 5+self.time*10+20, 5+30)
        n=len(self.modesHistory)
        drawText(screen, "; ".join(self.modesHistory[max(0,n-5):n]), 5, 550) #new
        self.childMode.draw(screen) #new

