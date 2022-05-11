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
    # print(list_action_code)

    for i in range(500):
        env.render()

        o,a,done,t = env.step(list_action_code)
        if done:
            env.dict_input['Playing_current_round'] = [i for i in range(env.players.__len__())]
            break
    
    for i in range(4):
        env.render()
        o,a,done,t = env.step(list_action_code)

main()