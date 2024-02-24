import display
from threading import Thread
import numpy as np
import math
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

print("Program started")

thread = Thread(target = display.render)
thread.start()

client = RemoteAPIClient()
sim = client.getObject('sim')

robot = sim.getObject("./youBot")
target = sim.getObject("./indoorPlant")

wheelJoints = [-1, -1, -1, -1]
wheelJoints[0] = sim.getObject("./rollingJoint_fl")
wheelJoints[1] = sim.getObject("./rollingJoint_rl")
wheelJoints[2] = sim.getObject("./rollingJoint_rr")
wheelJoints[3] = sim.getObject("./rollingJoint_fr")

def setMovement(forwBackVel,leftRightVel,rotVel):
    # Apply the desired wheel velocities:
    sim.setJointTargetVelocity(wheelJoints[0],-forwBackVel-leftRightVel-rotVel)
    sim.setJointTargetVelocity(wheelJoints[1],-forwBackVel+leftRightVel-rotVel)
    sim.setJointTargetVelocity(wheelJoints[2],-forwBackVel-leftRightVel+rotVel)
    sim.setJointTargetVelocity(wheelJoints[3],-forwBackVel+leftRightVel+rotVel)

def limAng(ang):
    while ang <= -math.pi: ang += 2*math.pi
    while ang > math.pi: ang -= 2*math.pi
    return ang

def setGoalMovement(p2):
    p1=sim.getObjectPosition(robot, -1)
    alpha, _, _ = sim.getObjectOrientation(robot, -1)
    beta = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
    gamma = beta-alpha
    setMovement(2, 0, 0.5 * gamma)

sim.setInt32Param(sim.intparam_idle_fps, 0)

#запуск симуляции в синхронном режиме
#sim.setStepping(True)
sim.startSimulation()
arr1=[[0,0]]
arr2=[[0,0]]
ind = 0
while (t := sim.getSimulationTime()) < 20:
    if t > 0:
        print(f"t = {t:.2f}")
    #if t<1: setMovement(2, 0, 0)
    #elif t<2: setMovement(0, 2, 0)
    #elif t<3: setMovement(-2, 0, 0)
    #elif t<4: setMovement(0, -2, 0)
    s = sim.getStringSignal("lidarInfo")
    arr=sim.unpackTable(s)
    arr=[p[:2] for p in arr]
    if ind%2==0: arr1=arr
    else: arr2=arr
    resultArr = [*arr1, *arr2]
    display.pts = resultArr

    lastArr=arr
    ind+=1

    p2=sim.getObjectPosition(target, -1)
    setGoalMovement(3, p2)


#остановка робота
setMovement(0, 0, 0)
sim.stopSimulation()

print("Program ended")