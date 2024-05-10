from fuzzylogic.classes import Domain, Set, Rule
from fuzzylogic.functions import R, S, triangular as T

#задание областей определения нечетких множеств
dist = Domain("Distance", 0, 100)
ang = Domain("Angle", -180, 180)

speed = Domain("Speed", 0, 10)
steer = Domain("Steer", -45, 45)

#задание термов (значений нечетких переменных)
#входные термы
dist.small = S(0, 20)
dist.big = R(15, 30)

ang.neg = S(-180, -20)
ang.zero = T(-30, 30)
ang.pos = R(20, 180)

#выходные термы
speed.small = S(0, 6)
speed.big = R(4, 10)

steer.neg = S(-45, 10)
steer.zero = T(-20, 20)
steer.pos = R(-10, 45)

#правила, связывающие входы и выходы
R1 = Rule({ (dist.small, ang.neg): speed.small})
R2 = Rule({ (dist.big, ang.neg): speed.big})
R3 = Rule({ (dist.small, ang.zero): speed.small})
R4 = Rule({ (dist.big, ang.zero): speed.big})
R5 = Rule({ (dist.small, ang.pos): speed.small})
R6 = Rule({ (dist.big, ang.pos): speed.big})

rr = [R1, R2, R3, R4, R5, R6]

rules = sum(rr) #система нечеткого логического вывода

vals = {dist: 45, ang: 0}
print( [r(vals) for r in rr], " => ", rules(vals) )

#TODO: запустить на Python 3.8
#TODO: добавить набор правил для руления
