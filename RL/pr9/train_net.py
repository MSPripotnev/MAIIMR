import random
import model
import numpy as np

with open("samples0.txt", "r") as f:
    lines=f.readlines()
    vals=np.array(  [[float(s) for s in l.split(", ")] for l in lines]   )
    inps=vals[:,:2]
    outs=vals[:,2:]

net=model.make_net()
net.compile(
    optimizer="adam",
    loss="mse",
    metrics=["mse"]
)

net.fit(inps, outs, batch_size=5, epochs=30)
net.save_weights("net.h5")