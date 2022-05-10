from ..base.player import Player
import random
from colorama import Fore, Style


class Agent(Player):
    def __init__(self, name):
        super().__init__(name)

    def action(self, dict_input):
        mode = 5
        
        action_space = self.action_space(dict_input['Turn_player_cards'])
        print(Fore.LIGHTWHITE_EX + 'Tất cả: ', end='')
        for key in action_space:
            print(Fore.LIGHTWHITE_EX + key, Fore.LIGHTGREEN_EX + str(action_space[key].__len__()), end=', ')
        
        print(Style.RESET_ALL)

        possible_action_space = self.possible_action_space(dict_input['Turn_player_cards'], dict_input['Board'].turn_cards, dict_input['Board'].turn_cards_owner)
        print(Fore.LIGHTWHITE_EX + 'Có thể đánh: ', end='')
        for key in possible_action_space:
            print(Fore.LIGHTWHITE_EX + key, Fore.LIGHTGREEN_EX + str(possible_action_space[key].__len__()), end=', ')

        print(Style.RESET_ALL)
        
        if mode == 1:
            
            list_possible_action = []
            for key in possible_action_space:
                list_possible_action += possible_action_space[key]

            random.shuffle(list_possible_action)
            action = random.choice(list_possible_action)

            return action['list_card']

        if mode == 2:
            list_action = []
            for key in action_space:
                list_action += action_space[key]

            random.shuffle(list_action)
            action = random.choice(list_action)

            return action['list_card']

        if mode == 3:
            n = dict_input['Turn_player_cards'].__len__()
            k = random.randint(0,n)
            list_index = random.sample([i for i in range(n)], k)

            return [dict_input['Turn_player_cards'][i] for i in list_index]

        if mode == 4:
            n = dict_input['Turn_player_cards'].__len__()
            k = random.randint(0,n)

            return [random.choice(dict_input['Turn_player_cards']) for i in range(k)]

        if mode == 5:
            return random.choice(dict_input['List_index_action'])