from .BaseScene import Scene
from Objects import Grid, Scale, Timer
from BaseCard import *
from HelperCard import *

from Players import *
from AssetHelper import *

import random
import pygame

from TkStats import log_to_csv

# note to self: when coding, we must think that this file exists at the "root" of the project ( or where we place our main )
class GameSession(Scene):
    def __init__(self,log_data_path=None,next_scene=None):
        # CORE
        GRID_SIZE = 4
        self.scale = Scale(20)
        self.grid = Grid(GRID_SIZE)
        self.countdown = 0
        self.delta_time = 0
        self.turn_count = 0
        
        # Players
        normal_val = [1, 2, 3]

        self.player = Player(
            deck=BaseCard.deck_creator([18, 8, 4], normal_val, "player"),
            helper_cards=helpers,
            hand=[]
        )
        self.player_hand_cursor = 0
        
        self.player.hand_limit = 7

        self.demon = Imp(BaseCard.deck_creator([16, 6, 2], normal_val, "demon"),[Lock])
        
        self.log_data_path = log_data_path

        self.data_to_evaluate = None
        '''
        {
            "valid_cards": valid_cards,
            "combos": combos,
            player": "player"  # or "demon"
        }
        '''
        
        self.helpers_to_eval = []
        self.pending_helper = None

        # ANIMATION!
        self.change_scenes = False
        self.next_scene = next_scene
            
        self.anim = {
            "floating_texts": [],
            "fade_in_timer": Timer(1000),
            "fade_out_timer":None,
            "cursor":[0,0],
            "hand_cursor":0,
            "card_flip": 0.5,
            "card_flip_timer":None,
            "combo_clear_timer": None,
            "spawn_cards_timer": None,
            "hang_timer": None
        }

        # Cute assets <3
        BaseCard.load_graphics()
        
        AssetLib.preload_sprites([
            "wood", "book", "border", "vignette", "right_vig",
            "cards/select", "cards/lock",
            "human_token", "demon_token", "scale_mid", "plate"
        ])
        
    def demon_turn(self):
        choice_type, data = self.demon.decide(self.grid)
        match choice_type:
            case "CARD": #if it's a card, we get the coords from cards.
                x,y= self.grid.get_coords_from_object(data)
                valid_cards, combos = self.grid.select_attempt(x,y)
                if len(valid_cards) != 0 :
                    self.data_to_evaluate = {
                        "valid_cards": valid_cards,
                        "combos": combos,
                        "player": "demon"  # or "demon"
                    }
                    self.anim['card_flip_timer'] = Timer(self.anim['card_flip']*1000)
                    AssetLib.play_sfx('blipSelect.wav')
            case "ACTION":
                print(f"The demon uses {data}")
                if data.verify(self.game_state):
                    # then it's OK
                    data.play(self.game_state)
                    self.helpers_to_eval.append(data)
                else:
                    if data.name != "Pass":
                        self.demon.description = "The demon tried to use a skill, but it failed..."
                    print(" The demon passed it's turn. (check failed!)")
        
        self.game_state['turn'] = 'EVALUATE'

    def enter(self):
        '''
        Called once when entering this state.
        Reset music, set player positions, etc.
        For loading assets or heavy stuff, it is advisable to load via __init__ instead.
        '''
        # Now, pick cards from it equally.
        amount = (self.grid.size**2)//2
        select_cards = self.player.choose_and_remove(amount) + self.demon.choose_and_remove(amount)
        
        random.shuffle(select_cards)
        grid_coords = self.grid.get_all_coords()

        for i in select_cards:
            i.x = grid_coords[0]
            i.y = grid_coords[1]

        self.grid.set_tiles_from_coords(
            grid_coords,select_cards
        )

              # STATES
        self.game_state = {
            "turn": "PLAYER",
            "player": self.player,
            "grid": self.grid,
            "demon": self.demon,
            "scale": self.scale
        }
        
        self.player.hand = []

    def exit(self):
        '''
        Called once when leaving this state.
        Clean up the scene, preparing for a new one.
        '''
        pass
    
    def handle_input(self, events):
        for event in events:
            if self.game_state['turn'] != 'PLAYER' or event.type != pygame.KEYDOWN:
                continue
            keys = pygame.key.get_pressed()
            self.player.grid_move = any([
                    keys[pygame.K_UP],
                    keys[pygame.K_DOWN],
                    keys[pygame.K_LEFT],
                    keys[pygame.K_RIGHT]
                ])
            
            self.player.get_pos_in_grid(events, self.grid.size)
        
            if self.pending_helper is not None:
                if event.key == pygame.K_SPACE:
                    if self.pending_helper.verify(self.game_state):
                        if self.log_data_path != None:
                            log_to_csv(f"data/{self.log_data_path}/helper_cards.csv", [self.pending_helper.name, 1])
                        self.pending_helper.play(self.game_state)
                        self.helpers_to_eval.append(self.pending_helper)
                        self.player.hand.remove(self.pending_helper)
                        self.player.picked_helper = True
                        AssetLib.play_sfx('lockon_available.wav')
                    else:
                        AssetLib.play_sfx('error.wav')

                    self.pending_helper = None
                    continue
                
                if self.player.hand_cursor != -1:
                    self.pending_helper = None
                continue
            
            # Now, below here will be accessible if the key is a space :P
            if event.key != pygame.K_SPACE:
               continue
            
            # If a helper is selected...
            if self.player.hand_cursor != -1:
                card = self.player.hand[self.player.hand_cursor]
                if card.needs_target:
                    self.anim['hand_cursor_index'] = self.player.hand_cursor
                    self.pending_helper = card
                    self.player.hand_cursor = -1   # return to main grid
                    AssetLib.play_sfx('lockon_available.wav')
                    continue
                
                if card.verify(self.game_state):
                    self.player.picked_helper = True
                    card = self.player.hand.pop(self.player.hand_cursor)
                    if self.log_data_path != None:
                        log_to_csv(f"data/{self.log_data_path}/helper_cards.csv", [card.name, 1])
                    
                    card.play(self.game_state)
                    self.helpers_to_eval.append(card)

                    if self.player.hand_cursor >= len(self.player.hand):
                        self.player.hand_cursor = len(self.player.hand) - 1
                    if len(self.player.hand) == 0:
                        self.player.hand_cursor = -1
                    AssetLib.play_sfx('lockon_available.wav')
                else:
                    AssetLib.play_sfx('error.wav')
                continue
            
            # Normal grid stuff
            # try to select the BaseCard
            valid_cards, combos = self.grid.select_attempt(self.player.cursor_x,self.player.cursor_y)
            print("valid: ",valid_cards)
            if len(valid_cards) != 0:
                # OK! Pend the data to evaluate_points
                self.data_to_evaluate = {
                    "valid_cards": valid_cards,
                    "combos": combos,
                    "player": "player"  # or "demon"
                }

                self.game_state['turn'] = 'EVALUATE'
                self.anim['card_flip_timer'] = Timer(self.anim['card_flip']*1000)
                
                if not self.player.picked_helper and len(self.player.hand) < self.player.hand_limit:
                    if self.grid.get_item(self.player.cursor_x,self.player.cursor_y).owner == "player":
                        print("Giving player...")
                        self.player.hand.append(self.player.choose_helper())

                self.player.picked_helper = False
                self.player.grid_move = False      
                AssetLib.play_sfx('blipSelect.wav')   
        return self
    
    def evaluate(self):
        '''
        this evaluates the card that has picked AND run helper's commands :3c
        '''
        
        self.game_state['data_to_evaluate'] = self.data_to_evaluate
        
        # Reset scale floating trackers manually before helpers/eval
        self.scale.player_scored = 0
        self.scale.demon_scored = 0

        # make the cards execute at the start of evaluation
        for i in self.helpers_to_eval:
            i.play_on_eval(self.game_state)
            
        if self.data_to_evaluate == None:
            print("NOTHING TO EVALUATE! SWITCH 2 PLAYER!")
            self.game_state['turn'] = 'PLAYER' 
            self._clean_helpers()
            return
        
        self._resolve_turn()
        self._clean_helpers()
    
    def _resolve_turn(self):
        '''
        help clearing the scores and grid
        '''
        
        raw = self.data_to_evaluate
        self.scale.evaluate_points(raw['valid_cards'],raw["player"])
        
        # Spawn floating score texts
        if self.scale.player_scored != 0:
            self.anim['floating_texts'].append({
                "text": f"{'+' if self.scale.player_scored > 0 else ''}{self.scale.player_scored}",
                "timer": Timer(1500),
                "side": "player"
            })
        if self.scale.demon_scored != 0:
            self.anim['floating_texts'].append({
                "text": f"{'+' if self.scale.demon_scored > 0 else ''}{self.scale.demon_scored}",
                "timer": Timer(1500),
                "side": "demon"
            })

        target = self.demon # who cleared the grid?
        
        if raw["player"] == "player":
            target = self.player
            if self.log_data_path != None:
                log_to_csv(f"data/{self.log_data_path}/points_gained.csv", [self.scale.player_scored])

        if self.log_data_path != None: 
            # LOG DATA...
            # Board Control
            # LOG: board control
            flatten_grid = Grid.flatten_list(self.grid.grid)
            player_count = len([c for c in flatten_grid if c.owner == "player"])
            demon_count = len([c for c in flatten_grid if c.owner == "demon"])
            log_to_csv(f"data/{self.log_data_path}/board_cards.csv", [self.turn_count, player_count, demon_count])
            
            # LOG: board value range
            board_value = sum([c.value for c in flatten_grid])
            log_to_csv(f"data/{self.log_data_path}/board_values.csv", [board_value])
            log_to_csv(f"data/{self.log_data_path}/points_diff.csv", [self.scale.get_delta_score()])
            
            self.turn_count += 1
            
        # if not win..
        if self.scale.who_won() == None:
            if self.game_state.get('extra_turn'):
                self.game_state['turn'] = self.game_state['extra_turn']
                if raw["combos"] == 0:  # Only clear immediately if not going into combo animation
                    self.game_state['extra_turn'] = None
            elif raw["player"] == "player":
                self.game_state['turn'] = 'DEMON'
            else:
                self.game_state['turn'] = 'PLAYER'
            
        else:
            # we are so done bro
            self.change_scenes = True
            if self.anim['hang_timer'] == None:
                AssetLib.play_sfx('')
                self.anim['hang_timer'] = Timer(5000)
                if self.scale.who_won() == "player":
                    AssetLib.play_sfx('victory.wav')
                else:
                    AssetLib.play_sfx('lose.wav')
            self.game_state['turn'] = 'HANG'

        # Now, CLEAN!
        if raw["combos"] > 0:
            AssetLib.play_sfx('crunch_a.wav')
            self.anim['combo_clear_timer'] = Timer(500)
            self.game_state['turn'] = 'EVALUATE_COMBO'
            self._target = target
            return

        self.data_to_evaluate = None

    def _clean_helpers(self):
        for helper in self.helpers_to_eval.copy():
            if helper.remove_check(self.game_state):
                print(f"Cleaning: {helper.name}")
                helper.clean_up(self.game_state)
                self.helpers_to_eval.remove(helper)
            else:
                print("NG: ",helper)

    def update(self, dt):
        '''
        Called every frame. Returns new State or None.
        Move things, check timers.
        '''
        if self.anim['fade_out_timer'] != None and self.anim['fade_out_timer'].is_finished():
            if self.change_scenes:
                if self.next_scene == None:
                    return GameSession()
                else:
                    return self.next_scene
            
        match self.game_state["turn"]:
            case "DEMON":
                self.demon_turn()

            case "EVALUATE": # The game checker each turn...
                # Now, I think I'll cheat the card flip animation here.
                if self.anim['card_flip_timer'] == None:
                    self.evaluate()
                elif self.anim['card_flip_timer'].is_finished():
                    self.anim['card_flip_timer'] = None

            case "EVALUATE_COMBO":
                if self.anim['combo_clear_timer'] is not None and self.anim['combo_clear_timer'].is_finished():
                    self.anim['combo_clear_timer'] = None
                    raw_flattened = list(set(Grid.flatten_list(self.data_to_evaluate['valid_cards'][1:])))
                    self._spawned_coords = self.grid.get_coords_from_tiles(raw_flattened)
                    self.grid.replace_cards(raw_flattened, self._target)
                    self.data_to_evaluate = None
                    
                    # Transition to spawning the new cards
                    self.anim['spawn_cards_timer'] = Timer(500)
                    self.game_state['turn'] = 'SPAWN_CARDS'
            
            case "SPAWN_CARDS":
                if self.anim['spawn_cards_timer'] is not None and self.anim['spawn_cards_timer'].is_finished():
                    self.anim['spawn_cards_timer'] = None
                    self._spawned_coords = None
                    # Resume to next turn
                    if self.scale.who_won() != None:
                        # ok someone just won, play ze music!
                        self.game_state['turn'] = 'HANG'
                    else:
                        self.game_state['turn'] = 'DEMON' if self._target == self.player else 'PLAYER'

            case "HANG":
                if self.anim['hang_timer'] is not None and self.anim['hang_timer'].is_finished():
                    if self.anim['fade_out_timer'] == None:
                        self.anim['fade_out_timer'] = Timer(1000)
                pass
            
        self.delta_time += dt
        return None

    def _draw_grid(self,screen):
        cursor_x = self.player.cursor_x
        cursor_y = self.player.cursor_y
        # First, let's layer the parallax.
        screen.blit(AssetLib.get_sprite('wood'),(0,0))
        card_surface = pygame.Surface((200,200),flags=pygame.SRCALPHA).convert_alpha()
        card_surface.fill((0,0,0,0))
        
        # Now, blit the BaseCard things.
        for y in range(self.grid.size):
            for x in range(self.grid.size):
                card = self.grid.grid[y][x]
                card_texture = BaseCard.base_sprite_front
                # Here, I'll draw the card flipping...
                if self.data_to_evaluate is not None and card in self.data_to_evaluate["valid_cards"] and self.anim[ 'card_flip_timer'] != None:
                    # it's freshly picked! Time to animate >:3
                    w,h = card_texture.get_size()
                
                    prog = self.anim['card_flip_timer'].get_p()
                    
                    if prog < self.anim['card_flip'] - 0.05:
                        card_texture = BaseCard.base_sprite_back
                        flip_p = prog / (self.anim['card_flip'] - 0.05)
                        scale_w = max(2, round(lerp(w, 2, flip_p)))
                        
                    elif prog > self.anim['card_flip'] + 0.05:
                        card_texture = card_texture.copy()
                        text = text_to_surface(str(card.value),'AlmendraSC-Regular',32)
                        ctr = card_texture.get_rect()
                        card_texture.blit(text, text.get_rect(center=(ctr.centerx,ctr.centery-2)))
                        
                        if card.owner == "demon":
                            card_texture = palette_swap(card_texture,(255,255,255),(200,0,0))
                        elif card.owner == "spooky":
                            card_texture = palette_swap(card_texture,(255,255,255),(200,0,155))
                        flip_p = (prog- self.anim['card_flip'] + 0.05) / (self.anim['card_flip'] - 0.05)
                        scale_w = max(2, round(lerp(2, w, flip_p)))
                    else:
                        card_texture = BaseCard.base_sprite_back
                        scale_w = 2
                        
                    card_texture = pygame.transform.scale(card_texture,(scale_w,h))
                    slot_x = x * 30 + 10
                    slot_y = y * 40
                    draw_x = slot_x + (w - scale_w) // 2
                    card_surface.blit(card_texture, (draw_x, slot_y))

                elif self.game_state['turn'] == 'EVALUATE_COMBO' and self.data_to_evaluate is not None and card in Grid.flatten_list(self.data_to_evaluate['valid_cards'][1:]):
                    # Animate Combo Clearing (shrinking/fading)
                    prog = self.anim['combo_clear_timer'].get_p()
                    w, h = card_texture.get_size()
                    
                    # Add pulse & shrink effect
                    scale_h = max(1, int(h * (1 - prog)))
                    scale_w = max(1, int(w * (1 - prog)))
                    
                    # Prepare final render text for full context as it shrinks
                    card_texture = card_texture.copy()
                    if "Peek" in card.effects:
                        card_texture = palette_swap(card_texture,(255,255,255),(255,200,35))
                    elif card.owner == "demon":
                        card_texture = palette_swap(card_texture,(255,255,255),(200,0,0))
                    elif card.owner == "spooky":
                        card_texture = palette_swap(card_texture,(255,255,255),(200,0,155))
                    text = text_to_surface(str(card.value),'AlmendraSC-Regular',32)
                    ctr = card_texture.get_rect()
                    card_texture.blit(text, text.get_rect(center=(ctr.centerx,ctr.centery-2)))

                    card_texture = pygame.transform.scale(card_texture, (scale_w, scale_h))
                    
                    # Center the shrinking card in its cell
                    slot_x = x * 30 + 10
                    slot_y = y * 40
                    draw_x = slot_x + (w - scale_w) // 2
                    draw_y = slot_y + (h - scale_h) // 2
                    
                    card_surface.blit(card_texture, (draw_x, draw_y))
                    
                elif self.game_state['turn'] == 'SPAWN_CARDS' and hasattr(self, '_spawned_coords') and self._spawned_coords is not None and (x, y) in self._spawned_coords:
                    # Animate Card Spawning (growing outward from center)
                    prog = self.anim['spawn_cards_timer'].get_p()
                    w, h = BaseCard.base_sprite_back.get_size()
                    
                    # Grow effect
                    scale_h = max(1, int(h * prog))
                    scale_w = max(1, int(w * prog))
                    
                    card_texture = BaseCard.base_sprite_back.copy()
                    card_texture = pygame.transform.scale(card_texture, (scale_w, scale_h))
                    
                    # Center the growing card in its cell
                    slot_x = x * 30 + 10
                    slot_y = y * 40
                    draw_x = slot_x + (w - scale_w) // 2
                    draw_y = slot_y + (h - scale_h) // 2
                    
                    card_surface.blit(card_texture, (draw_x, draw_y))
                else:
                    # just do the ol' boring stuff...    
                    if card.flipped or "Peek" in card.effects:
                        card_texture = card_texture.copy()
                        if "Peek" in card.effects:
                            card_texture = palette_swap(card_texture,(255,255,255),(255,200,35))
                        elif card.owner == "demon":
                            card_texture = palette_swap(card_texture,(255,255,255),(200,0,0))    
                        elif card.owner == "spooky":
                            card_texture = palette_swap(card_texture,(255,255,255),(200,0,155))
                        
                        text = text_to_surface(str(card.value),'AlmendraSC-Regular',32)
                        ctr = card_texture.get_rect()
                        
                        card_texture.blit(text, text.get_rect(center=(ctr.centerx,ctr.centery-2)))
                    
                    else:
                        card_texture = BaseCard.base_sprite_back
                        
                    if card.lock:
                        card_texture = AssetLib.get_sprite('cards/lock')
                        #card_texture = palette_swap(card_texture,(255,255,255),(205,90,150))
                
                    card_surface.blit(card_texture,(x*30 + 10,y*40))

        # THE CURSOR.... IS CURSED!
        if self.player.hand_cursor == -1:
            ct_x = cursor_x*30 + 10
            ct_y = cursor_y*40
            
            self.anim["cursor"][0] = lerp(self.anim["cursor"][0], ct_x, 0.2)
            self.anim["cursor"][1] = lerp(self.anim["cursor"][1], ct_y, 0.2)
            
            if abs(self.anim["cursor"][0] - ct_x) < 0.1:
                self.anim["cursor"][0] = ct_x
            if abs(self.anim["cursor"][1] - ct_y) < 0.1:
                self.anim["cursor"][1] = ct_y

            cursor_moving = (self.anim["cursor"][0] != ct_x or 
                            self.anim["cursor"][1] != ct_y)

            draw_x = int(self.anim["cursor"][0])
            draw_y = int(self.anim["cursor"][1])

            if self.game_state['turn'] == "PLAYER":
                if cursor_moving or int(self.delta_time * 4) % 2 == 0:
                    card_surface.blit(AssetLib.get_sprite('cards/select'), (draw_x, draw_y))

        screen.blit(card_surface,(10,10))

        vig_x = -40 + (self.anim["cursor"][0] * 0.2)
        vig_y = -30 + (self.anim["cursor"][1] * 0.2)
        vignette_sprite = AssetLib.get_sprite('vignette')
   
        screen.blit(vignette_sprite, (vig_x,vig_y))

        border_sprite = AssetLib.get_sprite('border')
        pulse = get_live_value(-15, 10, 10000, "breathe")
        
        # Center-scaled blit following the cursor
        scaled_border = pygame.transform.scale(border_sprite, 
            (border_sprite.get_width() + int(pulse), 
             border_sprite.get_height() + int(pulse)))
             
        screen.blit(scaled_border,
            (-30 - pulse/2, -40 - pulse/2))

    def _draw_book(self,screen):
        book = AssetLib.get_sprite("book").copy()
        book.blit(text_to_surface("------------------------------------------","felipa-Regular",10),(20,15))            
        # Helper card stuff
        helper_surface = AssetLib.get_cache("helper_blank")
        if helper_surface is None:
            helper_surface = pygame.Surface((120,18),flags=pygame.SRCALPHA).convert_alpha()
            for index in range(self.player.hand_limit):
                helper_surface.blit(AssetLib.get_sprite('helpers/helper_blank'),(1+index*16 + index,1))
            AssetLib.add_to_cache("helper_blank",helper_surface)
        else:
            helper_surface = AssetLib.get_cache("helper_blank").copy()
            
        for index,value in enumerate(self.player.hand):
            helper_surface.blit(AssetLib.get_sprite(f'helpers/{value.name}'),(1+index*16 + index,1))
        
        # THE CURSOR.... IS CURSED!
        cursor_x = self.player.hand_cursor
        if cursor_x != -1 or self.pending_helper is not None:
            if self.pending_helper is not None:
                cursor_x = self.anim['hand_cursor_index']
            ct_x = cursor_x*16 + cursor_x
            
            self.anim['hand_cursor'] = lerp(self.anim['hand_cursor'], ct_x, 0.2)
            
            if abs(self.anim['hand_cursor'] - ct_x) < 0.1:
                self.anim['hand_cursor'] = ct_x

            cursor_moving = (self.anim['hand_cursor'] != ct_x)

            draw_x = int(self.anim['hand_cursor'])

            if self.game_state['turn'] == "PLAYER":
                if cursor_moving or int(self.delta_time * 4) % 2 == 0:
                    helper_surface.blit(AssetLib.get_sprite('helpers/helper_cursor'), (draw_x, 0))
        # Name/Header
        if self.pending_helper is not None:
            cursor_x = self.anim['hand_cursor_index']
                
        if cursor_x != -1:
            book.blit(text_to_surface(f"{self.player.hand[int(cursor_x)].name.upper():^30}","felipa-Regular",12),(30,5))
        else:
            book.blit(text_to_surface(f"{self.demon.name.upper():^30}","felipa-Regular",12),(30,5))
        
        # Description
        # OK! the text can start at most x=20,y=20!
        description = self.demon.description
        if cursor_x != -1:
            description = self.player.hand[cursor_x].description
            
        for index,value in enumerate(basic_text_wrap(description,36)):
            book.blit(text_to_surface(value,"Tiny5-Regular",8),(20,22 + (index*8)))
        
        book.blit(helper_surface,(25,50))
        
        # Let's add the scales.
        scale_mid = AssetLib.get_sprite('scale_mid')
        scale_surface = pygame.Surface((100,100),flags=pygame.SRCALPHA).convert_alpha()

        human_scale = AssetLib.get_sprite('plate')
        demon_scale = AssetLib.get_sprite('plate')
        
        delta = self.scale.get_delta_score()
        
        delta_move = ((delta  / self.scale.threshold) * 30)
        delta_move = max(-30,min(delta_move,30))

        human_scale_pos = (scale_surface.get_width() // 2 + 30, human_scale.get_height() // 2 + 35 + delta_move)
        demon_scale_pos = (scale_surface.get_width() // 2 - 30, demon_scale.get_height() // 2 + 35 - delta_move)
        
        delta_text = text_to_surface(f"Δ{delta}x")
        pygame.draw.line(scale_surface, (0,0,0), (human_scale_pos[0],human_scale_pos[1]-10),
        (demon_scale_pos[0],demon_scale_pos[1]-10))

        human_size = max(5, 15 + delta//2) 
        demon_size = max(5, 15 - delta//2)

        human_token = pygame.transform.scale(AssetLib.get_sprite('human_token'), (int(human_size), int(human_size)))
        demon_token = pygame.transform.scale(AssetLib.get_sprite('demon_token'), (int(demon_size), int(demon_size)))

        scale_surface.blit(human_token, (human_scale_pos[0] - human_size // 2, human_scale_pos[1] - human_size // 2 + (15 - human_size) / 2))
        scale_surface.blit(demon_token, (demon_scale_pos[0] - demon_size // 2, demon_scale_pos[1] - demon_size // 2 + (15 - demon_size) / 2))

        scale_surface.blit(human_scale,human_scale.get_rect(center=human_scale_pos))
        scale_surface.blit(demon_scale,demon_scale.get_rect(center=demon_scale_pos))

        scale_surface.blit(scale_mid,scale_mid.get_rect(center=(scale_surface.get_width() // 2, scale_surface.get_height() // 2 + 10)))
        scale_surface.blit(delta_text,delta_text.get_rect(center=(scale_surface.get_width() // 2, scale_surface.get_height()- 5)))

        # Draw floating texts
        for ft in self.anim['floating_texts'][:]:
            if ft['timer'].is_finished():
                self.anim['floating_texts'].remove(ft)
                continue
            
            elapsed = pygame.time.get_ticks() - ft['timer'].start_time
            y_offset = -int(get_live_value(0, 10, ft['timer'].duration, "ease_out", elapsed))
            
            # create text surface
            txt_surf = text_to_surface(ft['text'], "Tiny5-Regular", 12, (255, 255, 255), 1, (0, 0, 0))
            
            if ft['side'] == 'player':
                target_pos = (human_scale_pos[0], human_scale_pos[1] + y_offset)
            else:
                target_pos = (demon_scale_pos[0], demon_scale_pos[1] + y_offset)
                
            scale_surface.blit(txt_surf, txt_surf.get_rect(center=target_pos))

        book.blit(scale_surface,(35,65))
        screen.blit(book,(165,0))
        
        surface1 = pygame.Surface((40,40), flags=pygame.SRCALPHA).convert_alpha()
        human_card_icon = AssetLib.get_sprite("card_icon")
        demon_card_icon = palette_swap(AssetLib.get_sprite("card_icon"),(255,255,255),(255,0,0))

        surface1.blit(palette_swap(demon_card_icon,(0,255,0),(255,255,255)),(0,0))
        surface1.blit(text_to_surface(f"x{len(self.demon.deck)}"),(14,0))

        surface1.blit(text_to_surface(f"x{len(self.player.deck)}"),(14,15))
        surface1.blit(human_card_icon,(0,15))
        
        swapped_s1 = palette_swap(surface1,(0,255,0),(255,255,255))
        swapped_s1.set_colorkey((255,255,255))
        screen.blit(swapped_s1,(185,150))

        offset = get_live_value(0,5,5000,"breathe")
        rv = AssetLib.get_sprite('right_vig')
        screen.blit(pygame.transform.scale(rv,(rv.get_size()[0]+offset,rv.get_size()[1]+offset)),(165-offset/2,0-offset/2))

    def draw(self, screen):
        '''Called for rendering the scene.'''
        # clear screen each frame
        screen.fill((0, 0, 0))

        self._draw_grid(screen)
        self._draw_book(screen)

        if self.scale.who_won() != None:
            win_surf = None
            if self.scale.who_won() == "player":
                win_surf = text_to_surface("You Won!","Jacquard24-Regular",32,(255,255,255),2,(0,0,0))
            elif self.scale.who_won() == "demon":
                win_surf = text_to_surface("You Lose...","Jacquard24-Regular",32,(255,0,0),2,(0,0,0))
            
            win_rect = win_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(win_surf, win_rect)
        
        # ========= The part for fading lol ======== #
        dithers = [0,7,4,3,6,1,5,2]
        if not self.anim['fade_in_timer'].is_finished():
            p = self.anim['fade_in_timer'].get_p()
            index = min(int(p * len(dithers)), len(dithers) - 1)
            cf = dithers[index]
            if cf == 0:
                screen.fill((0,0,0))
            else:
                screen.blit(AssetLib.get_sprite(f"dither_screen{cf}"),(0,0))
                
        if self.change_scenes and self.anim['fade_out_timer'] is not None and self.anim['fade_out_timer'].is_finished():
            screen.fill((0,0,0))
        else:
            if self.anim['fade_out_timer'] != None:
                p = self.anim['fade_out_timer'].get_p()
                index = min(int(p * len(dithers)), len(dithers) - 1)
                cf = dithers[-index]
                if cf != 0:
                    screen.blit(AssetLib.get_sprite(f"dither_screen{cf}"),(0,0))
