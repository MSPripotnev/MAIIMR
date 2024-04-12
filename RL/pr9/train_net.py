import random
import model
import numpy as np

net=model.make_net()
net.compile(
    optimizer="adam",
    loss="mse",
    metrics=["mse"]
)

with open("samples4.txt", "r") as f:
    lines=f.readlines()
    vals=np.array(  [[float(s) for s in l.split(", ")] for l in lines]   )

    for i in range(1):
        inds=list(range(len(vals)))
        np.random.shuffle(inds)
        vals=vals[inds]

        inps=np.array(vals[:,:2])/100 #нормализация данных
        outs=vals[:,2:]

        net.fit(inps, outs, batch_size=5, epochs=100)

    net.save_weights("net.h5")