from .BaseScene import Scene
from Objects import Grid, Scale
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
        self.scale = Scale(20)

        GRID_SIZE = 4
        self.grid = Grid(GRID_SIZE)

        normal_val= [1,2,3]

        self.player = Player(deck=BaseCard.deck_creator([18,4,2],normal_val,"player"),helper_cards=helpers,hand=[])
        self.player.hand_limit = 10
        self.demons = [
           Demon("Imp","An annoying low-level demon",BaseCard.deck_creator([16,6,2],normal_val,"demon"))
           #Abigor(BaseCard.deck_creator([16,6,2],normal_val,"demon"))
           #Baphomet(BaseCard.deck_creator([16,6,2],normal_val,"demon"))
           #Zariel(BaseCard.deck_creator([16,6,2],normal_val,"demon"))
        ]

        #self.SPOOKY = BaseCard.deck_creator([14,8,2],[-1,-2,-3],"spooky")
        self.countdown = 0

        self.data_to_evaluate = None
        '''
        {
            "valid_cards": valid_cards,
            "combos": combos,
            "player": "player"  # or "demon"
        }
        '''

        self.game_state = { 
            "turn":"PLAYER",
            "player":self.player,
            "grid":self.grid,
            "demon":self.demons[0],
            "scale":self.scale
        }

        # Queue for executing card stuff ig..
        self.helpers_to_eval = []

        self.delta_time = 0
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
                    
                    self.game_state['turn'] = 'EVALUATE'
            case "ACTION":
                self.helpers_to_eval.append(data)

    #########################################################
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
        '''
        for _ in range(16):
            self.player.hand.append(Lock())
        pass
        '''

    def exit(self):
        '''
        Called once when leaving this state.
        Clean up the scene, preparing for a new one.
        '''
        pass
    
    def handle_input(self, events):
        ''' Process keys. Returns 'self' or a NEW Scene.'''
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
        raw = self.data_to_evaluate
        #print(f"evaluating {raw['player']} {raw['valid_cards']}")
        for i in self.helpers_to_eval:
            i.play_on_eval(self.game_state)
            # bruhhh

        if self.data_to_evaluate == None:
            print("NOTHING TO EVALUATE!")
        else:
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

        # Now, I think I could make a "timer" for it...
        helpers_copy = self.helpers_to_eval.copy()
        for helper in helpers_copy:
            if helper.remove_check(self.game_state):
                print("OK REMOVE: ",helper)
                try:
                    print(f"Cleaning: {helper.name}")
                    helper.clean_up(self.game_state)
                except Exception as e:
                    print(f"ERROR! {helper}",e,)
                self.helpers_to_eval.remove(helper)
            else:
                print("NG: ",helper)

        helpers_copy = [] # just clear...

            #self.helpers_to_eval = []
            
    def update(self, dt):
        '''
        Called every frame. Returns new State or None.
        Move things, check timers.
        '''
        match self.game_state["turn"]:
            case "DEMON":
                self.demon_turn()

            case "EVALUATE": # The game checker each turn...
                self.evaluate()

            case "HANG":
                if self.countdown >= 2:
                    print("Aye aye!")
                    return GameSession()
                self.countdown += dt
        self.delta_time += dt
        return None

    def draw(self, screen):
        '''Called for rendering the scene.'''
        # clear screen each frame
        screen.fill((0, 0, 0))

        #region ========================= CARDS =========================
        cursor_x = self.player.cursor_x
        cursor_y = self.player.cursor_y
        # First, let's layer the parallax.
        screen.blit(
            AssetLib.get_sprite('wood'),
            (0,0)
        )
        card_surface = pygame.Surface((200,200),flags=pygame.SRCALPHA).convert_alpha()
        card_surface.fill((0,0,0,0))
        
        # Now, blit the BaseCard things.
        for y in range(self.grid.size):
            for x in range(self.grid.size):
                card = self.grid.grid[y][x]
                card_texture = BaseCard.base_sprite_front
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

        if int(self.delta_time * 4) % 2 == 0:
            card_surface.blit(AssetLib.get_sprite('cards/select'),(cursor_x*30 + 10,cursor_y*40))
        
        screen.blit(card_surface,(10,10))

        screen.blit(
            palette_swap(AssetLib.get_sprite('vignette'),(255,255,255),(0,0,0,0)),
            (-30,
            -40))        
        screen.blit(
            palette_swap(AssetLib.get_sprite('border'),(255,255,255),(0,0,0,0)),
            (-30,
            -40))
        #endregion ========================= **** =========================
        
        #region ================= RIGHT BOX =========================
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
        
        #scale_surface.blit(AssetLib.get_sprite('human_token'),human_scale.get_rect(center=human_scale_pos))
        #scale_surface.blit(AssetLib.get_sprite('demon_token'),demon_scale.get_rect(center=demon_scale_pos))

        scale_surface.blit(human_scale,human_scale.get_rect(center=human_scale_pos))
        scale_surface.blit(demon_scale,demon_scale.get_rect(center=demon_scale_pos))



        scale_surface.blit(scale_mid,scale_mid.get_rect(center=(scale_surface.get_width() // 2, scale_surface.get_height() // 2 + 10)))
        scale_surface.blit(delta_text,delta_text.get_rect(center=(scale_surface.get_width() // 2, scale_surface.get_height()- 5)))

        

        book.blit(scale_surface,(20,50))

        screen.blit(book,(165,0))
        #screen.blit(palette_swap(AssetLib.get_sprite('right_vig'),(255,255,255),(0,0,0,0)),(165,0))  
        #endregion ========================= **** =========================
        if self.scale.who_won() == "player":
            screen.blit(text_to_surface("You Win!"),(100,60))   
        elif self.scale.who_won() == "demon":
            screen.blit(text_to_surface("You Lose!"),(100,60))
