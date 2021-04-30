import numpy as np
import random


class RL():

    def __init__(self, **kwargs):
        '''
        States -> UnderLoaded, NormalLoad, OverLoaded, MaxLoad

        Actions -> ScaleDown, MaintainScale, ScaleUp, LowerMeanEMBBPacket, LowerMMTCPacketFreq

        Q[s, a] = 
                      | ScaleDown | MaintainScale | ScaleUp | LowerMeanEMBBPacket | LowerMMTCPacketFreq
        --------------|-----------|---------------|---------|---------------------|--------------------
        UnderLoaded   |           |               |         |                     |
        --------------|-----------|---------------|---------|---------------------|--------------------
        NormalLoad    |           |               |         |                     |
        --------------|-----------|---------------|---------|---------------------|--------------------
        OverLoaded    |           |               |         |                     |
        --------------|-----------|---------------|---------|---------------------|--------------------
        MaxLoad       |           |               |         |                     |
        --------------|-----------|---------------|---------|---------------------|--------------------
        '''

        self.states = ['UnderLoaded', 'NormalLoad', 'OverLoaded', 'MaxLoad']
        self.actions = ['ScaleDown', 'MaintainScale', 'ScaleUp', 'LowerMeanEMBBPacket', 'LowerMMTCPacketFreq']
        self.q = np.zeros((len(self.states), len(self.actions)))

        self.explore_chances = 0.01
        self.discount = 0.5
        self.lr = 0.1
        
        for k, v in kwargs.items():
            if k == 'alpha':
                self.lr = v
            elif k == 'discount':
                self.discount = v                
            else:
                print('Unknown argument')

    def __argmax_ahat(self, state):
        state = self.states[state]

        a_opt = {'UnderLoaded': 'ScaleDown', 
                 'NormalLoad':'MaintainScale', 
                 'OverLoaded':'ScaleUp', 
                 'MaxLoad': ['LowerMeanEMBBPacket', 'LowerMMTCPacketFreq']}

        if state != 'MaxLoad':
            ahat = a_opt[state]
        else:
            # TODO: improve this
            ahat = 'ScaleUp'

        return ahat        
        
    def __max_Q(self, state):
        opt_action_idx = np.argmax(self.q[state,:])

        return self.q[state][opt_action_idx]

    def __upt_Q(self, action, state):
        #if not self.__q_stable():
            reward = self.__policy(action, state)

            new_q_state_action = reward + self.discount * self.__max_Q(state)

            action = self.actions.index(action)

            self.q[state][action] = round(self.q[state][action] + self.lr * (new_q_state_action - self.q[state][action]), 2)

    def __policy(self, action, state):
        if self.__argmax_ahat(state) == action:
            reward = 1
        else:
            reward = -1
        
        return reward

    def __q_stable(self):
        for row in range(len(self.q[:,0])):
            if self.q[row, np.argmax(self.q[row,:])] == 0:
                return False

        return True

    def get_action(self, state):
        state_idx = self.states.index(state)

        action = self.actions[np.argmax(self.q[state_idx, :])]

        self.__upt_Q(action, state_idx)

        return action

    def get_q(self):

        return self.q



