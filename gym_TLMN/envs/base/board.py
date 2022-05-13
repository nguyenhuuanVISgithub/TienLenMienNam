from copy import deepcopy


class Board:
    def __init__(self):
        self.reset()

    def reset(self):
        self.__hidden_cards = []
        self.__played_cards = []
        self.__turn_cards = {
            'list_card': [],
            'hand_name': 'Nothing',
            'hand_score': -1,
        }
        self.__turn_cards_owner = 'None'

    @property
    def played_cards(self):
        return self.__played_cards.copy()

    @property
    def turn_cards(self):
        return deepcopy(self.__turn_cards)

    @property
    def turn_cards_owner(self):
        return self.__turn_cards_owner

    @property
    def amount_cards_hiding(self):
        return self.__hidden_cards.__len__()