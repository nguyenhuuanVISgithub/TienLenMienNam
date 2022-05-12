from colorama import Fore, Style
import gym
import random
import pandas
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

        data_action_space = pandas.read_csv('gym_TLMN/envs/action_space.csv')

        self.dict_input = {
            'Board': self.board,
            'Player': self.players,
            'Playing_id': [i for i in range(amount_player)],
            'Turn_id': self.players.index(self.turn),
            'Turn_player_cards': [],
            'State': [],
            'Close_game': -1,
            'List_all_action_code': list(data_action_space['action_code'])
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
        self.dict_input['State'] = self.state()
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

    def step(self, action_player):
        if self.close():
            self.process([])
            self.dict_input['Close_game'] = 1 if self.turn.name == self.p_name_victory else 0
            self.dict_input['State'] = self.state()
            
            return self, None, True, None
        else:
            if type(action_player) == list:
                self.process(action_player)

            else:
                if action_player == 0:
                    self.process([])
                else:
                    action_code = self.dict_input['List_all_action_code'][action_player]
                    temp = action_code.split('_')
                    hand_score = int(temp[-1])
                    hand_name = '_'.join(temp[:temp.__len__() - 1])
                    list_action = self.admin.list_card_hand(self.players_cards[self.turn.name], hand_name)
                    check = False
                    for act in list_action:
                        if act['hand_name'] == hand_name and act['hand_score'] == hand_score:
                            self.process(act['list_card'])
                            check = True
                            break

                    if not check:
                        print(Fore.LIGHTRED_EX + 'Index action không đúng: ' + str(action_player))

            done = self.close()

            if done:
                print_horizontal_lines()
                print(Fore.LIGHTYELLOW_EX + 'Chúc mừng ' + str(self.p_name_victory)+' là người chiến thắng', end='')
                print(Style.RESET_ALL)

                self.dict_input['Close_game'] = 1 if self.turn.name == self.p_name_victory else 0
                self.board._Board__turn_cards = {'list_card': [], 'hand_name': 'Nothing', 'hand_score': -1}
                self.board._Board__turn_cards_owner = 'None'
                self.dict_input['Playing_id'] = [i for i in range(self.players.__len__())]
                self.dict_input['State'] = self.state()

            return self, None, done, None
    
    def process(self, action_player: list):
        check_, score = self.check_action(action_player, self.dict_input['Turn_player_cards'])
        val_list_action = [i.stt for i in action_player]

        def print_list_card_(action_player, check_):
            for i in action_player:
                print(Fore.LIGHTBLUE_EX + i.name, end=', ')   

            print(Fore.LIGHTGREEN_EX + 'Type: ' + check_, end='')
            print(Style.RESET_ALL)

        if self.board.turn_cards['list_card'].__len__() == 0 or self.board.turn_cards_owner == self.turn.name: # Khởi đầu vòng chơi mới
            if check_ == 'Nothing' or check_ == 'Error_input': # Không đánh gì hoặc đầu vào lỗi
                if check_ == 'Nothing':
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' khởi đầu vòng mới nhưng không đánh gì', end='')
                else:
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTYELLOW_EX + ' đánh bài lỗi nên mất quyền khởi đầu vòng', end='')
                
                print(Style.RESET_ALL)

                # Thay đổi thẻ trên bàn chơi
                self.board._Board__turn_cards = {'list_card': [], 'hand_name': 'Nothing', 'hand_score': -1}
                self.board._Board__turn_cards_owner = 'None'

            else: # Đầu vào đúng
                print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' khởi đầu vòng mới với: ', end='')
                print_list_card_(action_player, check_)

                # Cập nhật các lá bài của người vừa đánh bài
                self.players_cards[self.turn.name] = [i for i in self.dict_input['Turn_player_cards'] if i.stt not in val_list_action]

                # Thêm vào list các thẻ đã đánh
                self.players[self.dict_input['Turn_id']]._Player__played_cards += action_player
                self.board._Board__played_cards += action_player

                # Thay đổi thẻ trên bàn chơi
                self.board._Board__turn_cards = {'list_card': action_player.copy(), 'hand_name': check_, 'hand_score': score}
                self.board._Board__turn_cards_owner = self.turn.name

            # Người đi tiếp theo
            self.dict_input['Turn_id'] = (self.dict_input['Turn_id'] + 1) % self.players.__len__()
            self.turn = self.players[self.dict_input['Turn_id']]

            # Truyền các lá bài của người tiếp theo vào state
            self.dict_input['Turn_player_cards'] = self.players_cards[self.turn.name]

            # Truyền state mới vào
            self.dict_input['State'] = self.state()

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
                    print_list_card_(action_player, check_)
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
                    print_list_card_(action_player, check_)

                # Bỏ người chơi này khỏi vòng
                indexx = self.dict_input['Playing_id'].index(self.dict_input['Turn_id'])
                self.dict_input['Playing_id'].remove(self.dict_input['Turn_id'])

                # Xác định người đi tiếp theo
                self.dict_input['Turn_id'] = self.dict_input['Playing_id'][indexx % self.dict_input['Playing_id'].__len__()]
                self.turn = self.players[self.dict_input['Turn_id']]

                # Truyền vào các lá bài của người tiếp theo vào
                self.dict_input['Turn_player_cards'] = self.players_cards[self.turn.name]

                # Nếu còn duy nhất một người trong Playing_id thì thêm lại tất cả người chơi vào
                if self.dict_input['Playing_id'].__len__() == 1:
                    self.dict_input['Playing_id'] = [i for i in range(self.players.__len__())]

                # Truyền state mới vào
                self.dict_input['State'] = self.state()

            else: # Chặt được bài trên bàn
                print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' chặt bài với: ', end='')
                print_list_card_(action_player, check_)

                # Cập nhật các lá bài của người vừa đánh bài
                self.players_cards[self.turn.name] = [i for i in self.dict_input['Turn_player_cards'] if i.stt not in val_list_action]

                # Thêm vào list các thẻ đã đánh
                self.players[self.dict_input['Turn_id']]._Player__played_cards += action_player
                self.board._Board__played_cards += action_player

                # Thay đổi thẻ trên bàn chơi
                self.board._Board__turn_cards = {'list_card': action_player.copy(), 'hand_name': check_, 'hand_score': score}
                self.board._Board__turn_cards_owner = self.turn.name

                # Nếu bài vừa đánh ra liên quan đến các là '2' hoặc dây đôi thông, tứ quý thì tất cả người chơi được thêm lại vào vòng
                if score >= 48 or check_ in ['4_of_a_kind', '3_pairs_straight', '4_pairs_straight']:
                    self.dict_input['Playing_id'] = [i for i in range(self.players.__len__())]

                # Xác định người đi tiếp theo
                indexx = self.dict_input['Playing_id'].index(self.dict_input['Turn_id'])
                self.dict_input['Turn_id'] = self.dict_input['Playing_id'][(indexx+1) % self.dict_input['Playing_id'].__len__()]
                self.turn = self.players[self.dict_input['Turn_id']]

                # Truyền vào các lá bài của người tiếp theo vào
                self.dict_input['Turn_player_cards'] = self.players_cards[self.turn.name]

                # Truyền state mới vào
                self.dict_input['State'] = self.state()

    def state(self):
        # Các lá bài đã đánh trên bàn : 0 51
        list_played_card = [card.stt for card in self.board.played_cards]
        temp_1 = [1 if i in list_played_card else 0 for i in range(52)]

        # Các lá bài hiện tại cần phải chặn 52 103
        list_turn_card = [card.stt for card in self.board.turn_cards['list_card']]
        temp_2 = [1 if i in list_turn_card else 0 for i in range(52)]

        # Các lá bài của người chơi hiện tại 104 155
        turn_player_cards = [card.stt for card in self.players_cards[self.turn.name]]
        temp_3 = [1 if i in turn_player_cards else 0 for i in range(52)]

        # Id của người chơi hiện tại 156
        turn_id = self.players.index(self.turn)

        # 4 pt, số lá bài còn lại của các người chơi theo góc nhìn agent 157 160
        temp_4_ = [9999 for i in range(4)]
        for i in range(self.players.__len__()):
            temp_4_[i] = self.players[i].amount_cards_remaining
        
        temp_4 = temp_4_[turn_id:] + temp_4_[:turn_id]

        # 4 pt, tình trạng theo vòng hoặc bỏ vòng của các người chơi theo góc nhìn agent 161 164
        temp_5_ = [0 for i in range(4)]
        for i in self.dict_input['Playing_id']:
            temp_5_[i] = 1

        temp_5 = temp_5_[turn_id:] + temp_5_[:turn_id]

        # Id của người chơi đang là chủ nhân của các lá bài cần chặn trên bàn 165
        temp_6 = None
        if self.board.turn_cards_owner == 'None':
            temp_6 = -1
        else:
            for i in range(self.players.__len__()):
                if self.players[i].name == self.board.turn_cards_owner:
                    temp_6 = i
                    break

        return temp_1 + temp_2 + temp_3 + [turn_id] + temp_4 + temp_5 + [temp_6]

    def check_action(self, action_player: list, list_card: list):
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
        temp_list = [i.stt for i in list_card]
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