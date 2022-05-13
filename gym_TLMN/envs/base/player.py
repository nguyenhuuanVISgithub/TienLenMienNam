from colorama import Fore, Style
from gym_TLMN.envs.base.card import Card
import pandas


class Player:
    def __init__(self, name: str):
        self.__name = name
        self.__full_action = list(pandas.read_csv('gym_TLMN/envs/action_space.csv')['action_code'])
        self.reset()

    def reset(self):
        self.__played_cards = []

    @property
    def name(self):
        return self.__name

    @property
    def played_cards(self):
        return self.__played_cards.copy()

    @property
    def amount_cards_remaining(self):
        return 13 - self.__played_cards.__len__()

    def get_list_index_action(self, state: list):
        list_all_action_code = self.__full_action.copy()
        if self.check_victory(state) == -1:
            action_space = self.get_action_space_from_list_state(state)
            list_action = []
            for key in action_space:
                list_action += action_space[key]
            
            list_action_code = []
            for action in list_action:
                hand_name = action['hand_name']
                hand_score = action['hand_score']
                list_action_code.append(f'{hand_name}_{hand_score}')

            return [list_all_action_code.index(action_code) for action_code in list_action_code]
        
        return [0]
    
    def check_victory(self, state: list):
        temp = state[157:161]
        if min(temp) == 0:
            if temp[0] == 0:
                return 1

            return 0

        return -1

    def get_action_space_from_list_state(self, state: list):
        board_turn_cards_ = state[52:104]
        my_cards_ = state[104:156]
        my_id_ = state[156]
        turn_cards_owner_id_ = state[165]

        board_list_card = [Card(i) for i in range(52) if board_turn_cards_[i] == 1]
        my_list_card = [Card(i) for i in range(52) if my_cards_[i] == 1]

        if my_id_ == turn_cards_owner_id_ or board_list_card.__len__() == 0:
            return self.action_space(
                my_list_card,
                {'list_card': [], 'hand_name': 'Nothing', 'hand_score': -1},
                self.name
            )
        
        check_, score = self.check_hand_card(board_list_card)
        if check_ == 'Error_input':
            print(Fore.LIGHTRED_EX + 'State đầu vào của hàm get_action bị sai')
            print(Style.RESET_ALL)
            return self.action_space(
                [],
                {'list_card': [], 'hand_name': 'Nothing', 'hand_score': -1},
                'NotMe132465'
            )

        else:
            return self.action_space(
                my_list_card,
                {'list_card': board_list_card, 'hand_name': check_, 'hand_score': score},
                'NotMe132465'
            )

    def check_hand_card(self, list_card: list):
        len_ = list_card.__len__()
        if len_ == 0:
            return 'Nothing', -1

        v_list = [i.score for i in list_card]
        val_list = [i.stt for i in list_card]

        # Kiểm tra xem có 2 lá bài nào trùng hay không
        temp_list = []
        for i in val_list:
            if i in temp_list:
                return 'Error_input', -7
            
            temp_list.append(i)

        if len_ == 1:
            return 'Single', list_card[0].stt

        if len_ == 2:
            if self.list_card_hand(list_card, 'Pair').__len__() != 0:
                return 'Pair', max(val_list)

            return 'Error_input', -7

        # Kiểm tra xem có phải là sảnh
        if max(v_list) - min(v_list) == (len_-1) and max(v_list) != 12:
            if self.list_card_hand(list_card, f'{len_}_straight').__len__() != 0:
                return f'{len_}_straight', max(val_list)

        # Kiểm tra xem có phải bộ ba hoặc tứ quý
        if max(v_list) == min(v_list):
            return f'{len_}_of_a_kind', max(val_list)

        # Kiểm tra dây đôi thông
        if len_ % 2 == 0 and len_ >= 6:
            if self.list_card_hand(list_card, f'{len_//2}_pairs_straight').__len__() != 0:
                return f'{len_//2}_pairs_straight', max(val_list)

        return 'Error_input', -7

    def action_space(self, list_card: list, board_turn_cards: dict, board_turn_cards_owner: str):
        possible_action = self.possible_action(list_card)
        action_space = {}

        if board_turn_cards['hand_name'] == 'Nothing' or board_turn_cards_owner == self.name:
            return possible_action
        
        list_hand_name = ['Nothing']
        if board_turn_cards['hand_name'] in ['Single', 'Pair', '3_of_a_kind']\
                                            + [f'{k}_straight' for k in range(3,12)]:
            if board_turn_cards['hand_score'] <= 47:
                list_hand_name += [board_turn_cards['hand_name']]
            else:
                if board_turn_cards['hand_name'] == 'Single':
                    list_hand_name += ['Single', '4_of_a_kind']\
                                    + [f'{k}_pairs_straight' for k in [3,4]]
                elif board_turn_cards['hand_name'] == 'Pair':
                    list_hand_name += ['Pair', '4_of_a_kind', '4_pairs_straight']
                else:
                    pass
            
            list_keys = list(possible_action.keys())
            for hand_name in list_hand_name:
                if hand_name in list_keys:
                    if hand_name == board_turn_cards['hand_name']:
                        temp_list = [action for action in possible_action[hand_name] if action['hand_score'] > board_turn_cards['hand_score']]
                        if temp_list.__len__() > 0:
                            action_space[hand_name] = temp_list.copy()
                    else:
                        action_space[hand_name] = possible_action[hand_name].copy()

            return action_space
        
        if board_turn_cards['hand_name'] == '3_pairs_straight':
            list_hand_name += [f'{k}_pairs_straight' for k in [3,4]] + ['4_of_a_kind']
        elif board_turn_cards['hand_name'] == '4_of_a_kind':
            list_hand_name += ['4_of_a_kind', '4_pairs_straight']
        elif board_turn_cards['hand_name'] == '4_pairs_straight':
            list_hand_name += ['4_pairs_straight']
        else:
            pass

        list_keys = list(possible_action.keys())
        for hand_name in list_hand_name:
            if hand_name in list_keys:
                if hand_name == board_turn_cards['hand_name']:
                    temp_list = [action for action in possible_action[hand_name] if action['hand_score'] > board_turn_cards['hand_score']]
                    if temp_list.__len__() > 0:
                        action_space[hand_name] = temp_list.copy()
                else:
                    action_space[hand_name] = possible_action[hand_name].copy()

        return action_space

    def possible_action(self, list_card: list):
        possible_action = {}
        list_hand_name = ['Nothing', 'Single', 'Pair']\
                        + [f'{k}_of_a_kind' for k in [3,4]]\
                        + [f'{k}_pairs_straight' for k in [3,4]]\
                        + [f'{k}_straight' for k in range(3,12)]

        for hand_name in list_hand_name:
            list_action = self.list_card_hand(list_card, hand_name)
            if list_action.__len__() != 0:
                possible_action[hand_name] = list_action.copy()
            
        return possible_action

    def get_list_state(self, dict_input: dict):
        # Các lá bài đã đánh trên bàn 0 51
        list_played_card = [card.stt for card in dict_input['Board'].played_cards]
        temp_1 = [1 if i in list_played_card else 0 for i in range(52)]

        # Các lá bài hiện tại cần phải chặn 52 103
        list_turn_card = [card.stt for card in dict_input['Board'].turn_cards['list_card']]
        temp_2 = [1 if i in list_turn_card else 0 for i in range(52)]

        # Các lá bài của người chơi hiện tại 104 155
        turn_player_cards = [card.stt for card in dict_input['Turn_player_cards']]
        temp_3 = [1 if i in turn_player_cards else 0 for i in range(52)]

        # Id của người chơi hiện tại 156
        list_player_name = [p.name for p in dict_input['Player']]
        turn_id = list_player_name.index(self.name)

        # 4 pt, số lá bài còn lại của các người chơi theo góc nhìn agent 157 160
        temp_4_ = [13 for i in range(4)]
        for i in range(list_player_name.__len__()):
            temp_4_[i] = dict_input['Player'][i].amount_cards_remaining
        
        temp_4 = temp_4_[turn_id:] + temp_4_[:turn_id]

        # 4 pt, tình trạng theo vòng hoặc bỏ vòng của các người chơi theo góc nhìn agent 161 164
        temp_5_ = [0 for i in range(4)]
        for i in dict_input['Playing_id']:
            temp_5_[i] = 1

        temp_5 = temp_5_[turn_id:] + temp_5_[:turn_id]

        # Id của người chơi đang là chủ nhân của các lá bài cần chặn trên bàn 165
        temp_6 = -1
        for i in range(list_player_name.__len__()):
            if dict_input['Player'][i].name == dict_input['Board'].turn_cards_owner:
                temp_6 = i
                break
        
        return temp_1 + temp_2 + temp_3 + [turn_id] + temp_4 + temp_5 + [temp_6]

    def list_card_hand(self, _list_card: list, hand_name: str):
        list_return = []
        list_card = _list_card.copy()
        list_card.sort(key=lambda x:x.stt)

        if hand_name == 'Nothing':
            list_return.append({
                'list_card': [],
                'hand_name': 'Nothing',
                'hand_score': -1
            })

        elif hand_name == 'Single':
            list_return += [{
                'list_card': [card],
                'hand_name': 'Single',
                'hand_score': card.stt
            } for card in list_card]

        elif hand_name == 'Pair' or hand_name.endswith('_of_a_kind'):
            n = None
            if hand_name == 'Pair':
                n = 2
            else:
                n = int(hand_name.split('_of_a_kind')[0])

            for i in range(13):
                temp_list = [card for card in list_card if card.score == i]
                if temp_list.__len__() >= n:
                    _temp_list_ = temp_list[:n-1]
                    for j in range(n-1, temp_list.__len__()):
                        list_return.append({
                            'list_card': _temp_list_ + [temp_list[j]],
                            'hand_name': 'Pair' if n == 2 else f'{n}_of_a_kind',
                            'hand_score': temp_list[j].stt
                        })

        elif hand_name.endswith('_pairs_straight'):
            n = int(hand_name.split('_pairs_straight')[0])
            list_score = []
            _list_score_ = []

            for i in range(12):
                temp_list = [card for card in list_card if card.score == i]
                if temp_list.__len__() >= 2:
                    list_score.append(i)
                    _list_score_.append(temp_list)

            list_straight_arr = list_straight_subsequence(list_score, n)
            if list_straight_arr.__len__() > 0:
                for straight_arr in list_straight_arr:
                    index_arr = [list_score.index(i) for i in straight_arr]
                    list_max_pair = []
                    max_score_cards = _list_score_[index_arr[n-1]]
                    temp_list = [max_score_cards[0]]
                    for i in range(1, max_score_cards.__len__()):
                        list_max_pair.append(temp_list + [max_score_cards[i]])
                    
                    temp_list = []
                    for i in index_arr[:n-1]:
                        temp_list += _list_score_[i][:2]

                    for pair in list_max_pair:
                        list_return.append({
                            'list_card': temp_list + pair,
                            'hand_name': f'{n}_pairs_straight',
                            'hand_score': pair[1].stt
                        })

        elif hand_name.endswith('_straight'):
            n = int(hand_name.split('_straight')[0])
            list_score = []
            _list_score_ = []

            for i in range(12):
                temp_list = [card for card in list_card if card.score == i]
                if temp_list.__len__() >= 1:
                    list_score.append(i)
                    _list_score_.append(temp_list)

            list_straight_arr = list_straight_subsequence(list_score, n)
            if list_straight_arr.__len__() > 0:
                for straight_arr in list_straight_arr:
                    index_arr = [list_score.index(i) for i in straight_arr]
                    max_score_cards = _list_score_[index_arr[n-1]]
                    temp_list = []
                    for i in index_arr[:n-1]:
                        temp_list.append(_list_score_[i][0])

                    for card in max_score_cards:
                        list_return.append({
                            'list_card': temp_list + [card],
                            'hand_name': f'{n}_straight',
                            'hand_score': card.stt
                        })

        return list_return

def list_straight_subsequence(list_int: list, k: int):
    n = list_int.__len__()
    if k <= 2 or n < k:
        return []
        
    list_return = []
    for i in range(0, n-k+1):
        sub_list = list_int[i:i+k]
        if max(sub_list) - min(sub_list) == k-1:
            list_return.append(sub_list)

    return list_return