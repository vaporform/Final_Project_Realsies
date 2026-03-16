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
    def deck_creator(ones, twos, threes, owner):
        deck = [1]*ones + [2]*twos + [3]*threes
        return [BaseCard(value=i,owner=owner) for i in deck]

class HelperCard:
    def __init__(self, n, d):
        self.name = n
        self.description = d
    
    def play(self, game_state):
        pass