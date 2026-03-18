from Objects import Grid
import random
import pygame

class BasePlayer:
    def __init__(self,deck=None,hand=None):
        if deck == None:
            self.deck = []
        else:
            self.deck = deck

        if hand == None:
            self.hand = []
        else:
            self.hand = hand
        
        self.session_deck = self.deck

        self.cursor_x = 0
        self.cursor_y = 0
    
    def choose_and_remove(self, amount):
        arr = []
        for i in range(amount):
            if len(self.session_deck) != 0: # No more left...
                c = random.choice(self.session_deck)
                self.session_deck.remove(c)
                arr.append(c)
        return arr


class Player(BasePlayer):
    def __init__(self, deck, hand, helper_cards):
        self.helper_cards = helper_cards
        self.picked_helper = False
        super().__init__(deck,hand)

    def get_pos_in_grid(self,events,grid_size):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # DIR STUFF...
                if event.key == pygame.K_UP and self.cursor_y != 0:
                    self.cursor_y -= 1
                elif event.key == pygame.K_DOWN and self.cursor_y != grid_size-1:
                    self.cursor_y += 1
                
                if event.key == pygame.K_LEFT and self.cursor_x != 0:
                    self.cursor_x -= 1
                elif event.key == pygame.K_RIGHT and self.cursor_x != grid_size-1:
                    self.cursor_x += 1
        pass
    
    def choose_helper(self):
        return random.choice(self.helper_cards)()

class Demon(BasePlayer):
    def __init__(self,name="None",description="None", deck=[], hand=[]):
        self.name = name
        self.description = description
        self.aggression = 0.0
        self.effect_pool = []
        super().__init__(deck,hand)
    
    def decide(self,grid: Grid): # Method Overriding!
        # maybe decide?
        # get all grids that aren't flipped...
        valid = grid.get_filtered_cards(lambda card: card.flipped == False and card.lock == False)
        choice = random.choice(valid)
        # Type, data
        return "CARD",choice