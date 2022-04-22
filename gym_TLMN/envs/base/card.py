class Card:
    def __init__(self, stt):
        name = ''

        stt %= 52
        a = stt // 4
        if a == 8:
            name = 'Jack'
        elif a == 9:
            name = 'Queen'
        elif a == 10:
            name = 'King'
        elif a == 11:
            name = 'Ace'
        elif a == 12:
            name = '2'
        else:
            name = str(a+3)

        card_type = ''

        b = stt % 4
        if b == 0:
            card_type = 'Spade'
        elif b == 1:
            card_type = 'Club'
        elif b == 2:
            card_type = 'Diamond'
        else:
            card_type = 'Heart'

        name += ' ' + card_type

        self.__stt = stt
        self.__name = name
        self.__card_type = card_type

    @property
    def stt(self):
        return self.__stt

    @property
    def name(self):
        return self.__name

    @property
    def card_type(self):
        return self.__card_type