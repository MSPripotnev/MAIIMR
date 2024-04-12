from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

def make_net():
    model=Sequential([
        Dense(10),
        Dense(2, activation="linear") #angle1, angle2
    ])
    model.build(input_shape=[1, 2]) #x, y
    return model

