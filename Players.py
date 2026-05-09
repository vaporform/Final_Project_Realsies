from Objects import Grid
import random
import pygame
from AssetHelper import AssetLib

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
        self.hand_cursor = -1 #index ok??
        
        super().__init__(deck,hand)

    def get_pos_in_grid(self,events,grid_size):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            
            max_hand_idx = len(self.hand) - 1
            if self.hand_cursor >= 0: #Hand mode
                if event.key == pygame.K_LEFT:
                    self.hand_cursor -= 1
                    if self.hand_cursor < 0:
                        # leave hand mode back to grid
                        self.hand_cursor = -1

                elif event.key == pygame.K_RIGHT:
                    if max_hand_idx >= 0:
                        self.hand_cursor = min(self.hand_cursor + 1, max_hand_idx)

            else: # Grid Mode
                # DIR STUFF...
                if event.key == pygame.K_UP and self.cursor_y != 0:
                    self.cursor_y -= 1
                elif event.key == pygame.K_DOWN and self.cursor_y != grid_size-1:
                    self.cursor_y += 1
                
                if event.key == pygame.K_LEFT and self.cursor_x != 0:
                    self.cursor_x -= 1
                elif event.key == pygame.K_RIGHT:
                    if self.cursor_x < grid_size - 1:
                        self.cursor_x += 1
                    else:
                        # at right edge: enter hand mode if hand has cards
                        if max_hand_idx >= 0:
                            self.hand_cursor = 0
    
    def choose_helper(self):
        return random.choice(self.helper_cards)()

class Demon(BasePlayer):
    def __init__(self,name="None",description="None", deck=[], hand=[]):
        self.name = name
        self.description = description
        self.aggression = 0.0
        super().__init__(deck,hand)
    
    def decide(self,grid: Grid): # Method Overriding!
        # maybe decide?
        # get all grids that aren't flipped...
        valid = grid.get_filtered_cards(lambda card: card.flipped == False and card.lock == False)
        choice = random.choice(valid)
        # Type, data
        return "CARD",choice

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

class TutorialDemon(Demon):
    def __init__(self,deck,hand):
        super().__init__("Tutorial",
                        "",deck,hand)
        self.round = 0
    
    def decide(self,grid): # Method Overriding!
        self.round += 1
        if self.round > 2:
            valid = grid.get_filtered_cards(lambda card: card.flipped == False and card.lock == False)
            choice = min(valid, key=lambda c: c.value)
            return "CARD", choice
        else:
            return "ACTION", self.choose_helper()        
        
class Imp(Demon):
    def __init__(self, deck, hand=[]):
        self.skill_used = False
        super().__init__("Imp", "A low level demon. It does not have a care in the world.", deck, hand)

    def choose_helper(self):
        AssetLib.play_sfx('dash.wav')
        return super().choose_helper()

    def decide(self,grid: Grid): # Method Overriding!
        # maybe decide?
        # get all grids that aren't flipped...
        valid = grid.get_filtered_cards(lambda card: card.flipped == False and card.lock == False)
        choice = random.choice(valid)
        self.cursor_x,self.cursor_y = grid.get_coords_from_object(choice)
        

        if random.random() > (1.0 - self.aggression):
            skill = self.choose_helper()
            self.aggression = 0
            self.description = random.choice(["Sheesh, this is too easy! I'll pass.","Eh, whatever. It's your turn now.","What a waste of our boss' time! Your turn.","Jeez, I feel sorry for you! Hahaha! Puny human! I wonder what you'll do!"])
            return "ACTION", skill
        self.aggression += 0.1
        self.description = "A low level demon. It does not have a care in the world."
        
        return "CARD",choice

class Abigor(Demon):
    def __init__(self,deck,hand=[]):
        super().__init__("Abigor", "Commander of lower-demons. Likes to play it fair and square.", deck, hand)

    def choose_helper(self):
        pass

    def decide(self, grid: Grid):
        valid = grid.get_filtered_cards(lambda c: not c.flipped and not c.lock)
        scored_moves = []

        for card in valid:
            score = card.value
            for line in self.get_line_stats(grid, card):
                if line["count"] == 3: score += 10 # Completion
                if self.aggression > 0.5 and line["unflipped_count"] <= 2 and line["player_count"] > 0:
                    score -= 5 # Blocking
                    self.aggression -= 0.1
            scored_moves.append((score, card))
            self.aggression += 0.1
        return "CARD", max(scored_moves, key=lambda x: x[0])[1]

class Fafnir(Demon):
    def __init__(self,deck,hand=[]):
        super().__init__("Fafnir", "Dragon that can smell value and worth. It is blinded by numbers.", deck, hand)

    def choose_helper(self):
        AssetLib.play_sfx('roar.wav')
        return super().choose_helper()

    def decide(self, grid: Grid):
        valid = grid.get_filtered_cards(lambda c: not c.flipped and not c.lock)
        choice = max(valid, key=lambda c: c.value)
        # Now, maybe some time, they might wanna randomize!
        
        self.cursor_x,self.cursor_y = grid.get_coords_from_object(choice)
        
        print(self.cursor_x,self.cursor_y)

        if random.random() > (1.0 - self.aggression):
            # trigger
            skill = self.choose_helper()
            self.aggression = 0
            self.description = random.choice(["X MARKS THE SPOT! FAFNIR CAN SENSE IT! HUMAN GREEDY!", "FANIFIR HATES THIS CARD!", "FANIFIR HOLDS THIS CARD! NO PICKING!"])
            return "ACTION", skill

        self.description = "Dragon that can smell value and worth. It is blinded by numbers."
        self.aggression += 0.1
        return "CARD", choice

class Baphomet(Demon):
    def __init__(self, deck, hand=[]):
        super().__init__("Baphomet", "The King of Demons. Has tricks up his sleeves.", deck, hand)
    
    def choose_helper(self):
        AssetLib.play_sfx('baa.wav')
        return super().choose_helper()

    def decide(self, grid: Grid):
        valid = grid.get_filtered_cards(lambda c: not c.flipped and not c.lock)
        if random.random() > (1.0 - self.aggression): # play helpers!
            skill = self.choose_helper()
            self.aggression = 0
            flavor_text = ''
            match skill.name:
                case "Lock":
                    flavor_text = random.choice(['I shall abstain you from picking that card.',"I won't allow that to happen.","Less choices, hm?"])
                case "Bounty":
                    flavor_text = random.choice(['Greedy always stays ahead.',"I shall boost this card to my liking.","I can sense a strong card."])
                case "Trap":
                    flavor_text = random.choice(['This trap shall do nicely...',"Hmmm... I wonder will you pick that card?"])
                case "Curse":
                    flavor_text = random.choice(["Can you sense your impending doom, mortal?","Don't you feel a bit off?"])
            self.description = flavor_text

            self.cursor_x,self.cursor_y = grid.get_coords_from_object(random.choice(valid))
            
            return "ACTION", skill
        # okay, we play it safe lmao
        self.aggression += 0.05
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

        choice = max(scored_moves, key=lambda x: x[0])[1]
        self.description = "The King of Demons. Has tricks up his sleeves."
        return "CARD", choice