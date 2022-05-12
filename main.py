import gym
import gym_TLMN
from pandas import read_csv
from copy import deepcopy


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

    for i in range(4):
        env.render()

        o,a,done,t = env.step(env.turn.action(env.dict_input))

main()


# self.dict_input = {
#     'Board': self.board,
#     'Player': self.players,
#     'Playing_id': [i for i in range(amount_player)],
#     'Turn_id': self.players.index(self.turn),
#     'Turn_player_cards': [],
#     'State': [],
#     'Close_game': -1,
#     'List_all_action_code': list(data_action_space['action_code'])
# }