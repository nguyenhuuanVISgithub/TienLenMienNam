class Board:
    def __init__(self):
        self.__name = 'Board'
        self.__hidden_cards = []
        self.__show_cards = []
        self.__current_cards = []
        self.__set_of_cards = '', -100, ''

    @property
    def name(self):
        return self.__name
    
    @property
    def show_cards(self):
        return self.__show_cards.copy()
    
    @property
    def current_cards(self):
        return self.__current_cards

    @property
    def set_of_cards(self):
        return self.__set_of_cards