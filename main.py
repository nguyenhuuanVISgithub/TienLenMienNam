import gym
import gym_TLMN


def main():
    env = gym.make('gym_TLMN-v0')
    env.reset()

    print([i.name for i in env.players])

    for i in range(500):
        env.render()

        o,a,done,t = env.step(env.turn.action(env.dict_input))
        if done:
            break

        # input()

    for i in range(env.players.__len__()):
        env.render()

        o,a,done,t = env.step(env.turn.action(env.dict_input))

main()