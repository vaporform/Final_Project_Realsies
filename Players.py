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
        self.hand_limit = 4
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
    
    def update_cursor_pos(self, pos):
        '''
        YOU MUST UPDATE THIS BEFORE SENDING!
        '''
        self.cursor_x = pos[0]
        self.cursor_y = pos[1]

    def get_line_stats(self, grid, card):
        '''
        Returns a list of dictionaries containing info about each line the card belongs to.
        '''
        stats = []
        x, y = grid.get_coords_from_object(card)
        # Assuming you added diagonals to get_related_coords, otherwise just rows/cols
        paths = grid.get_related_coords(x, y) 

        for path in paths:
            raw_tiles = grid.get_tiles_from_coords(path)
            # Handle your tuple/list return inconsistency here once
            tiles = raw_tiles[0] if isinstance(raw_tiles, tuple) else raw_tiles
            
            # Clean list of card objects
            line_cards = [c[0] if isinstance(c, (list, tuple)) else c for c in tiles if hasattr(c, 'flipped') or (isinstance(c, (list, tuple)) and hasattr(c[0], 'flipped'))]
            
            flipped = [c for c in line_cards if c.flipped]
            stats.append({
                "count": len(flipped),
                "sum": sum(c.value for c in flipped),
                "player_count": sum(1 for c in flipped if c.owner == "player"),
                "unflipped_count": len(line_cards) - len(flipped)
            })
        return stats

    def choose_helper(self):
        return random.choice(self.hand)()

class Imp(Demon):
    def __init__(self, deck, hand=[]):
        self.skill_used = False
        super().__init__("Imp", "A low level demon. It does not have a care in the world.", deck, hand)

    def decide(self,grid: Grid): # Method Overriding!
        # maybe decide?
        # get all grids that aren't flipped...
        valid = grid.get_filtered_cards(lambda card: card.flipped == False and card.lock == False)
        choice = random.choice(valid)
        self.update_cursor_pos(grid.get_coords_from_object(choice))
        # Type, data
        if random.random() < 0.3 and not self.skill_used:
            skill = self.choose_helper()
            self.skill_used = True
            return "ACTION", skill

        self.skill_used = False
        return "CARD",choice

class Abigor(Demon):
    def __init__(self,deck,hand=[]):
        super().__init__("Abigor", "Commander of the 60 Legions. Grand duke of Hell.", deck, hand)

    def decide(self, grid: Grid):
        valid = grid.get_filtered_cards(lambda c: not c.flipped and not c.lock)
        scored_moves = []

        for card in valid:
            score = card.value
            for line in self.get_line_stats(grid, card):
                if line["count"] == 3: score += 10 # Completion
                if self.aggression > 0.5 and line["unflipped_count"] <= 2 and line["player_count"] > 0:
                    score -= 5 # Blocking
            scored_moves.append((score, card))
        
        return "CARD", max(scored_moves, key=lambda x: x[0])[1]

class Fafnir(Demon):
    def __init__(self,deck,hand=[]):
        super().__init__("Fafnir", "Dragon that can smell value. It is blinded by numbers", deck, hand)

    def decide(self, grid: Grid):
        valid = grid.get_filtered_cards(lambda c: not c.flipped and not c.lock)
        choice = max(valid, key=lambda c: c.value)
        return "CARD", choice

class Zariel(Demon):
    def __init__(self, deck, hand=[]):
        super().__init__("Zariel", "Archduke Strategist", deck, hand)
        
    def decide(self, grid: Grid):
        valid = grid.get_filtered_cards(lambda c: not c.flipped and not c.lock)
        is_mining = len(self.deck) > 4
        scored_moves = []

        for card in valid:
            score = card.value * 2
            for line in self.get_line_stats(grid, card):
                # Completion Logic
                if line["count"] == 3:
                    score += 600 if (line["sum"] > 2 or is_mining) else -1000
                # Trap Logic
                elif line["count"] == 2:
                    score += 400 if line["sum"] < -5 else -700
                # Sabotage
                if line["player_count"] >= 1:
                    score += (line["sum"] * 15)

            scored_moves.append((score + random.uniform(0, 5), card))

        return "CARD", max(scored_moves, key=lambda x: x[0])[1]