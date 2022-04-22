import gym
import random
from gym_TLMN.envs.base.board import Board
from gym_TLMN.envs.base.card import Card
from gym_TLMN.envs.base.player import Player
from gym_TLMN.envs.base.error import *
from gym_TLMN.envs.agents import agent_interface

class TLMN_Env(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.board = None
        self.players = []
        self.players_cards = {}
        self.turn = None
        self.p_name_victory = ''
        self.state = {}
        
    def reset(self):
        self.board = Board()
        amount_player = agent_interface.list_player.__len__()
        self.players = random.sample(agent_interface.list_player, k=amount_player)
        for i in range(amount_player):
            self.players_cards['p'+str(i)] = []

        self.turn = random.choice(self.players)
        self.p_name_victory = ''
        self.state = {
            'board': self.board,
            'players': self.players,
            'playing_id': [i for i in range(amount_player)],
            'cur_player_id': self.players.index(self.turn),
            'cur_player_cards': []
        }

        self.setup_board()

    def setup_board(self):
        hidden_cards = []
        for i in range(52):
            hidden_cards.append(Card(i))

        total_play_cards = self.players.__len__() * 13
        tester = Player('tester')
        reset_player_cards = True
        
        while reset_player_cards:
            random.shuffle(hidden_cards)
            for i in range(self.players.__len__()):
                temp = [hidden_cards[j] for j in range(total_play_cards) if j % self.players.__len__()==i]
                temp.sort(key=lambda x:x.stt)

                # Kiểm tra tứ quý 2
                temp_abc = tester.get_set_of_cards(temp, '4_of_a_kind')
                if temp_abc.__len__() != 0 and max([i['score'] for i in temp_abc]) >= 48:
                    print(Fore.LIGHTYELLOW_EX + ' Có người chơi có tứ quý 2 nên chia lại bài: ')
                    for j in temp:
                        print(Fore.LIGHTBLUE_EX + j.name, end=', ')
                    
                    print(Style.RESET_ALL)
                    reset_player_cards = True
                    break

                # Kiểm tra 5 đôi thông:
                temp_abc = tester.get_set_of_cards(temp, '5_pairs_straight')
                if temp_abc.__len__() != 0:
                    print(Fore.LIGHTYELLOW_EX + ' Có người chơi có 5 đôi thông nên chia lại bài: ')
                    for j in temp:
                        print(Fore.LIGHTBLUE_EX + j.name, end=', ')
                    
                    print(Style.RESET_ALL)
                    reset_player_cards = True
                    break

                # Kiểm tra sảnh rồng
                temp_abc = tester.get_set_of_cards(temp, '12_straight')
                if temp_abc.__len__() != 0:
                    print(Fore.LIGHTYELLOW_EX + ' Có người chơi có sảnh rồng nên chia lại bài: ')
                    for j in temp:
                        print(Fore.LIGHTBLUE_EX + j.name, end=', ')
                    
                    print(Style.RESET_ALL)
                    reset_player_cards = True
                    break
                
                # Kiểm tra 6 đôi bất kì
                temp_abc = tester.get_set_of_cards(temp, 'Pair')
                v_list = [i['score']//4 for i in temp_abc]
                check_list = []
                for j in v_list:
                    if j not in check_list:
                        check_list.append(j)
                
                if check_list.__len__() == 6:
                    print(Fore.LIGHTYELLOW_EX + ' Có người chơi 6 bộ đôi nên chia lại bài: ')
                    for j in temp:
                        print(Fore.LIGHTBLUE_EX + j.name, end=', ')
                    
                    print(Style.RESET_ALL)
                    reset_player_cards = True
                    break

                self.players_cards['p'+str(i)] = temp
                reset_player_cards = False
                for j in temp:
                    print(Fore.LIGHTBLUE_EX + j.name, end=', ')
                    
                print(Style.RESET_ALL)

        self.board._Board__hidden_cards = hidden_cards[total_play_cards:]
        self.state['cur_player_cards'] = self.players_cards['p'+str(self.players.index(self.turn))]
        print('----------------------------------------------------------------------------------------------------')

    def close(self):
        temp_arr = [self.players_cards['p'+str(i)].__len__() for i in range(self.players.__len__())]
        if min(temp_arr) < 1:
            for i in range(self.players.__len__()):
                if self.players_cards['p'+str(i)].__len__() == 0:
                    self.p_name_victory = self.players[i].name
                    break
            
            return True
        
        return False
    
    def render(self, mode="human", close=False):
        print('----------------------------------------------------------------------------------------------------')
        for i in range(self.state['cur_player_cards'].__len__()):
            print(Fore.LIGHTMAGENTA_EX + str(i), end='. ')
            print(Fore.LIGHTWHITE_EX + self.state['cur_player_cards'][i].name, end=', ')
        
        print(Style.RESET_ALL)
    
    def step(self, action_player):
        self.process(action_player)
        if self.close():
            print('----------------------------------------------------------------------------------------------------')
            printYellowColor('Chúc mừng '+str(self.p_name_victory)+' là người chiến thắng')
        
        return self, None, self.close(), None

    def process(self, action_player):
        check_, score = self.check_action(action_player)
        val_list_action = [i.stt for i in action_player]

        if self.board.current_cards.__len__() == 0 or self.board.set_of_cards[2] == self.turn.name: # Khởi đầu vòng mới
            if check_ == 'Nothing' or check_ == 'Error_input':
                if check_ == 'Nothing':
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' khởi đầu vòng mới nhưng không đánh gì', end='')
                else:
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTYELLOW_EX + ' đánh bài lỗi nên mất quyền khởi đầu vòng', end='')
                
                print(Style.RESET_ALL)

                # Thay đổi thẻ trên bàn chơi
                self.board._Board__current_cards = []
                self.board._Board__set_of_cards = '', -100, ''

            else: # Đầu vào đúng
                print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' khởi đầu vòng mới với: ', end='')
                for i in action_player:
                    print(Fore.LIGHTBLUE_EX + i.name, end=', ')
                
                print(Fore.LIGHTGREEN_EX + 'Type: ' + check_, end='')
                print(Style.RESET_ALL)

                # Cập nhật các lá bài của người vừa đánh bài
                new_player_cards = [i for i in self.state['cur_player_cards'] if i.stt not in val_list_action]
                self.players_cards['p'+str(self.state['cur_player_id'])] = new_player_cards
                # Thêm vào list các thẻ đã đánh
                self.turn._Player__played_cards += action_player
                self.board._Board__show_cards += action_player
                # Thay đổi thẻ trên bàn chơi
                self.board._Board__current_cards = action_player
                self.board._Board__set_of_cards = check_, score, self.turn.name
            
            # Tất cả người chơi được thêm lại vào vòng
            self.state['playing_id'] = [i for i in range(self.players.__len__())]

            # Người đi tiếp theo
            self.state['cur_player_id'] = (self.state['cur_player_id']+1) % self.players.__len__()
            self.turn = self.players[self.state['cur_player_id']]
            # Truyền các lá bài của người tiếp theo vào state
            self.state['cur_player_cards'] = self.players_cards['p'+str(self.state['cur_player_id'])]

        else: # Không phải khởi đầu vòng mới
            eliminate = None # True: bị loại khỏi vòng vì lí do nào đó, False: chặt được nên không bị loại khỏi vòng

            # Không đánh gì hoặc đầu vào lỗi
            if check_ == 'Nothing' or check_ == 'Error_input':
                if check_ == 'Nothing':
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' không chặt gì nên bị loại khỏi vòng', end='')
                else:
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTYELLOW_EX + ' đánh bài lỗi nên bị loại khỏi vòng', end='')

                print(Style.RESET_ALL)
                eliminate = True

            # Đánh đúng, cùng loại với bài hiện tại
            elif check_ == self.board.set_of_cards[0]:
                if score < self.board.set_of_cards[1]:
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTYELLOW_EX + ' đánh bài thấp hơn nên bị loại khỏi vòng: ', end='')
                    for i in action_player:
                        print(Fore.LIGHTBLUE_EX + i.name, end=', ')
                    
                    print(Fore.LIGHTGREEN_EX + 'Type: ' + check_, end='')
                    print(Style.RESET_ALL)
                    eliminate = True
                else:
                    eliminate = False
            
            # Đánh đúng, khác loại với bài hiện tại
            else:
                # 3 đôi thông chặt được 1 con 2
                if check_ == '3_pairs_straight' and self.board.set_of_cards[1] >= 48 and self.board.set_of_cards[0] == 'Single':
                    eliminate = False
                
                # Tứ quý chặt được 1 hoặc đôi 2, 3 đôi thông
                elif check_ == '4_of_a_kind':
                    # 1 hoặc đôi 2
                    if self.board.set_of_cards[1] >= 48 and self.board.set_of_cards[0] in ['Single', 'Pair']:
                        eliminate = False
                    # 3 đôi thông
                    elif self.board.set_of_cards[0] == '3_pairs_straight':
                        eliminate = False

                    else:
                        eliminate = True
                
                # 4 đôi thông chặt được 1 hoặc đôi 2, tứ quý, 3 đôi thông
                elif check_ == '4_pairs_straight':
                    # 1 hoặc đôi 2
                    if self.board.set_of_cards[1] >= 48 and self.board.set_of_cards[0] in ['Single', 'Pair']:
                        eliminate = False
                    # 3 đôi thông
                    elif self.board.set_of_cards[0] == '3_pairs_straight':
                        eliminate = False
                    # Tứ quý
                    elif self.board.set_of_cards[0] == '4_of_a_kind':
                        eliminate = False

                    else:
                        eliminate = True

                else:
                    eliminate = True

            if eliminate: # Bị loại khỏi vòng chơi
                if (check_ != 'Nothing') and (check_ != 'Error_input') and (check_ != self.board.set_of_cards[0]):
                    print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTYELLOW_EX + ' chặt bài không phù hợp nên bị loại khỏi vòng: ', end='')
                    for i in action_player:
                        print(Fore.LIGHTBLUE_EX + i.name, end=', ')
                    
                    print(Fore.LIGHTGREEN_EX + 'Type: ' + check_, end='')
                    print(Style.RESET_ALL)

                # Bỏ người chơi này khỏi vòng
                indexx = self.state['playing_id'].index(self.state['cur_player_id'])
                self.state['playing_id'].remove(self.state['cur_player_id'])

                # Xác định người đi tiếp theo
                self.state['cur_player_id'] = self.state['playing_id'][indexx % self.state['playing_id'].__len__()]
                self.turn = self.players[self.state['cur_player_id']]
                # Truyền vào các lá bài của người tiếp theo vào
                self.state['cur_player_cards'] = self.players_cards['p'+str(self.state['cur_player_id'])]

            else: # Chặt được bài trên bàn
                print(Fore.LIGHTCYAN_EX + self.turn.name + Fore.LIGHTGREEN_EX + ' chặt bài với: ', end='')
                for i in action_player:
                    print(Fore.LIGHTBLUE_EX + i.name, end=', ')
                
                print(Fore.LIGHTGREEN_EX + 'Type: ' + check_, end='')
                print(Style.RESET_ALL)

                # Cập nhật các lá bài của người vừa đánh bài
                new_player_cards = [i for i in self.state['cur_player_cards'] if i.stt not in val_list_action]
                self.players_cards['p'+str(self.state['cur_player_id'])] = new_player_cards
                # Thêm vào list các thẻ đã đánh
                self.turn._Player__played_cards += action_player
                self.board._Board__show_cards += action_player
                # Thay đổi thẻ trên bàn chơi
                self.board._Board__current_cards = action_player
                self.board._Board__set_of_cards = check_, score, self.turn.name

                # Nếu bài vừa đánh ra liên quan đến các là '2' hoặc dây đôi thông, tứ quý thì tất cả người chơi được thêm lại vào vòng
                if score >= 48 or check_ in ['4_of_a_kind', '3_pairs_straight', '4_pairs_straight']:
                    self.state['playing_id'] = [i for i in range(self.players.__len__())]

                # Xác định người đi tiếp theo
                indexx = self.state['playing_id'].index(self.state['cur_player_id'])
                self.state['cur_player_id'] = self.state['playing_id'][(indexx+1) % self.state['playing_id'].__len__()]
                self.turn = self.players[self.state['cur_player_id']]
                # Truyền vào các lá bài của người tiếp theo vào
                self.state['cur_player_cards'] = self.players_cards['p'+str(self.state['cur_player_id'])]

    def check_action(self, action_player):
        len_ = action_player.__len__()
        if len_ == 0:
            return 'Nothing', -1

        v_list = [i.stt//4 for i in action_player]
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
        temp_list = [i.stt for i in self.state['cur_player_cards']]
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
            if max(v_list) == min(v_list):
                return 'Pair', max(val_list)

            print(Fore.LIGHTRED_EX + 'Dạng bài không đúng: ', end='')
            for i in action_player:
                print(Fore.RED + str(i.name) + ', ', end='')

            print(Style.RESET_ALL)
            return 'Error_input', -7

        # Kiểm tra xem có phải là sảnh
        if max(v_list) - min(v_list) == (len_-1) and max(v_list) != 12:
            straight_check = True
            for v_check in range(min(v_list)+1, max(v_list)):
                if v_check not in v_list:
                    straight_check = False
                    break
            
            if straight_check:
                return f'{len_}_straight', max(val_list)

        # Kiểm tra xem có phải bộ ba hoặc tứ quý
        if max(v_list) == min(v_list):
            return f'{len_}_of_a_kind', max(val_list)

        # Kiểm tra dây đôi thông
        if len_ % 2 == 0 and len_ >= 6:
            n_pairs_straight_check = True
            n = int(len_/2)
            n_list = []
            for i in v_list:
                if i not in n_list:
                    n_list.append(i)
                    count = 0
                    for j in v_list:
                        if j == i:
                            count += 1

                    if count != 2:
                        n_pairs_straight_check = False
                        break
        
            if n_pairs_straight_check:
                if max(v_list) - min(v_list) == (n-1) and max(v_list) != 12:
                    for n_check in range(min(n_list)+1, max(n_list)):
                        if n_check not in n_list:
                            n_pairs_straight_check = False
                            break
                else:
                    n_pairs_straight_check = False
            
            if n_pairs_straight_check:
                return f'{n}_pairs_straight', max(val_list)

        print(Fore.LIGHTRED_EX + 'Dạng bài không đúng: ', end='')
        for i in action_player:
            print(Fore.RED + str(i.name) + ', ', end='')

        print(Style.RESET_ALL)
        return 'Error_input', -7