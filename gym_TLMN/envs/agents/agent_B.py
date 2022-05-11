from ..base.player import Player
import random
from colorama import Fore, Style


class Agent(Player):
    def __init__(self, name):
        super().__init__(name)

    def action(self, dict_input):
        list_index_action = self.get_list_index_action(dict_input['State'], dict_input['List_all_action_code'])

        print(list_index_action)
        return random.choice(list_index_action)