import time

import matplotlib.pyplot as plt
import numpy as np

# create 1000 equally spaced points between -10 and 10
X = np.linspace(-10, 10, 1000)

# calculate the y value for each element of the x vector
def F1(X):
    res = X**2 + 2*X + 2
    return res

Y = [F1(x) for x in X]
fig, ax = plt.subplots()
ax.plot(X, Y)

#пригодность
def F(x):
    return 1/F1(x)


class Creature:
    def __init__(self, x):
        self.x=x
        self.y=0
        self.score=0



def evaluate(population):
    for c in population:
        c.y=F1(c.x)
        c.score=F(c.x)


def getArrays(population):
    return [c.x for c in population], [c.y for c in population]

def selectBest(population):
    cc = sorted(population, key=lambda c: -c.score)[:2]
    return cc
def cross(best, N):
    res=[*best]
    while len(res)<N:
        a, b = np.random.rand(2)
        delta=best[1].x-best[0].x
        x0=best[0].x-delta/2
        x1=best[1].x+delta/2
        s=a+b
        a/=s
        b/=s
        c = a*x0+b*x1
        res.append(Creature(c))
    return res

#1
population=[Creature(-10+20*np.random.random()) for i in range(10)]

for i in range(10):
    evaluate(population)

    plt.plot(*getArrays(population), 'o')

    best=selectBest(population)
    plt.plot(*getArrays(best), 'x')

    newPopulation=cross(best, 10)
    evaluate(newPopulation)
    plt.plot(*getArrays(newPopulation), '*')

    population=newPopulation

    plt.show()
    print(i)
    time.sleep(1)


