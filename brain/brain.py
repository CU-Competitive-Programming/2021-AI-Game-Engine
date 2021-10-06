import json
import os
import sys
import time
import socket
import math

import numpy as np

# this is my first attempt at making a neural net so im going to try and comment for my sake


class Brain:
    def __init__(self, il, h1, o, h2=0, h3=0):
        self.last = h1
        # hidden layer setup, +1 for bias layer ~~ shape(len(il), h1 + 1)
        self.hlayer1 = np.array([(2 * np.random.rand(h1 + 1) - 1)
                                for i in range(il)])

        # starting the big network fun by putting all the layers into one big array
        self.network = [self.hlayer1]

        if h2 > 0:
            # ~~ shape(h1, h2 + 1)
            self.hlayer2 = np.array([(2 * np.random.rand(h2 + 1) - 1)
                                    for i in range(h1)])
            self.network.append(self.hlayer2)
            self.last = h2
        if h3 > 0:
            # ~~ shape(h2, h3 + 1)
            self.hlayer3 = np.array([(2 * np.random.rand(h3 + 1) - 1)
                                    for i in range(h2)])
            self.network.append(self.hlayer3)
            self.last = h3

        self.output = np.array([(2 * np.random.rand(self.last + 1) - 1)
                                for i in range(o)])  # output layer ~~ shape(o, self.last + 1)
        self.network.append(self.output)
        # print(self.network)

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
                # get the value from the activation function
                activated = self.activate(node, inputs)
                sig = self.sigmoid(activated)  # sigmoid these hoes
                ninputs.append(sig)  # add to new inputs
            inputs = ninputs
        return inputs.index(np.max(inputs))

    def activate(self, weights, inputs):
        activation = weights[-1]  # the last number is reserved for the bias
        for i in range(len(weights) - 1):
            # multiplying all the weights to the inputs
            activation += weights[i] * inputs[i]
        return activation
