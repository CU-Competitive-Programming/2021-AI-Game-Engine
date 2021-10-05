import json
import os
import sys
import time
import socket
import math

import numpy as np

# this is my first attempt at making a neural net so im going to try and comment for my sake


class Brain:
    def __init__(self, h1, o, h2=0, h3=0):
        # hidden layer setup, +1 for bias layer ~~ shape(1 + len(data), h1)
        self.hlayer1 = np.array([np.random.rand(h1)
                                for i in range(len(data) + 1)])

        # starting the big network fun by putting all the layers into one big array
        self.network = np.array(self.hlayer1)

        if h2 > 0:
            # ~~ shape(1 + h1, h2)
            self.hlayer2 = np.array([np.random.rand(h2)
                                    for i in range(h1 + 1)])
            np.append(self.network, self.hlayer2)
        if h3 > 0:
            # ~~ shape(1 + h2, h3)
            self.hlayer3 = np.array([np.random.rand(h3)
                                    for i in range(h2 + 1)])
            np.append(self.network, self.hlayer3)

        self.output = np.zeros(o)  # output layer ~~ shape(o, )
        np.append(self.network, self.output)

    def sigmoid(self, num):  # sigmoid function to make values in hidden layers between 0 and 1
        return 1.0 / (1.0 + math.exp(-num))

    # this is the big function that does the whole learning process and returns the max value of the output array
    # https://machinelearningmastery.com/implement-backpropagation-algorithm-scratch-python/
    def generateOutput(self, ndata):
        # updating what the network learns on every turn since it isnt always going to be the same
        inputs = ndata
        for layer in self.network:
            ninputs = []  # new inputs for next layer
            for node in layer:
                activated = node  # TODO: do activation
                sig = self.sigmoid(activated)  # sigmoid these hoes
                ninputs.append(sig)  # add to new inputs
            inputs = ninputs
        return inputs.index(np.max(inputs))
