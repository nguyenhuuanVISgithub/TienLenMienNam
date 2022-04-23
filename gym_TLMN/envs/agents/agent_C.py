from ..base.player import Player
import random

class Agent(Player):
    def __init__(self, name):
        super().__init__(name)

    def action(self, state):
        mode = 1 # 1,2,3,4

        if mode == 1: # Tự tìm các bộ bài có thể chặt và đánh, nếu không chặt được thì bỏ vòng
            available_action_space = self.get_available_action(state['board'].set_of_cards[0], state['board'].set_of_cards[1], state['board'].set_of_cards[2], state['cur_player_cards'])
            if available_action_space == {}:
                return []
            
            list_available_action = []
            for key in available_action_space.keys():
                list_available_action += available_action_space[key]
            
            action = random.choice(list_available_action)
            
            return action['set']
        
        if mode == 2: # Đánh ngẫu nhiên các dạng bài hợp lệ (chưa chắc đã chặt được)
            action_space = self.get_action_space(state['cur_player_cards'])
            if action_space == {}:
                return []

            list_action = []
            for key in action_space.keys():
                list_action += action_space[key]

            action = random.choice(list_action)
            
            return action['set']

        if mode == 3: # Chọn random các lá bài để đánh, số lượng cũng random, tuy nhiên ko có 2 lá nào trùng nhau
            n = state['cur_player_cards'].__len__()
            k = random.randint(0,n)
            list_index = random.sample([i for i in range(n)], k)

            return [state['cur_player_cards'][i] for i in list_index]

        if mode == 4: # Chọn random các lá bài để đánh, số lượng cũng random, có thể có 2 lá bài trùng nhau
            n = state['cur_player_cards'].__len__()
            k = random.randint(0,n)

            return [random.choice(state['cur_player_cards']) for i in range(k)]