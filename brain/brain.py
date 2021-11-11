import math
import torch
from torch import nn
#from torch._C import float64, int64
from torch.utils.data import DataLoader
from torchvision import datasets
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T
import numpy as np
from collections import namedtuple, deque
from itertools import count
import random

# this is my first attempt at making a neural net so im going to try and comment for my sake


# https://www.analyticsvidhya.com/blog/2019/04/introduction-deep-q-learning-python/
# https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html
# https://github.com/nevenp/dqn_flappy_bird/blob/master/dqn.py
# Alright, time for the rewrite
# This is going to be the structure for a multi-agent deep q learning neural net
# Now that is a mouthful but it just means that each agent type shares a brain
# And the brain learns off of every agent in the field simutaniously
# I might have to change this because of speed, but that will be minor


# https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
Transition = namedtuple(
    'Transition', ('state', 'action', 'next_state', 'reward'))

# https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html


class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class NN(nn.Module):
    def __init__(self, i, h, o):
        super(NN, self).__init__()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(i, h),
            nn.ReLU(),
            nn.Linear(h, h),
            nn.ReLU(),
            nn.Linear(h, o)
        )

    def forward(self, x):
        logits = self.linear_relu_stack(x)
        return logits


class Brain:
    def __init__(self, i, h, o):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.policy_net = NN(i, h, o).to(self.device)
        self.target_net = NN(i, h, o).to(self.device)
        self.n_actions = o
        self.BATCH_SIZE = 128
        self.GAMMA = 0.999
        self.EPS_START = 0.9
        self.EPS_END = 0.05
        self.EPS_DECAY = 200
        self.TARGET_UPDATE = 10
        self.steps_done = 0

        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.RMSprop(self.policy_net.parameters())
        self.memory = ReplayMemory(10000)

    def select_action(self, state):
        d = torch.tensor(np.array(state, dtype=np.float32))
        sample = random.random()
        eps_threshold = self.EPS_END + (self.EPS_START - self.EPS_END) * \
            math.exp(-1. * self.steps_done / self.EPS_DECAY)
        self.steps_done += 1
        if sample > eps_threshold:
            with torch.no_grad():
                # t.max(1) will return largest column value of each row.
                # second column on max result is index of where max element was
                # found, so we pick action with the larger expected reward.
                return self.policy_net(d).max(0)
        else:
            return torch.tensor([[random.randrange(self.n_actions)]], device=self.device, dtype=torch.long)

    def optimize_model(self):
        if len(self.memory) < self.BATCH_SIZE:
            return
        transitions = self.memory.sample(self.BATCH_SIZE)
        # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
        # detailed explanation). This converts batch-array of Transitions
        # to Transition of batch-arrays.
        batch = Transition(*zip(*transitions))

        # Compute a mask of non-final states and concatenate the batch elements
        # (a final state would've been the one after which simulation ended)
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                            batch.next_state)), device=self.device, dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state
                                           if s is not None])
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
        # columns of actions taken. These are the actions which would've been taken
        # for each batch state according to policy_net
        state_action_values = self.policy_net(
            state_batch).gather(1, action_batch)

        # Compute V(s_{t+1}) for all next states.
        # Expected values of actions for non_final_next_states are computed based
        # on the "older" target_net; selecting their best reward with max(1)[0].
        # This is merged based on the mask, such that we'll have either the expected
        # state value or 0 in case the state was final.
        next_state_values = torch.zeros(self.BATCH_SIZE, device=self.device)
        next_state_values[non_final_mask] = self.target_net(
            non_final_next_states).max(1)[0].detach()
        # Compute the expected Q values
        expected_state_action_values = (
            next_state_values * self.GAMMA) + reward_batch

        # Compute Huber loss
        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values,
                         expected_state_action_values.unsqueeze(1))

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()
