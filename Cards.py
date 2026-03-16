class BaseCard:
    def __init__(self, value=1, x=0,y=0):
        self.flipped = False
        self.value = value
        # Additional info
        self.x = x
        self.y = y

        self.owner = ""

    def flip(self):
        self.flipped = not self.flipped

class HelperCard:
    def __init__(self, n, d):
        self.name = n
        self.description = d
    
    def play(self, game_state):
        pass