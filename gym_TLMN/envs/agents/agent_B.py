from ..base.player import Player
import random
from colorama import Fore, Style


class Agent(Player):
    def __init__(self, name):
        super().__init__(name)

    def action(self, dict_input):
        list_action = self.get_list_index_action(dict_input['State'], dict_input['List_all_action_code'], dict_input['Close_game'])
        random.shuffle(list_action)
        # print(list_action)
        action = random.choice(list_action)
        # print(action)
        print(dict_input['State'][:52], 'Đã đánh')
        print(dict_input['State'][52:104], 'Cần chặn')
        print(dict_input['State'][104:156], 'Trên tay')
        print(dict_input['State'][156], 'ID')
        print(dict_input['State'][157:161], 'Số lá còn lại')
        print(dict_input['State'][161:165], 'Tình trạng bỏ vòng')
        print(dict_input['State'][165], 'ID chủ nhân bài hiện tại')
        print(dict_input['Close_game'])
        
        if dict_input['Close_game'] != -1:
            if dict_input['Close_game'] == 0:
                print(Fore.LIGHTYELLOW_EX + self.name + ' thua')
            elif dict_input['Close_game'] == 1:
                print(Fore.LIGHTYELLOW_EX + self.name + ' thắng')
            
            print('Dòng lệnh trên và dòng lệnh này được in ra từ agent')
            print(Style.RESET_ALL)
            
        return action

    