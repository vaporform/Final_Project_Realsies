class BaseCard:
    def __init__(self, value=1, x=0,y=0,owner="None"):
        self.flipped = False
        self.value = value
        # Additional info
        self.x = x
        self.y = y

        self.owner = owner

    def flip(self):
        self.flipped = not self.flipped
    
    @staticmethod
    def deck_creator(rates, values, owner):
        deck = []
        for index, r in enumerate(rates):
            deck.extend([values[index]] * r)
        
        return [BaseCard(value=i,owner=owner) for i in deck]

############################################

class HelperCard:
    def __init__(self, n, d):
        self.name = n
        self.description = d
    
    def play(self, game_state):
        pass