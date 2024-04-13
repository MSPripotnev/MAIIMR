import math

import numpy as np

balls = ["orange", "blue",  "blue",  "blue",  "blue",
         "orange","orange","orange","orange","blue",  "blue",  "blue",  "blue",
         "orange","orange","orange","orange","orange", "orange", "blue"]

balls2 = ["orange",  "orange","orange","orange","blue"]

def calcEntropy(balls):
    # if len(balls)==1:
    #     return 0
    s=set(balls)
    res=0
    for x in s:
        p=balls.count(x)/len(balls)
        if p<=1: res+=p*math.log(p, 2)
    return -res

H=calcEntropy(balls)
print(H)
H2=calcEntropy(balls2)
print(H2)


def findInformationGain(balls, i):
    arr1=balls[:i]
    arr2=balls[i:]
    H = calcEntropy(balls)
    H1 = calcEntropy(arr1)
    H2 = calcEntropy(arr2)
    IG = H - len(arr1)/len(balls)*H1 - len(arr2)/len(balls)*H2
    return IG

# def findSplit(balls): #НЕПРАВИЛЬНО - не учитываются численности подразбиений
#     HBest=calcEntropy(balls)
#     iBest=0
#     for i in range(1, len(balls)-1):
#         H1=calcEntropy(balls[:i])
#         H2=calcEntropy(balls[i:])
#         if H1+H2<HBest:
#             iBest=i
#             HBest=H1+H2
#     return iBest


def findSplit(balls):
    IGBest=0
    iBest=0
    for i in range(1, len(balls)):
        IG=findInformationGain(balls, i)
        if IG>IGBest:
            IGBest=IG
            iBest=i
    return iBest

i=findSplit(["orange", "blue"]) #i=1


i=findSplit(balls)

print(i)
print(balls[:i])
print(balls[i:])


class Graph:
    def __init__(self, balls):
        self.nodes=[Node(balls, 0, 0)]
        self.balls=balls
    def split(self):
        for n in self.nodes:
            n.split()
    def show(self):
        self.nodes[0].showInds()
        self.nodes[0].showElements()

    # def getLinearList(self):

    #предсказание типа элемента путем поиска релевантного диапазона на дереве
    def predict(self, x):
        return self.nodes[0].predict(x)

class Node:
    def __init__(self, array, level, globalInd):
        self.globalInd=globalInd
        self.indSplit=0
        self.array=array
        self.childNodes=[]
        self.level=level
    def split(self):
        self.indSplit=findSplit(self.array)
        if self.indSplit>0:
            n1=Node(self.array[:self.indSplit], self.level + 1, self.globalInd)
            n1.split()
            self.childNodes.append(n1)
            n2=Node(self.array[self.indSplit:], self.level + 1, self.globalInd+len(n1.array))
            n2.split()
            self.childNodes.append(n2)

    def showInds(self):
        indent="---|"*self.level
        print(f"{indent}{self.indSplit+self.globalInd}")
        for n in self.childNodes:
            n.showInds()
    def showElements(self):
        indent="---|"*self.level
        print(f"{indent}{self.array}")
        for n in self.childNodes:
            n.showElements()

    def predict(self, x):
        if x>=self.globalInd:
            if len(self.childNodes)==0:
                return self.array[0] #все элементы одинаковы - можно вернуть ллюбой
            else:
                for n in self.childNodes:
                    res=n.predict(x)
                    if res is not None:
                        return res
        return None


graph=Graph(balls)
graph.split()
graph.show()

graph2=Graph(list(reversed(balls)))
graph2.split()
graph2.show()

res1=graph.predict(7)
res2=graph2.predict(7)

print(f"Predictions: {res1}; {res2}")