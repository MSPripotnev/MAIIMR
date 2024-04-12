import math

import numpy as np

balls = ["orange", "blue",  "blue",  "blue",  "blue",
         "orange","orange","orange","orange","blue",  "blue",  "blue",  "blue",
         "orange","orange","orange","orange","orange", "orange", "blue"]

balls2 = ["orange",  "orange","orange","orange","blue"]

def calcEntropy(balls):
    s=set(balls)
    res=0
    for x in s:
        p=balls.count(x)/len(balls)
        if p<1: res+=p*math.log(2, p)
    return -res


H=calcEntropy(balls)
print(H)
H2=calcEntropy(balls2)
print(H2)

def findSplit(balls):
    HBest=calcEntropy(balls)
    iBest=0
    for i in range(1, len(balls)-1):
        H1=calcEntropy(balls[:i])
        H2=calcEntropy(balls[i:])
        if H1+H2<HBest:
            iBest=i
            HBest=H1+H2
    return iBest

i=findSplit(balls)

print(i)
print(balls[:i])
print(balls[i:])