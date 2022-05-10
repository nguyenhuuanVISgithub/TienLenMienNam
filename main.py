import gym
import gym_TLMN
from pandas import read_csv
from copy import deepcopy


def main():
    env = gym.make('gym_TLMN-v0')
    env.reset()

    print([i.name for i in env.players])

    action_space = read_csv('gym_TLMN/envs/action_space.csv')
    list_action_code = list(action_space['action_code'])

    for i in range(500):
        env.render()

        o,a,done,t = env.step(list_action_code)
        if done:
            break
        


main()