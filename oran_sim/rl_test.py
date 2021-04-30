from rl import RL
import random
import numpy as np
import time


if __name__ == '__main__':
    states = ['UnderLoaded', 'NormalLoad', 'OverLoaded', 'MaxLoad']

    rl_model = RL()

    while True:
        state = states[random.randint(0, len(states) - 1)]
        action = rl_model.get_action(state)

        q = rl_model.get_q()
        print('State: {} Action: {}'.format(state, action))
        print(q)

        time.sleep(0.1)


