import matplotlib.pyplot as plt
import numpy as np

# plt.plot([1, 2, 3], [1, 4, 9])
# plt.show()

#нечеткое значение
class Term:
    def __init__(self, name, x0, w):
        self.name=name
        self.x0=x0
        self.w=w
        self.left=False
        self.right=False
    def F(self, x):
        if self.left and x<=self.x0: return 1
        if self.right and x>=self.x0: return 1
        if x<self.x0-self.w/2: return 0
        elif x<self.x0: return -(2*self.x0 / self.w - 1) + 2/self.w*x
        elif x<self.x0+self.w/2: return (2*self.x0 / self.w + 1) - 2/self.w*x
        else: return 0
    def calc(self, x):
        self.last_input=x
        self.activation=self.F(x)
        return self.activation
    def draw(self, xmin, xmax):
        N=100
        dx=(xmax-xmin)/N
        xx=[i*dx for i in range(N)]
        yy=[self.F(x) for x in xx]
        plt.plot(xx, yy)

def calcFuzzy(x, terms, R):
    aa=[t.calc(x) for t in terms]
    #применение правил
    terms2=[terms[R[i][1]] for i in range(len(R))]
    #дефаззификация
    cc=[t.x0 for t in terms2]
    v=np.dot(aa, cc)
    return v

def main():
    t1 = Term("Small", 0, 100)
    t1.draw(0, 100)
    t2 = Term("Mid", 50, 100)
    t2.draw(0, 100)
    t3 = Term("Big", 100, 100)
    t3.draw(0, 100)
    plt.show()

    # цикл активации термов при линейном изменении входной координаты
    for x in range(100):
        a1, a2, a3 = t1.calc(x), t2.calc(x), t3.calc(x)
        print(a1, a2, a3)

    # тестовая база правил, отображающая нечеткие значения сами в себя
    R = [[0, 0], [1, 2], [2, 1]]  # при наблюдении нечеткого значения i выдать нечеткое значение j

    xx=np.arange(0, 100, 1)
    terms=[t1, t2, t3]
    yy=[calcFuzzy(x, terms, R) for x in xx]

    plt.plot(xx, yy)
    plt.show()

main()
# fig = plt.figure()
# ax = fig.add_subplot(111)
# coords=[]
# ax.plot([c[0] for c in coords],[c[1] for c in coords])
# def onclick(event):
#     ix, iy = event.xdata, event.ydata
#     global coords, ax
#     coords.append((ix, iy))
#     ax.plot([c[0] for c in coords], [c[1] for c in coords])
#     plt.show()
#
#
# cid = fig.canvas.mpl_connect('button_press_event', onclick)
# plt.show()