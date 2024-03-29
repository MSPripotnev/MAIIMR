#S. Diane, 2024
import math
import time

import pygame
import sys
import numpy as np
from helper import *
from http_server import MyHTTPServer, HTTPError, Response
from threading import Thread

WIDTH, HEIGHT=800, 600

class Obj:
    def __init__(self, x, y, sz=15):
        self.x=x
        self.y=y
        self.sz=sz
        self.color=(0,0,255)
        self.detectionFlags=[] #факт обнаружения разными роботами
    def getPos(self):
        return (self.x, self.y)
    def draw(self, screen):
        x_, y_=self.x-self.sz/2, self.y-self.sz/2
        bb=(x_, y_, self.sz, self.sz)
        w=4 if len(self.detectionFlags)>0 else 2
        pygame.draw.rect(screen, self.color, bb, w)

class Robot:
    def __init__(self, id, x, y, ang = 1, sz=70):
        self.id=id
        self.x=x
        self.y=y
        self.ang=ang
        self.sz=sz
        self.vLin=0
        self.vRot=0
        self.debugInfo=""
        v0=(sz, 0)
        self.sensors=[
            Sensor(self, *rot(v0, -45 / 180 * np.pi)),
                   Sensor(self, *v0),
           Sensor(self, *rot(v0, 45 / 180 * np.pi)) ]
        self.stats=RobotStats()
    def getPos(self):
        return (self.x, self.y)
    def getObjs(self, ind, objs):
        return [o for o in objs if self.sensors[ind].contains(*o.getPos())]
    def goto(self, x, y):
        alpha=math.atan2(y-self.y, x-self.x)
        beta=self.ang
        gamma=limAng(alpha-beta)
        self.vRot=0.3*gamma
        self.vLin=50
    def control(self, objs):
        detections=[self.getObjs(0, objs), self.getObjs(1, objs), self.getObjs(2, objs)]
        nn=[len(d) for d in detections]
        s="; ".join([str(n) for n in nn])
        rule=-1

        if self.x<0 or self.x>WIDTH or self.y<0 or self.y>HEIGHT:
            # нужно двигаться к центру
            self.goto(WIDTH/2, HEIGHT/2)
            rule=0
        elif nn[0]==0: #двигаться вперед
            self.vRot, self.vLin=0, 50
            rule=1
        elif nn[1]>=nn[0] and nn[1]>=nn[2]: #нужна остановка
            self.vRot, self.vLin=0.5, 10
            rule=2
        elif nn[0]<(nn[1]+nn[2])/2: #нужно двигаться налево
            self.vRot, self.vLin = -0.5, 50
            rule=3
        elif nn[2]<(nn[0]+nn[1])/2: #нужно двигаться направо
            self.vRot, self.vLin = 0.5, 50
            rule=4
        else: #нужно двигаться вперед
            self.vRot, self.vLin = 0, 20
            rule=5

        self.debugInfo=f"nn = {s}, r = {rule}"

    def sim(self, dt):
        v=rot((self.vLin,0), self.ang) #вектор продольного направления
        self.x+=v[0]*dt
        self.y+=v[1]*dt
        self.ang+=self.vRot*dt
        self.stats.coveredDist += np.linalg.norm(np.array(v)*dt)

    def draw(self, screen):
        x_, y_=self.x-self.sz/2, self.y-self.sz/2
        rect=[[x_, y_], [x_+self.sz, y_],
              [x_+self.sz, y_+self.sz], [x_, y_+self.sz]]
        rect_=rotArr(np.subtract(rect, self.getPos()), self.ang)
        rect_=rect_ + np.array(self.getPos())
        pygame.draw.lines(screen, (0,0,0), True, rect_, 3)
        for s in self.sensors:
            s.draw(screen)
    def contains(self, x, y):
        dx, dy=x-self.x, y-self.y
        dx, dy=rot((dx,dy), -self.ang)
        return -self.sz//2<dx<self.sz//2 and -self.sz//2<dy<self.sz//2

class Sensor:
    def __init__(self, robot, x, y, r=70):
        self.robot=robot
        self.x=x
        self.y=y
        self.r=r
    def getPos(self):
        return (self.x, self.y)
    def getGlobalPos(self):
        return np.array(self.robot.getPos()) + rot(self.getPos(), self.robot.ang)
    def contains(self, x, y):
        d=dist((x,y), self.getGlobalPos())
        return d<self.r
    def draw(self, screen):
        x,y=self.getGlobalPos()
        pygame.draw.circle(screen, (255,0,0), (x, y), self.r, 1)

def calcControlQuality(tSim, stats):
    Q=stats.nDet/30 / (tSim/60 + stats.coveredDist/1000 + stats.nColl/30 + 0.001)
    return Q

class RobotStats:
    def __init__(self):
        self.nColl = 0
        self.nDet = 0
        self.coveredDist = 0

class RobotHTTPServer (MyHTTPServer):
    def __init__(self, host, port, server_name, robots):
        super().__init__(host, port, server_name)
        self.robots=robots

    def handle_request(self, req):  # непосредственное формирование текста ответа клиенту
        if req.path == '/robots' and req.method == 'GET':
            return self.handle_get_robots(req)
        ok = True
        if "id" in req.query.keys(): robot_id = req.query["id"]
        else:ok = False
        if ok:
            return self.handle_get_robot(req, int(robot_id[0]))
        raise HTTPError(404, 'Not found 777')

    def handle_get_robot(self, req, robot_id):
        body = ""
        K=req.query.keys()
        R=self.robots[robot_id]

        accept = req.headers.get('Accept')

        vecMode="array" in accept

        if "vx" in K:
            robot_vx = req.query["vx"][0]
            R.vLin = float(robot_vx)
            if vecMode:
                body += f"RobotHTTPServer: Applying robot {robot_id} lin. velocity: {robot_vx} <br>"

        if "va" in K:
            robot_va = req.query["va"][0]
            R.vRot = float(robot_va)/180*math.pi
            if vecMode:
                body += f"RobotHTTPServer: Applying robot {robot_id} rot. velocity: {robot_va} <br>"

        if vecMode:
            body=f"{R.x:.2f} {R.y:.2f} {R.ang:.2f}"

        if 'text/html' in accept: contentType = 'text/html; charset=utf-8'
        elif vecMode: contentType = 'text/html; charset=utf-8'
        else:return Response(406, 'Not Acceptable')

        body = body.encode('utf-8')
        headers = [('Content-Type', contentType), ('Content-Length', len(body))]
        return Response(200, 'OK', headers, body)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    timer = pygame.time.Clock()

    robots = []

    def initRobots():
        nonlocal robots
        robots = [Robot(0, 130, 130), Robot(1, 330, 330), Robot(2, 130, 330)]

    initRobots()

    def startServer():
        #SERVER:
        # HOWTO: http://127.0.0.1:8888/?id=1&vx=55&va=45
        host = "127.0.0.1"
        port = 8888
        name = "127.0.0.1"  # "Robot Server"
        serv = RobotHTTPServer(host, port, name, robots)
        try: serv.serve_forever()
        except KeyboardInterrupt:
            pass
    #
    # def simple():
    #     while True:
    #         print(222)
    #         time.sleep(3)

    t = Thread(target=startServer)
    t.start()

    # r = robots[0]
    fps = 20
    tSim=0
    tInd=0

    objs=[]
    for i in range(20):
        x=np.random.randint(50, WIDTH-50)
        y=np.random.randint(50, HEIGHT-50)
        objs.append(Obj(x, y))

    logFile = None

    while True:
        if tSim>=60 and logFile is not None:
            Q=calcControlQuality(tSim, r.stats)
            logFile.write(f"Q = {Q}")
            logFile.close()
            sys.exit(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logFile.write(f"Q = {Q}")
                logFile.close()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    arr=[f"{o.x} {o.y}" for o in objs]
                    text= "; ".join(arr)
                    with open("map.txt", "w") as f:
                        f.write(text)
                if event.key == pygame.K_l:
                    tSim=0
                    tInd = 0
                    initRobots()
                    logFile= open("log.txt", "w")
                    with open("map.txt", "r") as f:
                        tokens=f.read().split("; ")
                        pts=[[float(x) for x in t.split(" ")] for t in tokens]
                        objs.clear()
                        for p in pts:
                            objs.append(Obj(*p))

        screen.fill( (255,255,255) )

        # аналитическое управление
        # r.vLin = 50
        # r.vRot = -0.2

        # экспертное управление
        for r in robots:


            # r.control(objs)
            r.sim(1/fps)

            for o in objs:
                if r.contains(*o.getPos()):
                    o.color = (255, 0, 0)
                    r.stats.nColl+=1
                else:
                    for s in r.sensors:
                        if s.contains(*o.getPos()):
                            o.color=(0,200,200)
                            if not r.id in o.detectionFlags:
                                o.detectionFlags.append(r.id)
                            break
                        else: o.color=(0,0,255)

        for r in robots:
            r.draw(screen)

        for o in objs:
            o.draw(screen)

        drawText(screen, r.debugInfo, 5, 5)
        drawText(screen, f"tSim={tSim:.2f}, d={r.stats.coveredDist:.2f}", 5, 30)

        yLast=30
        for i, r in enumerate(robots):
            drawText(screen, f"nColl[{r.id}]={r.stats.nColl}", 5, yLast:=yLast+25)
            r.stats.nDet=len([o for o in objs if i in o.detectionFlags])
            drawText(screen, f"nDet[{r.id}]={r.stats.nDet}", 5, yLast:=yLast+25)
            if logFile is not None:
                Q=calcControlQuality(tSim, r.stats)
                drawText(screen, f"Q[{r.id}]={Q:.3f}", 5, yLast:=yLast+25)

        if logFile is not None and tInd%fps==0:
            logFile.write(f"{tSim:.2f} {r.coveredDist:.2f} {r.stats.nColl} {r.stats.nDet}\n")

        pygame.display.flip()
        timer.tick(fps)
        tSim+=1/fps
        tInd+=1

main()