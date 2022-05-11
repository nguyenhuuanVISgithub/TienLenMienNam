import gym
import gym_TLMN
from pandas import read_csv
from copy import deepcopy


def main():
    env = gym.make('gym_TLMN-v0')
    env.reset()

    print([i.name for i in env.players])
    # print(list_action_code)

    for i in range(500):
        env.render()

        o,a,done,t = env.step(0)
        if done:
            env.dict_input['Playing_current_round'] = [i for i in range(env.players.__len__())]
            break
    
    for i in range(4):
        env.render()
        o,a,done,t = env.step(0)

main()