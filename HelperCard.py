from Objects import *
from Players import *

class HelperCard:
    # For test/typing purposes...
    _mock_up_data = {
        "turn":"PLAYER",
        "player":Player([],[],[]),
        "grid":Grid(4),
        "demon":Demon(),
        "scale":Scale(10)
    }

    def __init__(self, n, d):
        self.name = n
        self.description = d
        self.coord = None # maybe useful for storing player's chosen card
        self.needs_target = False
        
    def verify(self, game_state):
        '''
        Function for implementing verification for cards eg. is it ussable?
        '''

        print("WARNING! DID NOT IMPLEMENT VERIFICATION!")
        return True
    
    def play(self, game_state):
        '''
        Function for executing WHEN the player chooses the card IMMEDIATELY
        '''
        # this allows the card to fully edit everything in game when on turn
        print("WARNING! YOU HAVEN'T OVERRIDE PLAY!")
        pass
    
    def play_on_eval(self, game_state):
        '''
        Function for executing WHEN on the "evaluate" state.
        '''
        pass

    def clean_up(self, game_state):
        '''
        Function for cleaning up stuff on the "evaluate" state.
        '''
        # this allows the card to fully edit everything in game when turn is done
        print("WARNING! YOU HAVEN'T OVERRIDE CLEAN UP!")
    
    def remove_check(self, game_state):
        '''
        Function for checking if card can be removed on the "evaluate" state
        '''
        print("WARNING! DID NOT CHECK RM!")
        return True

    def basic_verify(self,game_state):
        if game_state['turn'] == "DEMON":
            plyr = game_state["demon"]
        else:
            plyr = game_state["player"]

        print(plyr.deck, len(plyr.deck))
        self.coord = (plyr.cursor_x, plyr.cursor_y)
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if temp_card.flipped == False and not self.name in temp_card.effects:
            return True
        return False
    
    def basic_send_effect(self,game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        temp_card.effects.append(self.name)
        print(temp_card.effects)
        print(f"Successfully appended {self.name}!")
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
###############################

class Pass_On(HelperCard):
    def __init__(self):
        super().__init__("Pass",
        "Pass your turn to the opponent.",)
        
    def verify(self, game_state):
        return self.basic_verify(game_state)
    
    def play(self, game_state):
        pass
    
    def play_on_eval(self, game_state):
        pass

    def clean_up(self, game_state):
        pass
    
    def remove_check(self, game_state):
        return True
    
class Peek(HelperCard):
    def __init__(self):
        super().__init__("Peek",
        "Reveals selected tile of your choice",
        )
        self.needs_target = True
    
    def verify(self,game_state=HelperCard._mock_up_data):
        return self.basic_verify(game_state)

    def play(self, game_state=HelperCard._mock_up_data):
        self.basic_send_effect(game_state)

    def clean_up(self, game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if "Peek" in temp_card.effects:
            temp_card.effects.remove("Peek")
            print("Removed peek effect! OK!")
        else:
            print("Card may have been changed, revert.")

class Lock(HelperCard):
    def __init__(self):
        super().__init__("Lock",
        "Makes the card impossible to pick from either sides.",
        )
        self.round = 0
        self.needs_target = True
    
    def verify(self,game_state=HelperCard._mock_up_data):
        return self.basic_verify(game_state)

    def play(self, game_state=HelperCard._mock_up_data):
        self.played_by = game_state['turn']
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        temp_card.lock = True
        print("Successfully appended!")

    def clean_up(self, game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if temp_card.lock == True:
            temp_card.lock = False
            print("Removed lock effect! OK!")
        else:
            print("Card may have been changed, revert.")

    def play_on_eval(self,gs):
        if gs['turn'] != self.played_by:
            self.round += 1

    def remove_check(self, game_state):
        if self.round >= 2:
            return True
        return False

class TwoTime(HelperCard):
    def __init__(self):
        super().__init__("Two Time",
        "Let you choose cards twice",
        )
        self.needs_target = False

    def verify(self,gs):
        return True
    
    def play(self,gs):
        self.played_by = gs['turn']
    
    def remove_check(self, gs):
        return True
    
    def clean_up(self, game_state):
        game_state['turn'] =self.played_by

class Trap(HelperCard):
    def __init__(self):
        self.triggered = False
        super().__init__("Trap",
        "Drain card points from opponent if picked.",
        )
        self.round = 0
        self.needs_target = True
    
    def verify(self,game_state=HelperCard._mock_up_data):
        return self.basic_verify(game_state)

    def clean_up(self, game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if self.name in temp_card.effects:
            temp_card.effects.remove(self.name)
            print("Removed lock effect! OK!")
        else:
            print("Card may have been changed, revert.")

    def play(self,gs):
        self.basic_send_effect(gs)

    def play_on_eval(self,game_state):
        self.round += 1
        if game_state['turn'] == 'DEMON':
            temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
            Scale.player_score += temp_card.value
            temp_card.value = 0
            self.triggered = True

    def remove_check(self, game_state):
        return self.triggered

helpers = [
    Peek, Lock, TwoTime, Trap
]