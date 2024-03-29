import math
import time

import numpy as np
import requests
import json


def dist(p1, p2):
    return np.linalg.norm(np.subtract(p2,p1))

def limAng(ang):
    while ang<=-math.pi: ang+=2*math.pi
    while ang>math.pi: ang-=2*math.pi
    return ang

class ControlSystem:
    def __init__(self, robotId):
        self.robotId=robotId
        self.ipAddress="127.0.0.1"
        self.port=8888

        self.x=0
        self.y=0
        self.ang=0

        self.vx=0
        self.va=0

    def control(self):
        headers = {"Accept": "array"}
        r = requests.get(f'http://{self.ipAddress}:{self.port}/?id={self.robotId}&vx={self.vx}&va={self.va}',
                         headers=headers)
        answer = r.text
        D = json.loads(answer)
        # print(D)
        self.x, self.y, self.ang = D["pose"]

        objs = D["objects"]
        goal = [400,300]
        if len(objs)>0:
            dd=[dist(o, (self.x, self.y)) for o in objs]
            i = np.argmin(dd)
            goal=objs[i]

        # goal = [400,300]
        a1=self.ang
        dx, dy=np.subtract(goal, (self.x, self.y))
        a2=math.atan2(dy, dx)
        delta=limAng(a2-a1)

        self.vx=round(0.3*dist(goal, (self.x, self.y)), 1)
        self.va=round(0.3*delta * 180/math.pi, 1)

        # self.x, self.y, self.ang = [float(v) for v in answer.split(" ")]

def main():
    cs = ControlSystem(0)
    cs1 = ControlSystem(1)
    cs2 = ControlSystem(2)
    while True:
        cs.control()
        cs1.control()
        cs2.control()
        time.sleep(0.1)
        print(f"vx={cs.vx}, va={cs.va}")

main()