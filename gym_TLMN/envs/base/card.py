class Card:
    def __init__(self, stt: int):
        name = ''
        stt %= 52
        score = stt // 4
        if score == 8:
            name = 'Jack'
        elif score == 9:
            name = 'Queen'
        elif score == 10:
            name = 'King'
        elif score == 11:
            name = 'Ace'
        elif score == 12:
            name = '2'
        else:
            name = str(score+3)

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

        name += '_' + card_type

        self.__stt = stt
        self.__name = name
        self.__score = score
        self.__card_type = card_type

    @property
    def stt(self):
        return self.__stt

    @property
    def name(self):
        return self.__name

    @property
    def score(self):
        return self.__score

    @property
    def card_type(self):
        return self.card_type

    def convert_to_dict(self):
        return {
            'stt': self.__stt,
            'name': self.__name,
            'score': self.__score,
            'card_type': self.__card_type
        }