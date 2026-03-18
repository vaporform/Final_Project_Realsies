from Objects import *
from Players import *

class HelperCard:
    # For test/typing purposes...
    _mock_up_data = {
        "turn":"PLAYER",
        "player":Player([],[]),
        "grid":Grid(4),
        "demon":Demon(),
        "scale":Scale(10)
    }
    def __init__(self, n, d):
        self.name = n
        self.description = d

    def verify(self, game_state):
        print("WARNING! DID NOT IMPLEMENT VERIFICATION!")
        return True
    
    def play(self, game_state):
        # this allows the card to fully edit everything in game when on turn
        print("WARNING! YOU HAVEN'T OVERRIDE PLAY!")
        pass

    def clean_up(self, game_state):
        # this allows the card to fully edit everything in game when turn is done
        print("WARNING! YOU HAVEN'T OVERRIDE CLEAN UP!")

    def __str__(self):
        return self.name
    
###############################

class Peek(HelperCard):
    def __init__(self):
        self.coord = None
        super().__init__("Peek",
        "Reveals selected tile of your choice",
        )
    
    def verify(self,game_state=HelperCard._mock_up_data):
        plyr = game_state["player"]
        self.coord = (plyr.cursor_x, plyr.cursor_y)
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if temp_card.flipped == False and not "Peek" in temp_card.effects:
            return True
        return False
    def play(self, game_state=HelperCard._mock_up_data):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        temp_card.effects.append("Peek")
        print(temp_card.effects)
        print("Successfully appended peek!")

    def clean_up(self, game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        temp_card.effects.remove("Peek")
        print("Removed peek effect! OK!")