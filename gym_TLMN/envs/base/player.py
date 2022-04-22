import itertools

from matplotlib.style import available

class Player:
    def __init__(self, name):
        self.message = ''
        self.__name = name
        self.__played_cards = []

    @property
    def name(self):
        return self.__name
    
    @property
    def played_cards(self):
        return self.__played_cards.copy()

    def print_card_name(self, list_card):
        for i in list_card:
            print(i.name, end=', ')

        print()

    def get_available_set(self, set_name, score):
        # Hàm này trả ra các dạng bài 'có thể' chặn được dạng bài đầu vào

        if set_name == 'Nothing':
            return ['Nothing', 'Single', 'Pair'] + [f'{k}_of_a_kind' for k in [3,4]] + [f'{k}_pairs_straight' for k in [3,4]] + [f'{k}_straight' for k in range(3,12)]
        
        if set_name == '3_pairs_straight':
            return ['3_pairs_straight']

    def get_available_action(self, set_name, score, name, cur_cards):
        # Hàm này trả ra các trường hợp có thể đánh mà không vi phạm luật chơi
        action_space = self.get_action_space(cur_cards)
        available_action_space = {}

        if set_name == 'Nothing' or set_name == '' or name == self.name:
            return action_space
        
        if set_name in ['Single', 'Pair', '3_of_a_kind'] + [f'{k}_straight' for k in range(3,12)]:
            if score < 48:
                list_keys = [set_name]
            else:
                if set_name == 'Single':
                    list_keys = ['Single', '4_of_a_kind'] + [f'{k}_pairs_straight' for k in [3,4]]
                elif set_name == 'Pair':
                    list_keys = ['Pair', '4_of_a_kind', '4_pairs_straight']
                else:
                    return {}
            
            for key in list_keys:
                available_action_space[key] = []
                if key in action_space.keys():
                    if key == set_name:
                        available_action_space[key] = [action for action in action_space[key] if action['score'] > score]
                    else:
                        available_action_space[key] = action_space[key].copy()

                if available_action_space[key].__len__() == 0:
                    del available_action_space[key]
            
            return available_action_space
        
        if set_name == '3_pairs_straight':
            list_keys = [f'{k}_pairs_straight' for k in [3,4]] + ['4_of_a_kind']
        elif set_name == '4_of_a_kind':
            list_keys = ['4_of_a_kind', '4_pairs_straight']
        elif set_name == '4_pairs_straight':
            list_keys = ['4_pairs_straight']
        else:
            return {}

        for key in list_keys:
            available_action_space[key] = []
            if key in action_space.keys():
                if key == set_name:
                    available_action_space[key] = [action for action in action_space[key] if action['score'] > score]
                else:
                    available_action_space[key] = action_space[key].copy()

            if available_action_space[key].__len__() == 0:
                del available_action_space[key]

        return available_action_space
 
    def get_action_space(self, cards=[]):
        action_space = {}
        list_set_name = ['Nothing', 'Single', 'Pair'] + [f'{k}_of_a_kind' for k in [3,4]] + [f'{k}_pairs_straight' for k in [3,4]] + [f'{k}_straight' for k in range(3,12)]
        for set_name in list_set_name:
            a_s = self.get_set_of_cards(cards, set_name)
            if a_s.__len__() != 0:
                action_space[set_name] = a_s

        return action_space

    def get_set_of_cards(self, cards=[], set_name='Nothing'):
        list_return = []
        if set_name == 'Nothing':
            pass

        elif set_name == 'Single':
            list_return = [{'set': [card], 'score': card.stt} for card in cards]

        elif set_name == 'Pair' or set_name.endswith('_of_a_kind'):
            n = None
            if set_name == 'Pair':
                n = 2
            else:
                n = int(set_name.split('_of_a_kind')[0])
            
            for i in range(13):
                temp_list = [card for card in cards if card.stt // 4 == i]
                if temp_list.__len__() >= n:
                    temp = itertools.combinations(temp_list, n)
                    list_return += [{'set': list(set_), 'score': max([card.stt for card in list(set_)])} for set_ in temp]
        
        elif set_name.endswith('_pairs_straight'):
            n = int(set_name.split('_pairs_straight')[0])
            n_list = []
            _n_list_ = []
            for i in range(12):
                temp_list = [card for card in cards if card.stt // 4 == i]
                if temp_list.__len__() > 1:
                    n_list.append(i)
                    temp_abcxyz = itertools.combinations(temp_list, 2)
                    _n_list_.append([list(set_) for set_ in temp_abcxyz])
                
            list_straight_arr = self.get_straight_arr(n_list, n)
            if list_straight_arr.__len__() > 0:
                for straight_arr in list_straight_arr:
                    list_index = [n_list.index(i) for i in straight_arr]
                    all_list = [_n_list_[i] for i in list_index]
                    temp_xyzabc = [[] for i in range(n)]
                    temp_xyzabc[0] = [set_ for set_ in all_list[0]]
                    for i in range(1,n):
                        for j in temp_xyzabc[i-1]:
                            for k in all_list[i]:
                                temp_ = j + k
                                temp_xyzabc[i].append(temp_)

                    list_return += [{'set': list_, 'score': max([i.stt for i in list_])} for list_ in temp_xyzabc[n-1]]

        elif set_name.endswith('_straight'):
            n = int(set_name.split('_straight')[0])
            n_list = []
            _n_list_ = []
            for i in range(12):
                temp_list = [card for card in cards if card.stt // 4 == i]
                if temp_list.__len__() > 0:
                    n_list.append(i)
                    _n_list_.append(temp_list)

            list_straight_arr = self.get_straight_arr(n_list, n)
            if list_straight_arr.__len__() > 0:
                for straight_arr in list_straight_arr:
                    list_index = [n_list.index(i) for i in straight_arr]
                    all_list = [_n_list_[i] for i in list_index]
                    temp_abcxyz = [[] for i in range(n)]
                    temp_abcxyz[0] = [[card] for card in all_list[0]]
                    for i in range(1,n):
                        for j in temp_abcxyz[i-1]:
                            for k in all_list[i]:
                                temp_ = j + [k]
                                temp_abcxyz[i].append(temp_)

                    list_return += [{'set': list_, 'score': max([i.stt for i in list_])} for list_ in temp_abcxyz[n-1]]

        list_return.sort(key=lambda x:x['score'])
        return list_return

    def get_straight_arr(self, input_list, k=3):
        n = input_list.__len__()
        if k <= 2 or n < k:
            return []
        
        list_return = []
        for i in range(0, n-k+1):
            temp = input_list[i:i+k]
            if max(temp) - min(temp) == (k-1):
                list_return.append(temp)

        return list_return