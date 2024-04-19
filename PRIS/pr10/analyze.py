import numpy as np

symbols=['R', 'S', '_', 'Z', 'Ml', '_', 'L', 'Ml', '_', 'F', 'Mr', '_', 'F', 'Mr', 'C', 'F', 'Mr', 'C', 'F', 'Mr', '_', 'L', 'Ml', '_', 'L', 'Mf', '_', 'Z', 'Mf', '_', 'F', 'Mf', '_', 'Z', 'Mr', '_', 'Z', 'Mr', '_', 'Z', 'Mr', '_', 'Z', 'Mr', '_', 'R', 'Mf', '_', 'R', 'Mf', '_', 'R', 'Mr', '_', 'F', 'Mf', 'C', 'F', 'Mf', 'C', 'L', 'Mr', '_', 'F', 'Mr', '_', 'L', 'Mr', '_', 'Z', 'Mf', '_', 'F', 'Mf', '_', 'F', 'Ml', '_', 'F', 'Ml', 'C', 'F', 'Ml', 'C', 'F', 'Ml', 'C', 'F', 'Mf', '_', 'Z', 'Mf', '_', 'L', 'Mf', '_', 'F', 'Mr', '_', 'F', 'Mr', 'C', 'F', 'Mr', 'C', 'F', 'Mr', 'C', 'L', 'Mf', '_', 'Z', 'Mf', '_', 'F', 'Mf', '_', 'F', 'Mf', 'C']
symbols2=['R', 'S', '_', 'Z', 'Mf', '_', 'F', 'Ml', '_', 'F', 'Ml', '_', 'R', 'Mr', '_', 'F', 'Mr', '_', 'R', 'Mr', '_', 'R', 'Mr', '_', 'R', 'Mr', '_', 'F', 'Mr', '_', 'F', 'Ml', 'C', 'Z', 'Mr', '_', 'Z', 'Ml', '_', 'F', 'Mr', '_', 'F', 'Mr', '_', 'F', 'Mr', 'C', 'F', 'Mr', 'C', 'L', 'Ml', 'C', 'F', 'Mr', '_', 'F', 'Mr', '_', 'F', 'Mr', '_', 'F', 'Mr', 'C', 'F', 'Mr', 'C', 'L', 'Mr', '_', 'L', 'Mr', '_', 'F', 'Mr', '_', 'F', 'Mr', '_', 'Z', 'Ml', '_', 'F', 'Ml', '_', 'F', 'Ml', 'C', 'F', 'Ml', 'C', 'L', 'Mr', '_', 'L', 'Ml', '_', 'F', 'Ml', '_', 'R', 'Mr', 'C', 'R', 'Mr', '_', 'F', 'Ml', '_', 'F', 'Mr', 'C', 'L', 'Ml', '_', 'F', 'Ml', '_', 'F', 'Ml', 'C', 'R', 'Mr', '_', 'Z', 'Ml', '_', 'F', 'Mr', '_', 'F', 'Mr', '_', 'F', 'Mr', '_', 'F', 'Ml', 'C', 'Z', 'Mr', '_', 'Z', 'Mr', '_', 'R', 'Mr', '_', 'F', 'Mr', '_', 'L', 'Ml', 'C', 'Z', 'Mr', '_', 'F', 'Ml', '_', 'F', 'Ml', 'C', 'F', 'Ml', 'C', 'F', 'Mr', 'C', 'F', 'Ml', 'C', 'F', 'Ml', 'C', 'F', 'Ml', 'C', 'R', 'Ml', '_', 'F', 'Mr', '_', 'Z', 'Ml', '_', 'Z', 'Ml', '_', 'F', 'Ml', '_', 'F', 'Ml', 'C', 'F', 'Mr', 'C', 'L', 'Ml', '_', 'L', 'Ml', '_', 'F', 'Ml', '_', 'F', 'Ml', 'C', 'Z', 'Mr', '_', 'Z', 'Ml', '_', 'F', 'Mr', '_', 'R', 'Ml', 'C', 'R', 'Mr', '_', 'F', 'Mr', '_', 'L', 'Ml', '_', 'F', 'Ml', 'C', 'F', 'Mr', 'C', 'F', 'Mr', 'C', 'F', 'Mr', '_', 'Z', 'Mr', '_', 'Z', 'Mr', '_', 'F', 'Ml', '_', 'L', 'Mr', 'C', 'Z', 'Ml', '_', 'L', 'Ml', '_', 'F', 'Ml', 'C', 'F', 'Ml', 'C', 'R', 'Ml', '_', 'F', 'Mr', '_', 'L', 'Mr', 'C', 'R', 'Mr', '_', 'R', 'Mr', '_', 'F', 'Mr', '_', 'F', 'Ml', 'C', 'F', 'Mr', 'C', 'L', 'S', 'C', 'F', 'S', 'C', 'F', 'Mf', 'C', 'F', 'Mf', '_', 'F', 'Mf', 'C', 'F', 'S', 'C', 'F', 'S', 'C', 'R', 'S', 'C', 'Z', 'S', '_', 'Z', 'S', '_', 'Z', 'S', '_', 'F', 'S', '_', 'L', 'Mf', '_', 'L', 'S', '_', 'F', 'S', '_', 'F', 'Mr', '_', 'F', 'S', 'C', 'F', 'S', 'C', 'L', 'S', 'C', 'L', 'S', '_', 'Z', 'S', '_', 'Z', 'S', '_', 'Z', 'S', '_', 'R', 'S', '_', 'F', 'Mf', '_', 'R', 'Mf', '_', 'F', 'Ml', 'C', 'F', 'Mf', '_', 'F', 'S', '_', 'F', 'S', '_', 'R', 'S', '_', 'Z', 'Ml', '_', 'L', 'Mf', '_', 'F', 'Mf', '_', 'F', 'Mf', '_', 'L', 'S', '_', 'L', 'Mr', '_', 'L', 'Mf', '_', 'L', 'S', '_', 'F', 'S', '_', 'F', 'S', '_', 'F', 'S', '_']


#каковы вероятности столкновения робота при различных начальных условиях и движениях?
#например, определим вероятность столкновения при срабатывангии датчика R и движении робота вперед
#искомые символы 'R', 'Mf'

n,n1=0,0
for i in range(0, len(symbols) - 2, 3):
    if symbols[i]=='F' and symbols[i+1]=='Mf':
        n+=1
        if symbols[i+2]=='C':
            n1+=1

pCollision=n1/n
print(f"pCollision = {pCollision}")

#расчет вероятности столкновения
def calcCollisionP(sensor, action, symbols):
    n, n1 = 0, 0
    for i in range(0, len(symbols) - 2, 3):
        if symbols[i] == sensor and symbols[i + 1] == action:
            n += 1
            if symbols[i + 2] == 'C':
                n1 += 1
    if n==0: return 0
    pCollision = n1 / n
    return pCollision

#уточненный расчет вероятности столкновения с горизонтом прогноза hor
def calcCollisionP_(sensor, action, symbols, horMin, hor):
    n, n1 = 0, 0
    for i in range(0, len(symbols) - 2, 3):
        if symbols[i] == sensor and symbols[i + 1] == action:
            n += 1
            c=False
            for j in range(horMin, hor):
                if symbols[i + 2 + 3*(hor-1)] == 'C':
                    c=True
                    break
            if c:
                n1+=1

    if n==0: return 0
    pCollision = n1 / n
    return pCollision

#выбор целесообразного действия
def selectAction(sensor, actions, symbols):
    pp=[calcCollisionP(sensor, a, symbols) for a in actions]
    i = np.argmin(pp)
    return actions[i], pp
def selectAction_(sensor, actions, symbols):
    pp=[calcCollisionP_(sensor, a, symbols, 1, 4) for a in actions]
    i = np.argmin(pp)
    return actions[i], pp

# actions=['S', 'Mf', 'Ml', 'Mr']
actions=['Ml', 'Mr']
S=symbols2

# A=selectAction
A=selectAction_

a, pp=A('R',actions, S)
print(f"Sensor = R; Action = {a}; {pp}")

a2, pp2=A('L',actions, S)
print(f"Sensor = L; Action = {a2}; {pp2}")

a3, pp3=A('F',actions, S)
print(f"Sensor = F; Action = {a3}; {pp3}")

a4, pp4=A('Z',actions, S)
print(f"Sensor = Z; Action = {a4}; {pp4}")


