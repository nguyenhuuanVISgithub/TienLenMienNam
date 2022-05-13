from ..base.player import Player
import random
from colorama import Fore, Style


class Agent(Player):
    def __init__(self, name):
        super().__init__(name)

    def action(self, dict_input):
        list_action = self.get_list_index_action(self.get_list_state(dict_input))

        print(list_action)
        action = random.choice(list_action)
        print(action)
        victory = self.check_victory(self.get_list_state(dict_input))
        if victory == 1:
            print(Fore.LIGHTYELLOW_EX + self.name + ' thắng', end='')
        elif victory == 0:
            print(Fore.LIGHTYELLOW_EX + self.name + ' thua', end='')
        elif victory == -1:
            print(Fore.LIGHTYELLOW_EX + 'Chưa hết game', end='')
        
        print(Style.RESET_ALL)

        return action