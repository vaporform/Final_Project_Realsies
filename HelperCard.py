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
    
    def play(self, game_state=HelperCard._mock_up_data):
        plyr = game_state["player"]
        self.coord = (plyr.cursor_x, plyr.cursor_y)
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        temp_card.effects.append("Peek")
        print(temp_card.effects)
        print("Successfully appended peek!")
        pass

    def clean_up(self, game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        temp_card.effects.remove("Peek")
        print("Removed peek effect! OK!")