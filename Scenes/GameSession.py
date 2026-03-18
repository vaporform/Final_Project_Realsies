from .BaseScene import Scene
from Objects import Grid, Scale
from BaseCard import *
from HelperCard import *

from Players import *

import random
import pygame

# note to self: when coding, we must think that this file exists at the "root" of the project ( or where we place our main )
class GameSession(Scene):
    def __init__(self):
        self.scale = Scale(50)

        GRID_SIZE = 4
        self.grid = Grid(GRID_SIZE)

        normal_val= [1,2,3]
        helpers = [
            Peek(), 
        ]

        self.player = Player(deck=BaseCard.deck_creator([18,4,2],normal_val,"player"),
                            helper_cards=helpers,
                            hand=[]
                            )

        self.demons = [
            Demon("Imp","An annoying low-level demon",BaseCard.deck_creator([16,6,2],normal_val,"demon"))
        ]

        self.CARD_TEXTURES = {
            "backside":pygame.image.load("assets/sprites/cards/test.png").convert(),
            "select":pygame.image.load("assets/sprites/cards/select.png").convert_alpha(),
            "1":pygame.image.load("assets/sprites/cards/1.png").convert(),
            "2":pygame.image.load("assets/sprites/cards/2.png").convert(),
            "3":pygame.image.load("assets/sprites/cards/3.png").convert(),
        }

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
        
    def palette_swap(self,surf, old_c, new_c):
        img_copy = pygame.Surface(surf.get_size())
        img_copy.fill(new_c)
        surf.set_colorkey(old_c)
        img_copy.blit(surf, (0, 0))
        return img_copy

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

        self.player.hand.append(Peek())
        pass

    def exit(self):
        '''
        Called once when leaving this state.
        Clean up the scene, preparing for a new one.
        '''
        pass
    
    def handle_input(self, events):
        ''' Process keys. Returns 'self' or a NEW Scene.'''
        for event in events:
            if self.game_state['turn'] == 'PLAYER':
                if event.type == pygame.KEYDOWN:
                    # DIR STUFF...
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
                            self.player.hand.append(Peek())

                    if event.key == pygame.K_0:
                        if len(self.player.hand) != 0 and self.player.hand[0].verify(self.game_state):
                            card = self.player.hand.pop(0)
                            card.play(self.game_state)
                            self.helpers_to_eval.append(card)            
        return self
    
    def evaluate(self):
        raw = self.data_to_evaluate
        #print(f"evaluating {raw['player']} {raw['valid_cards']}")
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
            for helper in self.helpers_to_eval:
                try:
                    print(f"Cleaning: {helper.name}")
                    helper.clean_up(self.game_state)
                except Exception as e:
                    print(f"ERROR! {helper}",e,)
            
            if raw["combos"] > 0:
                self.grid.replace_cards(Grid.flatten_list(raw['valid_cards'][1:]),target)

            self.data_to_evaluate = None

            # Now, I think I could make a "timer" for it...
            helpers_copy = self.helpers_to_eval.copy()
            for i in helpers_copy:
                if i.remove_check(self.game_state):
                    self.helpers_to_eval.remove(i)

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
        return None

    def draw(self, screen):
        '''Called for rendering the scene.'''
        cursor_x = self.player.cursor_x
        cursor_y = self.player.cursor_y

        card_surface = pygame.Surface((200,200))

        font = pygame.font.Font(None, 16) # load default font

        screen.fill((255, 255, 255))          # clear screen each frame
        card_surface.fill((255,255,255))

        c_text = font.render(f"{cursor_x,cursor_y}\nplayer:{self.scale.player_score, len(self.player.session_deck)}\ndemon:{self.scale.demon_score,  len(self.demons[0].session_deck)}\ndelta:{self.scale.get_delta_score()}\nturn:{self.game_state['turn']}"
        , True, (0,0,0)) # create text surface

        hand_text = ""
        for i in self.player.hand:
            hand_text += f"{i} "
        h_text = font.render(hand_text, True, (0,0,0))
        e_text = font.render(f"effects: {','.join(self.grid.get_item(cursor_x,cursor_y).effects)}\neval:{self.helpers_to_eval}"
        , True, (0,0,0))
        # Now, blit the BaseCard things.
        for y in range(self.grid.size):
            for x in range(self.grid.size):
                card = self.grid.grid[y][x]
                if card.flipped:
                    if card.owner == "demon":
                        card_surface.blit(self.palette_swap(self.CARD_TEXTURES[str(card.value)],(255,255,255),(200,0,0))
                        , (x*20 + 10,y*30))
                    elif card.owner == "spooky":
                        card_surface.blit(self.palette_swap(self.CARD_TEXTURES[str(abs(card.value))],(255,255,255),(200,0,155))
                        , (x*20 + 10,y*30))
                    else:
                        card_surface.blit(self.CARD_TEXTURES[str(card.value)]
                        , (x*20 + 10,y*30))
                else:
                    card_surface.blit(self.CARD_TEXTURES['backside'], (x*20 + 10,y*30))
                    if card.owner == "spooky":
                        card_surface.blit(self.palette_swap(self.CARD_TEXTURES['backside'],(255,255,255),(200,0,155)), (x*20 + 10,y*30))
                
                if "Peek" in card.effects:
                    card_surface.blit(self.palette_swap(self.CARD_TEXTURES[str(abs(card.value))],(255,255,255),(205,90,150))
                        , (x*20 + 10,y*30))

        card_surface.blit(self.CARD_TEXTURES['select'],(cursor_x*20 + 10,cursor_y*30))

        screen.blit(card_surface)
        screen.blit(c_text,(100,10))
        screen.blit(h_text,(100,80))
        screen.blit(e_text,(100,100))
        if self.scale.who_won() == "player":
            screen.blit(font.render("you win",True, (0,0,0)),(100,60))   
        elif self.scale.who_won() == "demon":
            screen.blit(font.render("you lose",True, (0,0,0)),(100,60))