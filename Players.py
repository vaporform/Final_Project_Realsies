from Objects import Grid
import random

class Player:
    def __init__(self,deck=None,hand=None):
        if deck == None:
            self.deck = []
        else:
            self.deck = deck

        if hand == None:
            self.hand = []
        else:
            self.hand = hand
            
        self.points = 0
        self.cursor_x = 0
        self.cursor_y = 0

    def get_input(self):
        pass

class Demon(Player):
    def __init__(self,name="None",description="None", deck=[], hand=[]):
        self.name = name
        self.description = description
        self.aggression = 0.0
        self.effect_pool = []
        super().__init__(deck,hand)
    
    def decide(self,grid: Grid): # Method Overriding!
        # maybe decide?
        # get all grids that aren't flipped...
        valid = grid.get_filtered_cards(lambda card: card.flipped == False)
        choice = random.choice(valid)
        # Type, data
        return "CARD",choice