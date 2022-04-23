import gym
import gym_TLMN
from copy import deepcopy

def main():
    env = gym.make('gym_TLMN-v0')
    env.reset()

    for i in range(200): 
        env.render()
        o,a,done,t = env.step(env.turn.action(deepcopy(env.state)))
        if done:
            break
        
        

if __name__ == '__main__':
    main()