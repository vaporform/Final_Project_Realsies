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
        if temp_card.flipped == False and not self.name in temp_card.effects:
            return True
        return False
    
    def get_player_coord(self,game_state):
        if game_state['turn'] == "DEMON":
            plyr = game_state["demon"]
        else:
            plyr = game_state["player"]

        print(plyr.deck, len(plyr.deck))
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
        best_val = -1
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
        # Fires when it's the opponent's turn and they pick a tile
        if game_state["turn"] != self.played_by and not self.triggered:
            # Negate whatever score was just added — implementation assumes
            # the game engine adds to scale before play_on_eval runs.
            # We double-subtract to flip the sign (undo + negate).
            # Adjust to match your actual scoring hook.
            demon = game_state["scale"].demon_scored
            game_state["scale"].demon_score -= demon*2
            self.triggered = True  # UI/engine should handle the negation signal

    def clean_up(self, game_state):
        pass

    def remove_check(self, game_state):
        return self.triggered

class Bounty(HelperCard):
    """Places bonus points on a tile; whoever picks it earns the bonus."""

    def __init__(self):
        super().__init__("Bounty",
            f"Adds 3 points on a tile for anyone who picks it.")
        self.BONUS = 3
        self.needs_target = True
        self.triggered = False

    def verify(self, game_state):
        return self.basic_verify(game_state)

    def play(self, game_state):
        self.basic_send_effect(game_state)
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        temp_card.value += self.BONUS

    def play_on_eval(self, game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if temp_card.flipped and not self.triggered:
            # Award bounty to whoever flipped it
            if game_state["turn"] == "DEMON":
                game_state["scale"].demon_score += self.BONUS
            else:
                game_state["scale"].player_score += self.BONUS
            print(f"Bounty collected! +{self.BONUS} points.")
            self.triggered = True

    def clean_up(self, game_state):
        temp_card = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if self.name in temp_card.effects:
            temp_card.effects.remove(self.name)

    def remove_check(self, game_state):
        return self.triggered

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
                if game_state["scale"].get_delta_score() <= 0:
                    game_state["scale"] += abs(game_state["scale"].get_delta_score()) * 2
                    self.triggered = True
            self.round += 1
        pass

    def remove_check(self, game_state):
        return self.triggered

class Roulette(HelperCard):
    """Randomizes the values of three random unflipped tiles."""
    TILES_AFFECTED = 3

    def __init__(self):
        super().__init__("Roulette",
            "Randomizes the values of three random unflipped tiles.")
        self.needs_target = False

    def verify(self, game_state):
        return True

    def play(self, game_state):
        import random
        grid = game_state["grid"]
        candidates = [
            grid.get_item(r, c)
            for r in range(grid.size)
            for c in range(grid.size)
            if not grid.get_item(r, c).flipped
        ]
        chosen = random.sample(candidates, min(self.TILES_AFFECTED, len(candidates)))
        values = [cell.value for cell in chosen]
        random.shuffle(values)
        for cell, val in zip(chosen, values):
            cell.value = val
        print(f"Roulette: randomized {len(chosen)} tile values.")

    def play_on_eval(self, game_state):
        pass

    def clean_up(self, game_state):
        pass

    def remove_check(self, game_state):
        return True  # one-shot

class Sacrifice(HelperCard):
    def __init__(self):
        super().__init__("Sacrifice",
            "Remove a tile to instantly score its value.")
        self.needs_target = True
        self.scored_value = 0

    def verify(self, game_state):
        return self.basic_verify(game_state)

    def play(self, game_state):
        tile = game_state["grid"].get_item(self.coord[0], self.coord[1])
        self.scored_value = tile.value
        # TODO: award self.scored_value to whoever played this
        # TODO: remove tile from grid (replace with a blank/None sentinel?)

    def play_on_eval(self, game_state): pass
    def clean_up(self, game_state): pass
    def remove_check(self, game_state): return True  # one-shot


class Brand(HelperCard):
    def __init__(self):
        super().__init__("Brand",
            "Mark a tile — whoever picks it, you score the points.")
        self.needs_target = True
        self.triggered = False
        self.played_by = None

    def verify(self, game_state):
        return self.basic_verify(game_state)

    def play(self, game_state):
        self.played_by = game_state["turn"]
        self.basic_send_effect(game_state)  # stamps "Brand" onto tile.effects

    def play_on_eval(self, game_state):
        tile = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if tile.flipped and not self.triggered:
            # TODO: award tile.value to self.played_by instead of whoever flipped it
            # Hint: look at how Trap drains with Scale.player_score
            self.triggered = True

    def clean_up(self, game_state):
        tile = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if self.name in tile.effects:
            tile.effects.remove(self.name)

    def remove_check(self, game_state): return self.triggered

# ── NON-TARGETING CARDS (needs_target = False) ────────────────────────────────

class Windfall(HelperCard):
    def __init__(self):
        super().__init__("Windfall",
            "Draw a random helper card immediately.")
        self.needs_target = False

    def verify(self, game_state): return True

    def play(self, game_state):
        import random
        player = game_state["player"]
        player.hand(player.choose_helper())
        pass

    def play_on_eval(self, game_state): pass
    def clean_up(self, game_state): pass
    def remove_check(self, game_state): return True  # one-shot


class Recall(HelperCard):
    def __init__(self):
        super().__init__("Recall",
            "Return the last used helper card to your hand.")
        self.needs_target = False

    def verify(self, game_state):
        # Only usable if there is a last_used card stored
        return game_state.get("last_used") is not None

    def play(self, game_state):
        last = game_state.get("last_used")
        if last is not None:
            game_state["player"].hand.append(last)
            game_state["last_used"] = None
        # TODO: in GameSession, set game_state["last_used"] = card
        #       whenever a helper card is played

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


class Echo(HelperCard):
    def __init__(self):
        super().__init__("Echo",
            "Your next tile pick scores double.")
        self.needs_target = False
        self.played_by = None

    def verify(self, game_state): return True

    def play(self, game_state):
        self.played_by = game_state["turn"]
        game_state["echo_active"] = True
        game_state["echo_owner"] = self.played_by
        # TODO: in GameSession._resolve_turn(), check game_state["echo_active"]
        #       and double the score before calling scale.evaluate_points()

    def play_on_eval(self, game_state): pass  # _resolve_turn handles the effect

    def clean_up(self, game_state):
        game_state["echo_active"] = False
        game_state["echo_owner"] = None

    def remove_check(self, game_state):
        # Die after the very next evaluation
        return True

# ── MULTI-ROUND CARDS ─────────────────────────────────────────────────────────

class Bleed(HelperCard):
    def __init__(self):
        super().__init__("Bleed",
            "Opponent loses 1 point per turn for 2 rounds.")
        self.needs_target = False
        self.played_by = None
        self.round = 0
        self.MAX_ROUNDS = 2

    def verify(self, game_state): return True

    def play(self, game_state):
        self.played_by = game_state["turn"]

    def play_on_eval(self, game_state):
        if game_state["turn"] != self.played_by:
            # It's the opponent's turn — drain them
            # TODO: subtract 1 from opponent's scale score
            # e.g. game_state["scale"].demon_score -= 1
            self.round += 1

    def clean_up(self, game_state): pass

    def remove_check(self, game_state):
        return self.round >= self.MAX_ROUNDS

class Countdown(HelperCard):
    def __init__(self):
        super().__init__("Countdown",
            "A tile explodes in 2 turns, scoring its value for you. If the card was not picked.")
        self.needs_target = True
        self.played_by = None
        self.round = 0
        self.triggered = False

    def verify(self, game_state):
        return self.basic_verify(game_state)

    def play(self, game_state):
        self.played_by = game_state["turn"]
        self.basic_send_effect(game_state)
        # TODO: optionally add a visual indicator on the tile ("Countdown" in effects is enough)

    def play_on_eval(self, game_state):
        self.round += 1
        if self.round >= 2:
            tile = game_state["grid"].get_item(self.coord[0], self.coord[1])
            # TODO: award tile.value to self.played_by
            # TODO: remove tile from grid (or zero it out)
            self.triggered = True

    def clean_up(self, game_state):
        tile = game_state["grid"].get_item(self.coord[0], self.coord[1])
        if self.name in tile.effects:
            tile.effects.remove(self.name)

    def remove_check(self, game_state): return self.triggered

helpers = [
    Blind, Oracle, Payback,
    Inflate, Deflate, Scramble, Bounty,
    Roulette, 
    Peek, Lock, TwoTime, Trap
]
'''
helpers = [
    Peek, Lock, TwoTime, Trap
]
'''
