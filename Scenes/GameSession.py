from .BaseScene import Scene
from Objects import Grid, Scale, Timer
from BaseCard import *
from HelperCard import *

from Players import *
from GraphicHelper import *

import random
import math
import pygame

# note to self: when coding, we must think that this file exists at the "root" of the project ( or where we place our main )
class GameSession(Scene):
    def __init__(self):
        # CORE
        GRID_SIZE = 4
        self.scale = Scale(20)
        self.grid = Grid(GRID_SIZE)
        self.countdown = 0
        self.delta_time = 0

        # Players
        normal_val = [1, 2, 3]

        self.player = Player(
            deck=BaseCard.deck_creator([18, 4, 2], normal_val, "player"),
            helper_cards=helpers,
            hand=[]
        )
        self.player.hand_limit = 10

        self.demons = [
            #Demon("Imp", "An annoying low-level demon", BaseCard.deck_creator([16, 6, 2], normal_val, "demon"))
            #Abigor(BaseCard.deck_creator([16, 6, 2], normal_val, "demon"))
            # Baphomet(BaseCard.deck_creator([16, 6, 2], normal_val, "demon"))
            #Zariel(BaseCard.deck_creator([16, 6, 2], normal_val, "demon"))
            Imp(BaseCard.deck_creator([16, 6, 2], normal_val, "demon"),[Lock, TwoTime])
        ]

        # STATES
        self.game_state = {
            "turn": "PLAYER",
            "player": self.player,
            "grid": self.grid,
            "demon": self.demons[0],
            "scale": self.scale
        }

        self.data_to_evaluate = None
        '''
        {
            "valid_cards": valid_cards,
            "combos": combos,
            player": "player"  # or "demon"
        }
        '''
        self.helpers_to_eval = []

        # ANIMATION!
        self.anim = {
            "fade_in_timer": Timer(1000),
            "cursor":[0,0],
            "vignette":[0,0],
            "card_flip": 0.5,
            "card_flip_timer":None
        }

        # Cute assets <3
        BaseCard.load_graphics()

    def demon_turn(self):
        choice_type, data = self.demons[0].decide(self.grid)
        match choice_type:
            case "CARD":
                x,y= self.grid.get_coords_from_object(data)
                valid_cards, combos = self.grid.select_attempt(x,y)
                if len(valid_cards) != 0 :
                    self.data_to_evaluate = {
                        "valid_cards": valid_cards,
                        "combos": combos,
                        "player": "demon"  # or "demon"
                    }
                    self.anim['card_flip_timer'] = Timer(self.anim['card_flip']*1000)
            case "ACTION":
                print(f"The demon uses {data}")
                if data.verify(self.game_state):
                    # then it's OK
                    #self.helpers_to_eval.append(data)
                    data.play(self.game_state)
                    self.helpers_to_eval.append(data)
                else:
                    print(" The demon passed it's turn.")
        
        self.game_state['turn'] = 'EVALUATE'

    def enter(self):
        '''
        Called once when entering this state.
        Reset music, set player positions, etc.
        For loading assets or heavy stuff, it is advisable to load via __init__ instead.
        '''
        # Now, pick cards from it equally.
        amount = (self.grid.size**2)//2
        select_cards = self.player.choose_and_remove(amount) + self.demons[0].choose_and_remove(amount)
        
        random.shuffle(select_cards)
        grid_coords = self.grid.get_all_coords()

        for i in select_cards:
            i.x = grid_coords[0]
            i.y = grid_coords[1]

        self.grid.set_tiles_from_coords(
            grid_coords,select_cards
        )

    def exit(self):
        '''
        Called once when leaving this state.
        Clean up the scene, preparing for a new one.
        '''
        pass
    
    def handle_input(self, events):
        for event in events:
            if self.game_state['turn'] == 'PLAYER' and event.type == pygame.KEYDOWN:

                keys = pygame.key.get_pressed()
                self.player.grid_move = any([
                    keys[pygame.K_UP],
                    keys[pygame.K_DOWN],
                    keys[pygame.K_LEFT],
                    keys[pygame.K_RIGHT]
                ])
                self.player.get_pos_in_grid(events, self.grid.size)
                ##############
                if event.key == pygame.K_SPACE:
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
                        if self.player.picked_helper == False and len(self.player.hand) < self.player.hand_limit:
                            print("Giving player...")
                            self.player.hand.append(self.player.choose_helper())

                        self.player.picked_helper = False

                if event.key == pygame.K_0:
                    if len(self.player.hand) != 0 and self.player.hand[0].verify(self.game_state):
                        self.player.picked_helper = True
                        card = self.player.hand.pop(0)
                        card.play(self.game_state)
                        self.helpers_to_eval.append(card) 
            self.player.grid_move = False         
        return self
    
    def evaluate(self):
        '''
        this evaluates the card that has picked AND run helper's commands :3c
        '''
        
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
        target = self.demons[0]
        if raw["player"] == "player":
            target = self.player

        # if not win..
        if self.scale.who_won() == None:
            if raw["player"] == "player":
                self.game_state['turn'] = 'DEMON'
            else:
                self.game_state['turn'] = 'PLAYER'
        else:
            self.game_state['turn'] = 'HANG'

        # Now, CLEAN!
        if raw["combos"] > 0:
            self.grid.replace_cards(Grid.flatten_list(raw['valid_cards'][1:]),target)

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
        match self.game_state["turn"]:
            case "DEMON":
                self.demon_turn()

            case "EVALUATE": # The game checker each turn...
                # Now, I think I'll cheat the card flip animation here.
                if self.countdown >= 0.5:
                    self.evaluate()
                    self.countdown = 0
                self.countdown += dt

            case "HANG":
                if self.countdown >= 2:
                    print("Aye aye!")
                    return GameSession()
                self.countdown += dt
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
                if self.data_to_evaluate != None and card in self.data_to_evaluate["valid_cards"]:
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
    
                    if self.anim['card_flip_timer'].is_finished():
                        self.anim['card_flip_timer'] = None
                else:
                    # just do the ol' boring stuff...        
                    if card.owner == "spooky":
                        card_texture = palette_swap(card_texture,(255,255,255),(200,0,155))

                    if card.flipped or "Peek" in card.effects:
                        card_texture = card_texture.copy()
                        text = text_to_surface(str(card.value),'AlmendraSC-Regular',32)
                        ctr = card_texture.get_rect()
                        card_texture.blit(text, text.get_rect(center=(ctr.centerx,ctr.centery-2)))
                        
                        if card.owner == "demon":
                            card_texture = palette_swap(card_texture,(255,255,255),(200,0,0))
                    else:
                        card_texture = BaseCard.base_sprite_back
                        
                    if card.lock:
                        card_texture = AssetLib.get_sprite('cards/lock')
                        card_texture = palette_swap(card_texture,(255,255,255),(205,90,150))
                
                    card_surface.blit(card_texture,(x*30 + 10,y*40))

        # THE CURSOR.... IS CURSED!
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
        book = AssetLib.get_sprite("book") 
        # text can start at x=20
        book.blit(text_to_surface("LESSONS IN MAGIC","felipa-Regular",12),(30,5))
        book.blit(text_to_surface("------------------------------------------","felipa-Regular",10),(20,15))
        book.blit(text_to_surface("Arrow keys to move cursor.","Tiny5-Regular",10),(20,20))
        
        # Let's add the scales.
        scale_mid = AssetLib.get_sprite('scale_mid').convert_alpha()
        scale_surface = pygame.Surface((100,100),flags=pygame.SRCALPHA).convert_alpha()
        scale_surface.fill((155,0,155))
        human_scale = AssetLib.get_sprite('plate').convert_alpha()
        demon_scale = AssetLib.get_sprite('plate').convert_alpha()
        
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

        book.blit(scale_surface,(30,70))
        screen.blit(book,(165,0))

        offset = get_live_value(0,5,5000,"breathe")
        rv = AssetLib.get_sprite('right_vig')
        screen.blit(pygame.transform.scale(rv,(rv.get_size()[0]+offset,rv.get_size()[1]+offset)),(165-offset/2,0-offset/2))

    def draw(self, screen):
        '''Called for rendering the scene.'''
        # clear screen each frame
        screen.fill((0, 0, 0))

        self._draw_grid(screen)
        self._draw_book(screen)
        
        if self.scale.who_won() == "player":
            screen.blit(text_to_surface("You Win!"),(100,60))   
        elif self.scale.who_won() == "demon":
            screen.blit(text_to_surface("You Lose!"),(100,60))
        
        # ========= The part for fading lol ======== #
        
        if not self.anim['fade_in_timer'].is_finished():
            dithers = [0,7,4,3,6,1,5,2]
            p = self.anim['fade_in_timer'].get_p()
            index = min(int(p * len(dithers)), len(dithers) - 1)
            cf = dithers[index]
            if cf == 0:
                screen.fill((0,0,0))
            else:
                screen.blit(AssetLib.get_sprite(f"dither_screen{cf}"),(0,0))
