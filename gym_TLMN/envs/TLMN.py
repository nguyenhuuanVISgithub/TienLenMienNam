from colorama import Fore, Style
import gym
import random
from copy import deepcopy
from gym_TLMN.envs.base.board import Board
from gym_TLMN.envs.base.card import Card
from gym_TLMN.envs.base.player import Player
from gym_TLMN.envs.agents import agent_interface

def print_horizontal_lines():
    print('----------------------------------------------------------------------------------------------------')

def print_list_card(list_card: list):
    for i in range(list_card.__len__()):
        print(Fore.LIGHTMAGENTA_EX + str(i), end='. ')
        print(Fore.LIGHTWHITE_EX + list_card[i].name, end=', ')
        
    print(Style.RESET_ALL)




class TLMN_Env(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.reset()

    def reset(self):
        self.board = Board()
        amount_player = min(agent_interface.list_player.__len__(), 4)
        self.players = random.sample(agent_interface.list_player, k=amount_player)
        self.players_cards = {}
        for i in range(amount_player):
            self.players_cards[self.players[i].name] = []

        self.turn = random.choice(self.players)
        self.p_name_victory = 'None'
        self.dict_input = {
            'Board': self.board,
            'Player': self.players,
            'Playing_current_round': [i for i in range(amount_player)],
            'Turn_id': self.players.index(self.turn),
            'Turn_player_cards': [],
            'List_index_action': [],
            'State': []
        }

        self.setup_board()

    def setup_board(self):
        hidden_cards = [Card(i) for i in range(52)]
        total_play_cards = self.players.__len__() * 13
        self.admin = Player('ADMIN')

        reset_deal_cards = True
        while reset_deal_cards:
            random.shuffle(hidden_cards)
            i = 0

            for player in self.players:
                player.reset()
                temp_list = [hidden_cards[j] for j in range(total_play_cards) if j % self.players.__len__() == i]

                # Kiểm tra tứ quý 2
                check_list = self.admin.list_card_hand(temp_list, '4_of_a_kind')
                if check_list.__len__() != 0 and max(i['hand_score'] for i in check_list) >= 48:
                    print(Fore.LIGHTYELLOW_EX + f'{player.name} có tứ quý Hai nên chia lại bài', end='')
                    print(Style.RESET_ALL)
                    reset_deal_cards = True
                    break
                
                # Kiểm tra 5 đôi thông
                check_list = self.admin.list_card_hand(temp_list, '5_pairs_straight')
                if check_list.__len__() != 0:
                    print(Fore.LIGHTYELLOW_EX + f'{player.name} có 5 đôi thông nên chia lại bài', end='')
                    print(Style.RESET_ALL)
                    reset_deal_cards = True
                    break

                # Kiểm tra sảnh rồng
                check_list = self.admin.list_card_hand(temp_list, '12_straight')
                if check_list.__len__() != 0:
                    print(Fore.LIGHTYELLOW_EX + f'{player.name} sảnh rồng nên chia lại bài', end='')
                    print(Style.RESET_ALL)
                    reset_deal_cards = True
                    break

                self.players_cards[player.name] = temp_list.copy()
                reset_deal_cards = False
                i += 1

        self.board._Board__hidden_cards = hidden_cards[total_play_cards:]
        self.dict_input['Turn_player_cards'] = self.players_cards[self.turn.name]
        print_horizontal_lines()

    def close(self):
        temp_arr = [self.players_cards[player.name].__len__() for player in self.players]
        if min(temp_arr) == 0:
            for player in self.players:
                if self.players_cards[player.name].__len__() == 0:
                    self.p_name_victory = player.name
                    break

            return True
        
        return False

    def render(self, mode="human", close=False):
        print_horizontal_lines()
        print_list_card(self.dict_input['Turn_player_cards'])


    def step(self, list_all_action_code):
        possible_action_space = self.admin.possible_action_space(self.players_cards[self.turn.name], self.board.turn_cards, self.board.turn_cards_owner)
        list_possible_action_space = []
        for key in possible_action_space:
            list_possible_action_space += possible_action_space[key]
        
        # list_action_code = [f'{action['hand_name']}_{action['hand_score']}' for for action in list_possible_action_space]
        list_action_code = []
        for action in list_possible_action_space:
            hand_name = action['hand_name']
            hand_score = action['hand_score']
            list_action_code.append(f'{hand_name}_{hand_score}')

        self.dict_input['List_index_action'] = [list_all_action_code.index(action_code) for action_code in list_action_code]
        self.dict_input['State'] = self.state()

        action_player = self.turn.action(self.dict_input)
        if type(action_player) == list:
            self.process(action_player)

        elif type(action_player) == int:
            print(self.dict_input['State'])
            print(self.dict_input['List_index_action'])
            print(action_player)
            print_list_card(list_possible_action_space[self.dict_input['List_index_action'].index(action_player)]['list_card'])
            if action_player in self.dict_input['List_index_action']:
                list_card = list_possible_action_space[self.dict_input['List_index_action'].index(action_player)]['list_card']
                self.process(list_card)
        
        else:
            print(Fore.LIGHTRED_EX + ' đầu vào sai: ' + str(action_player))
            print(Style.RESET_ALL)

        if self.close():
            print_horizontal_lines()
            print(Fore.LIGHTYELLOW_EX + 'Chúc mừng ' + str(self.p_name_victory)+' là người chiến thắng', end='')
            print(Style.RESET_ALL)

        return self, None, self.close(), None

    def state(self):
        # Kí tự đầu: số thẻ bài còn thừa trên bàn
        state = []
        state.append(self.board._Board__hidden_cards.__len__())
        # 52 kí tự sau: Các lá bài đã được người chơi đánh ra
        list_played_card = [card.stt for card in self.board.played_cards]
        temp = [1 if i in list_played_card else 0 for i in range(52)]
        state += temp

        # 3 kí tự tiếp theo, lần lượt số lá bài còn lại của 3 người chơi đối thủ, nếu có ít hơn 4 người chơi thì coi như có 1 số người ko đánh quân bài nào
        temp = [13 for i in range(4)]
        for i in range(self.players.__len__()):
            temp[i] = self.players[i].amount_cards_remaining
        
        temp.remove(temp[self.players.index(self.turn)])
        state += temp

        return state

    def process(self, action_player):
        check_, score = self.check_action(action_player)
        val_list_action = [i.stt for i in action_player]

        if self.board.turn_cards['list_card'].__len__() == 0 or self.board.turn_cards_owner == self.turn.name:
            if check_ == 'Nothing' or check_ == 'Error_input':
                if check_ == 'Nothing':
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' khởi đầu vòng mới nhưng không đánh gì', end='')
                else:
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTYELLOW_EX + ' đánh bài lỗi nên mất quyền khởi đầu vòng', end='')
                
                print(Style.RESET_ALL)
            
                # Thay đổi thẻ trên bàn chơi
                self.board._Board__turn_cards = {
                    'list_card': [],
                    'hand_name': 'Nothing',
                    'hand_score': -1,
                }
                self.board._Board__turn_cards_owner = 'None'
        
            else: # Đầu vào đúng
                print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' khởi đầu vòng mới với: ', end='')
                for i in action_player:
                    print(Fore.LIGHTBLUE_EX + i.name, end=', ')   

                print(Fore.LIGHTGREEN_EX + 'Type: ' + check_, end='')
                print(Style.RESET_ALL)

                # Cập nhật các lá bài của người vừa đánh bài
                new_player_cards = [i for i in self.dict_input['Turn_player_cards'] if i.stt not in val_list_action]
                self.players_cards[self.turn.name] = new_player_cards.copy()
                # Thêm vào list các thẻ đã đánh
                self.players[self.dict_input['Turn_id']]._Player__played_cards += action_player
                self.board._Board__played_cards += action_player
                # Thay đổi thẻ trên bàn chơi
                self.board._Board__turn_cards = {
                    'list_card': action_player.copy(),
                    'hand_name': check_,
                    'hand_score': score
                }
                self.board._Board__turn_cards_owner = self.turn.name
            
            # Tất cả người chơi được thêm lại vào vòng
            self.dict_input['Playing_current_round'] = [i for i in range(self.players.__len__())]

            # Người đi tiếp theo
            self.dict_input['Turn_id'] = (self.dict_input['Turn_id'] + 1) % self.players.__len__()
            self.turn = self.players[self.dict_input['Turn_id']]

            # Truyền các lá bài của người tiếp theo vào state
            self.dict_input['Turn_player_cards'] = self.players_cards[self.turn.name]

        else: # Không phải khởi đầu vòng mới
            elimination = None # True: bị loại khỏi vòng vì lí do nào đó, False: chặt được nên không bị loại khỏi vòng

            # Không đánh gì hoặc đầu vào lỗi
            if check_ == 'Nothing' or check_ == 'Error_input':
                if check_ == 'Nothing':
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' không chặt gì nên bị loại khỏi vòng', end='')
                else:
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTYELLOW_EX + ' đánh bài lỗi nên bị loại khỏi vòng', end='')
                    
                print(Style.RESET_ALL)
                elimination = True

            # Đánh đúng, cùng loại với bài hiện tại
            elif check_ == self.board.turn_cards['hand_name']:
                if score < self.board.turn_cards['hand_score']:
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTYELLOW_EX + ' đánh bài thấp hơn nên bị loại khỏi vòng: ', end='')
                    for i in action_player:
                        print(Fore.LIGHTBLUE_EX + i.name, end=', ')
                    
                    print(Fore.LIGHTGREEN_EX + 'Type: ' + check_, end='')
                    print(Style.RESET_ALL)
                    elimination = True
                else:
                    elimination = False
            
            # Đánh đúng, khác loại với bài hiện tại
            else:
                # 3 đôi thông chặt được 1 con 2
                if check_ == '3_pairs_straight' and self.board.turn_cards['hand_name'] == 'Single' and self.board.turn_cards['hand_score'] >= 48:
                    elimination = False
                
                # Tứ quý chặt được 1 hoặc đôi 2, 3 đôi thông
                elif check_ == '4_of_a_kind':
                    # 1 hoặc đôi 2
                    if self.board.turn_cards['hand_score'] >= 48 and self.board.turn_cards['hand_name'] in ['Single', 'Pair']:
                        elimination = False
                    # 3 đôi thông
                    elif self.board.turn_cards['hand_name'] == '3_pairs_straight':
                        elimination = False

                    else:
                        elimination = True

                # 4 đôi thông chặt được 1 hoặc đôi 2, tứ quý, 3 đôi thông
                elif check_ == '4_pairs_straight':
                    # 1 hoặc đôi 2
                    if self.board.turn_cards['hand_score'] >= 48 and self.board.turn_cards['hand_name'] in ['Single', 'Pair']:
                        elimination = False
                    # 3 đôi thông
                    elif self.board.turn_cards['hand_name'] == '3_pairs_straight':
                        elimination = False
                    # Tứ quý
                    elif self.board.turn_cards['hand_name'] == '4_of_a_kind':
                        elimination = False

                    else:
                        elimination = True

                else:
                    elimination = True

            if elimination: # Bị loại khỏi vòng chơi
                if (check_ != 'Nothing') and (check_ != 'Error_input') and check_ != self.board.turn_cards ['hand_name']:
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTYELLOW_EX + ' chặt bài không phù hợp nên bị loại khỏi vòng: ', end='')
                    for i in action_player:
                        print(Fore.LIGHTBLUE_EX + i.name, end=', ')

                    print(Fore.LIGHTGREEN_EX + 'Type: ' + check_, end='')
                    print(Style.RESET_ALL)

                # Bỏ người chơi này khỏi vòng
                indexx = self.dict_input['Playing_current_round'].index(self.dict_input['Turn_id'])
                self.dict_input['Playing_current_round'].remove(self.dict_input['Turn_id'])

                # Xác định người đi tiếp theo
                self.dict_input['Turn_id'] = self.dict_input['Playing_current_round'][indexx % self.dict_input['Playing_current_round'].__len__()]
                self.turn = self.players[self.dict_input['Turn_id']]

                # Truyền vào các lá bài của người tiếp theo vào
                self.dict_input['Turn_player_cards'] = self.players_cards[self.turn.name]

            else: # Chặt được bài trên bàn
                print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' chặt bài với: ', end='')
                for i in action_player:
                    print(Fore.LIGHTBLUE_EX + i.name, end=', ')
                
                print(Fore.LIGHTGREEN_EX + 'Type: ' + check_, end='')
                print(Style.RESET_ALL)

                # Cập nhật các lá bài của người vừa đánh bài
                new_player_cards = [i for i in self.dict_input['Turn_player_cards'] if i.stt not in val_list_action]
                self.players_cards[self.turn.name] = new_player_cards.copy()

                # Thêm vào list các thẻ đã đánh
                self.players[self.dict_input['Turn_id']]._Player__played_cards += action_player
                self.board._Board__played_cards += action_player

                # Thay đổi thẻ trên bàn chơi
                self.board._Board__turn_cards = {
                    'list_card': action_player.copy(),
                    'hand_name': check_,
                    'hand_score': score
                }
                self.board._Board__turn_cards_owner = self.turn.name

                # Nếu bài vừa đánh ra liên quan đến các là '2' hoặc dây đôi thông, tứ quý thì tất cả người chơi được thêm lại vào vòng
                if score >= 48 or check_ in ['4_of_a_kind', '3_pairs_straight', '4_pairs_straight']:
                    self.dict_input['Playing_current_round'] = [i for i in range(self.players.__len__())]

                # Xác định người đi tiếp theo
                indexx = self.dict_input['Playing_current_round'].index(self.dict_input['Turn_id'])
                self.dict_input['Turn_id'] = self.dict_input['Playing_current_round'][(indexx+1) % self.dict_input['Playing_current_round'].__len__()]
                self.turn = self.players[self.dict_input['Turn_id']]

                # Truyền vào các lá bài của người tiếp theo vào
                self.dict_input['Turn_player_cards'] = self.players_cards[self.turn.name]

    def check_action(self, action_player):
        len_ = action_player.__len__()
        if len_ == 0:
            return 'Nothing', -1

        v_list = [i.score for i in action_player]
        val_list = [i.stt for i in action_player]

        # Kiểm tra xem có 2 lá bài nào trùng hay không
        temp_list = []
        for i in val_list:
            if i in temp_list:
                print(Fore.LIGHTRED_EX + 'Có hai thẻ bài trùng nhau: ', end='')
                for i in action_player:
                    print(Fore.RED + str(i.name) + ', ', end='')

                print(Style.RESET_ALL)
                return 'Error_input', -7
            
            temp_list.append(i)

        # Kiểm tra xem các lá bài có phải của người chơi hiện tại không
        temp_list = [i.stt for i in self.dict_input['Turn_player_cards']]
        for i in val_list:
            if i not in temp_list:
                print(Fore.LIGHTRED_EX + 'Có ít nhất 1 thẻ bài không phải của người chơi hiện tại: ', end='')
                for i in action_player:
                    print(Fore.RED + str(i.name) + ', ', end='')

                print(Style.RESET_ALL)
                return 'Error_input', -7

        if len_ == 1:
            return 'Single', action_player[0].stt

        if len_ == 2:
            if self.admin.list_card_hand(action_player, 'Pair').__len__() != 0:
                return 'Pair', max(val_list)

            print(Fore.LIGHTRED_EX + 'Dạng bài không đúng: ', end='')
            for i in action_player:
                print(Fore.RED + str(i.name) + ', ', end='')

            print(Style.RESET_ALL)
            return 'Error_input', -7

        # Kiểm tra xem có phải là sảnh
        if max(v_list) - min(v_list) == (len_-1) and max(v_list) != 12:
            if self.admin.list_card_hand(action_player, f'{len_}_straight').__len__() != 0:
                return f'{len_}_straight', max(val_list)

        # Kiểm tra xem có phải bộ ba hoặc tứ quý
        if max(v_list) == min(v_list):
            return f'{len_}_of_a_kind', max(val_list)

        # Kiểm tra dây đôi thông
        if len_ % 2 == 0 and len_ >= 6:
            if self.admin.list_card_hand(action_player, f'{len_//2}_pairs_straight').__len__() != 0:
                return f'{len_//2}_pairs_straight', max(val_list)

        print(Fore.LIGHTRED_EX + 'Dạng bài không đúng: ', end='')
        for i in action_player:
            print(Fore.RED + str(i.name) + ', ', end='')

        print(Style.RESET_ALL)
        return 'Error_input', -7