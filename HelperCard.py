from Objects import *
from Players import *
import math

# play() -> play_on_eval() (BEFORE EVAL) -> remove_check() (AFTER EVAL) -> clean_up()
class HelperCard:
    # For test/typing purposes...
    _mock_up_data = {
        "turn":"PLAYER", #"PLAYER, DEMON"
        "player":Player([],[],[]),
        "grid":Grid(4),
        "demon":Demon(),
        "scale":Scale(10)
    }

    
    def __init__(self, n, d):
        self.name = n
        self.description = d
        self.coord = None # maybe useful for storing player's chosen card
        self.needs_target = False #sends the cursor to the grid :)
        self.blacklist_states = ["EVALUATE_COMBO","SPAWN_CARDS","HANG"]

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
        self.get_player_coord(game_state)
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        print("VERIFY:",temp_card, self.coord,temp_card.flipped, self.name in temp_card.effects)
        if temp_card.flipped == False and not self.name in temp_card.effects:
            return True
        return False
    
    def get_player_coord(self,game_state):
        if game_state['turn'] == "DEMON":
            plyr = game_state["demon"]
        else:
            plyr = game_state["player"]
        self.coord = (plyr.cursor_x, plyr.cursor_y)

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
        "Let you choose cards twice, if you don't complete a combo.",
        )
        self.needs_target = False

    def verify(self,gs):
        return True
    
    def play(self,gs):
        self.played_by = gs['turn']
    
    def play_on_eval(self, game_state):
        game_state['extra_turn'] = self.played_by

    def remove_check(self, gs):
        return True
    
    def clean_up(self, game_state):
        pass

class Trap(HelperCard):
    def __init__(self):
        self.triggered = False
        super().__init__("Trap",
        "Drain card points from opponent if picked.",
        )
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
        self.played_by = gs['turn']
        self.basic_send_effect(gs)

    def play_on_eval(self,game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if temp_card.flipped and not self.triggered:
            data = game_state.get("data_to_evaluate")
            if data:
                # Find out exactly who flipped this trap
                picker = data["player"].upper() 
                
                # Only punish if the OPPONENT picked it
                if picker != self.played_by and not (game_state["turn"] in self.blacklist_states):
                    if self.played_by == 'PLAYER':
                        game_state["scale"].player_score += temp_card.value
                        game_state["scale"].player_scored += temp_card.value
                        game_state["scale"].demon_score -= temp_card.value
                        game_state["scale"].demon_scored -= temp_card.value
                    elif self.played_by == 'DEMON':
                        game_state["scale"].demon_score += temp_card.value
                        game_state["scale"].demon_scored += temp_card.value
                        game_state["scale"].player_score -= temp_card.value
                        game_state["scale"].player_scored -= temp_card.value
                
                # Mark as triggered regardless of who stepped on it so it can be cleaned up
                self.triggered = True

    def remove_check(self, game_state):
        return self.triggered

# MORE STUFF!
class Blind(HelperCard):
    def __init__(self):
        super().__init__("Blind",
            "Unflips a revealed tile.")
        self.needs_target = True

    def verify(self, game_state):
        self.get_player_coord(game_state)
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        return(temp_card.flipped == True)

    def play(self, game_state):
        # We hide the tile by ensuring no Peek effect is present.
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        temp_card.flipped = False

    def play_on_eval(self, game_state):
        pass

    def clean_up(self, game_state):
        pass

    def remove_check(self, game_state):
        return True  # one-shot

class Oracle(HelperCard):
    def __init__(self):
        super().__init__("Oracle",
            "Shows the position of the highest-value unflipped tile.")
        self.needs_target = False
        self.revealed_coord = None

    def verify(self, game_state):
        return True

    def play(self, game_state):
        grid = game_state["grid"]
        Player = game_state["player"]
        best = None
        best_val = -float('inf')
        for row in range(grid.size):
            for col in range(grid.size):
                cell = grid.get_item(row, col)
                if not cell.flipped and cell.value > best_val:
                    best_val = cell.value
                    best = (row, col)
        if best:
            self.revealed_coord = best
            print(best_val)
            Player.hand_cursor = -1
            Player.cursor_x = best[0]
            Player.cursor_y = best[1]

    def play_on_eval(self, game_state):
        pass

    def remove_check(self, game_state):
        return True  # one-shot

# ── MANIPULATION / SABOTAGE ───────────────────────────────────────────────────

class Inflate(HelperCard):
    def __init__(self):
        super().__init__("Inflate",
            "Doubles a chosen tile's value for a turn.")
        self.needs_target = True
        self.original_value = None
        self.done = False

    def verify(self, game_state):
        self.get_player_coord(game_state)
        return True

    def play(self, game_state):
        self.basic_send_effect(game_state)
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        self.original_value = temp_card.value
        temp_card.value *= 2

    def play_on_eval(self, game_state):
        self.done = True

    def clean_up(self, game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if temp_card is not None:
            temp_card.value = self.original_value
        
        print("INFLATE: ",temp_card.value)

    def remove_check(self, game_state):
        return self.done

class Deflate(HelperCard):
    def __init__(self):
        super().__init__("Deflate",
            "Halves a chosen tile's value for a turn.")
        self.needs_target = True
        self.original_value = None
        self.done = False

    def verify(self, game_state):
        self.get_player_coord(game_state)
        return True

    def play(self, game_state):
        self.basic_send_effect(game_state)
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        self.original_value = temp_card.value
        temp_card.value = temp_card.value//2
    
    def play_on_eval(self, game_state):
        self.done = True

    def clean_up(self, game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if temp_card is not None:
            temp_card.value = self.original_value
        self.done = True
        print("DEFLATE: ",temp_card.value)

    def remove_check(self, game_state):
        return self.done

class Scramble(HelperCard):
    def __init__(self):
        super().__init__("Scramble",
            "Shuffles the values of all unflipped tiles randomly.")
        self.needs_target = False

    def verify(self, game_state):
        return True

    def play(self, game_state):
        import random
        grid = game_state["grid"]
        cells = []
        values = []
        for row in range(grid.size):
            for col in range(grid.size):
                cell = grid.get_item(row, col)
                if not cell.flipped:
                    cells.append(cell)
                    values.append(cell.value)
        random.shuffle(values)
        for cell, val in zip(cells, values):
            cell.value = val
        print(f"Scramble: shuffled {len(cells)} tile values.")

    def play_on_eval(self, game_state):
        pass

    def clean_up(self, game_state):
        pass

    def remove_check(self, game_state):
        return True  # one-shot

class Curse(HelperCard):
    """The opponent's next tile pick scores negative points for them."""
    def __init__(self):
        super().__init__("Curse",
            "The opponent's next tile pick scores negative instead of positive.")
        self.needs_target = False
        self.played_by = None
        self.triggered = False

    def verify(self, game_state):
        return True

    def play(self, game_state):
        self.played_by = game_state["turn"]
        print("Curse: opponent's next pick will score negatively.")

    def play_on_eval(self, game_state):
        if not self.triggered:
            data = game_state.get("data_to_evaluate")
            if data:
                picker = data["player"].upper()
                if picker != self.played_by and not (game_state["turn"] in self.blacklist_states):
                    # Calculate total value they are about to receive
                    total_val = 0
                    for item in data["valid_cards"]:
                        if isinstance(item, list):
                            total_val += sum(c.value for c in item)
                        else:
                            total_val += item.value
                            
                    if picker == "PLAYER":
                        game_state["scale"].player_score -= abs(total_val) * 2
                        game_state["scale"].player_scored -= abs(total_val) * 2
                    else:
                        game_state["scale"].demon_score -= abs(total_val) * 2
                        game_state["scale"].demon_scored -= abs(total_val) * 2
                        
                    self.triggered = True

    def clean_up(self, game_state):
        pass

    def remove_check(self, game_state):
        return self.triggered

class Bounty(HelperCard):
    def __init__(self):
        super().__init__("Bounty",
            f"Adds 3 points to an unflipped tile.")
        self.BONUS = 3
        self.needs_target = True

    def verify(self, game_state):
        return self.basic_verify(game_state)

    def play(self, game_state):
        self.basic_send_effect(game_state)
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        temp_card.value += self.BONUS

    def remove_check(self, game_state):
        return True

# ── GRID ALTERATION ───────────────────────────────────────────────────────────

class Wall(HelperCard):
    """Permanently blocks a tile from being picked by either player."""
    def __init__(self):
        super().__init__("Wall",
            "Permanently blocks a tile from being picked.")
        self.needs_target = True

    def verify(self, game_state):
        return self.basic_verify(game_state)

    def play(self, game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        temp_card.lock = True
        temp_card.effects.append("Wall")
        print(f"Wall: tile {self.coord} is permanently blocked.")

    def play_on_eval(self, game_state):
        pass

    def clean_up(self, game_state):
        # Wall is permanent — do not remove lock on clean_up
        pass

    def remove_check(self, game_state):
        return True  # card is done immediately; lock persists on the tile

# ── COMBO / CONDITIONAL ───────────────────────────────────────────────────────
class Payback(HelperCard):
    def __init__(self):
        super().__init__("Payback",
            "If next turn your scale is negative, get double score of the difference.")
        self.needs_target = False
        self.played_by = None
        self.triggered = False
        self.round = 0

    def verify(self, game_state):
        return True

    def play(self, game_state):
        self.played_by = game_state["turn"]
        pass

    def play_on_eval(self, game_state):
        if game_state["turn"] != self.played_by:
            # first round (now), then 2nd Pass
            if self.round >= 1:
                # check the scales...
                delta = game_state["scale"].get_delta_score()
                is_negative = (delta < 0) if self.played_by == "PLAYER" else (delta > 0)
                if is_negative:
                    bonus = abs(delta) * 2
                    if self.played_by == "DEMON":
                        game_state["scale"].demon_score += bonus
                        game_state["scale"].demon_scored += bonus
                    else:
                        game_state["scale"].player_score += bonus
                        game_state["scale"].player_scored += bonus
                self.triggered = True
            self.round += 1
        pass

    def remove_check(self, game_state):
        return self.triggered

# ── NON-TARGETING CARDS (needs_target = False) ────────────────────────────────

class Windfall(HelperCard):
    def __init__(self):
        super().__init__("Windfall",
            "Draw a random helper card immediately.")
        self.needs_target = False

    def verify(self, game_state): return True

    def play(self, game_state):
        player = game_state["player"]
        player.hand.append(player.choose_helper())
        pass

    def play_on_eval(self, game_state): pass
    def clean_up(self, game_state): pass
    def remove_check(self, game_state): return True  # one-shot

class Fog(HelperCard):
    def __init__(self):
        super().__init__("Fog",
            "Unflip all currently revealed tiles.")
        self.needs_target = False

    def verify(self, game_state): return True

    def play(self, game_state):
        grid = game_state["grid"]
        for row in range(grid.size):
            for col in range(grid.size):
                tile = grid.get_item(row, col)
                if tile.flipped:
                    tile.flipped = False

    def play_on_eval(self, game_state): pass
    def clean_up(self, game_state): pass
    def remove_check(self, game_state): return True

# ── MULTI-ROUND CARDS ─────────────────────────────────────────────────────────

class Bleed(HelperCard):
    def __init__(self):
        super().__init__("Bleed",
            "Opponent loses 1 point per turn for 3 rounds.")
        self.needs_target = False
        self.played_by = None
        self.round = 0
        self.MAX_ROUNDS = 5

    def verify(self, game_state): return True

    def play(self, game_state):
        self.played_by = game_state["turn"]

    def play_on_eval(self, game_state):
        if game_state["turn"] != self.played_by and not (game_state["turn"] in self.blacklist_states):
            # It's the opponent's turn — drain them
            if self.played_by == "PLAYER":
                game_state["scale"].demon_score -= 1
                game_state["scale"].demon_scored -= 1
            else:
                game_state["scale"].player_score -= 1
                game_state["scale"].player_scored -= 1
            self.round += 1

    def clean_up(self, game_state): pass

    def remove_check(self, game_state):
        return self.round >= self.MAX_ROUNDS

helpers = [
    Peek, Lock, TwoTime, Trap,
    Blind, Oracle, Curse,
    Inflate, Deflate, Scramble, Bounty,
    Payback, Windfall, Fog, Bleed
]