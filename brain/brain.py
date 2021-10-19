import math
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T
import numpy as np
from collections import namedtuple, deque
import random

# this is my first attempt at making a neural net so im going to try and comment for my sake
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using {} device".format(device))

# https://www.analyticsvidhya.com/blog/2019/04/introduction-deep-q-learning-python/
# https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
# https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html
# https://github.com/nevenp/dqn_flappy_bird/blob/master/dqn.py
# Alright, time for the rewrite
# This is going to be the structure for a multi-agent deep q learning neural net
# Now that is a mouthful but it just means that each agent type shares a brain
# And the brain learns off of every agent in the field simutaniously
# I might have to change this because of speed, but that will be minor


class Brain(nn.Module):
    def __init__(self):
        super(Brain, self).__init__()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(10, 6),
            nn.ReLU(),
            nn.Linear(6, 6),
            nn.ReLU(),
            nn.Linear(6, 2)
        )

    def forward(self, x):
        logits = self.linear_relu_stack(x)
        return logits


b = Brain().to(device)
X = torch.rand(1, 10, device=device)
logits = b(X)
pred_probab = nn.Softmax(dim=1)(logits)
y_pred = pred_probab.argmax(1)
print(f"Predicted class: {y_pred[0]}")
