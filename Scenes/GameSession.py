from .BaseScene import Scene
from Objects import Grid
from Cards import BaseCard, HelperCard
from Players import Demon, Player

import random
import pygame

# note to self: when coding, we must think that this file exists at the "root" of the project ( or where we place our main )
class GameSession(Scene):
    def __init__(self):
        self.game_state = { 
            "turn":"PLAYER",
            "player_score":0,
            "demon_score":0,
        }

        GRID_SIZE = 4
        self.grid = Grid(GRID_SIZE)

        normal_val= [1,2,3]
        self.player = Player(deck=BaseCard.deck_creator([12,8,4],normal_val,"player"))
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

        self.SPOOKY = BaseCard.deck_creator([14,8,2],[-1,-2,-3],"spooky")
        self.session_cards = {
            "player":[],
            "demon":[]
        }
    
    def palette_swap(self,surf, old_c, new_c):
        img_copy = pygame.Surface(surf.get_size())
        img_copy.fill(new_c)
        surf.set_colorkey(old_c)
        img_copy.blit(surf, (0, 0))
        return img_copy

    def enter(self):
        '''
        Called once when entering this state.
        Reset music, set player positions, etc.
        For loading assets or heavy stuff, it is advisable to load via __init__ instead.
        '''
        self.session_cards = {
            "player":self.player.deck,
            "demon":self.demons[0].deck
        }

         # Now, pick cards from it equally.
        select_cards = self.choose_and_remove('player',8) + self.choose_and_remove('demon',8)
        
        random.shuffle(select_cards)
        grid_coords = self.grid.get_all_coords()

        for i in select_cards:
            i.x = grid_coords[0]
            i.y = grid_coords[1]

        self.grid.set_tiles_from_coords(
            grid_coords,select_cards
        )

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
                    if event.key == pygame.K_UP and self.player.cursor_y != 0:
                        self.player.cursor_y -= 1
                    elif event.key == pygame.K_DOWN and self.player.cursor_y != self.grid.size-1:
                        self.player.cursor_y += 1
                    
                    if event.key == pygame.K_LEFT and self.player.cursor_x != 0:
                        self.player.cursor_x -= 1
                    elif event.key == pygame.K_RIGHT and self.player.cursor_x != self.grid.size-1:
                        self.player.cursor_x += 1
                    
                    ##############
                    if event.key == pygame.K_SPACE:
                        # try to select the BaseCard
                        #self.game_state['scale'] 
                        valid_cards, combos = self.grid.select_attempt(self.player.cursor_x,self.player.cursor_y)
                        if len(valid_cards) != 0:
                            # OK! change to next player turn...
                            self.evaluate_points(valid_cards,"player_score")
                            if combos > 0:
                                arr = []
                                arr.append(valid_cards[0])
                                arr.extend(valid_cards[1])
                                arr.extend(valid_cards[2])
                                self.replace_cards(arr,"player")
                            self.game_state['turn'] = 'DEMON'
                        pass
        return self
    def demon_turn(self):
        choice_type, data = self.demons[0].decide(self.grid)
        match choice_type:
            case "CARD":
                x,y= self.grid.get_coords_from_object(data)
                valid_cards, combos = self.grid.select_attempt(x,y)
                if len(valid_cards) != 0 :
                    # OK! change to next player turn...
                    self.evaluate_points(valid_cards,"demon_score")
                    if combos > 0:
                        arr = []
                        arr.append(valid_cards[0])
                        arr.extend(valid_cards[1])
                        arr.extend(valid_cards[2])
                        self.replace_cards(arr,"demon")
                    self.game_state['turn'] = 'PLAYER'

    def evaluate_points(self,raw_cards,player):
        # might be the stupidest way to do ts
        for i in raw_cards:
            if isinstance(i,BaseCard):
                self.game_state[player] += i.value
            # or maybe it's actually an array of cards!
            else:
                s = 0
                for individual_card in i:
                    self.game_state[player] += individual_card.value
                    s += individual_card.value

                # Bonus!
                self.game_state[player] += 5

    def replace_cards(self,raw_cards,player):
        s = Grid.count_nested_items(raw_cards)
        new_cards = self.choose_and_remove(player, s)
        coords = self.grid.get_coords_from_tiles(raw_cards)
        print(len(raw_cards),new_cards,coords)
        self.grid.set_tiles_from_coords(coords,new_cards)

    def choose_and_remove(self,player, amount):
        arr = []
        for i in range(amount):
            c = None
            if len(self.session_cards[player]) == 0: # No more left...
                # create spooky deck
                c = random.choice(self.SPOOKY)
                c.flipped = False
            else:
                c = random.choice(self.session_cards[player])
                self.session_cards[player].remove(c)

            arr.append(c)

        return arr

    def update(self, dt):
        '''
        Called every frame. Returns new State or None.
        Move things, check timers.
        '''
        if self.game_state["turn"] == "DEMON":
            # ask the Demon
            self.demon_turn()
        return None

    def draw(self, screen):
        '''Called for rendering the scene.'''
        cursor_x = self.player.cursor_x
        cursor_y = self.player.cursor_y

        card_surface = pygame.Surface((200,200))

        font = pygame.font.Font(None, 16) # load default font

        screen.fill((255, 255, 255))          # clear screen each frame
        card_surface.fill((255,255,255))

        c_text = font.render(f"{cursor_x,cursor_y}\nplayer:{self.game_state['player_score']}\ndemon:{self.game_state['demon_score']}\ndelta:{self.game_state['player_score']-self.game_state['demon_score']}\nturn:{self.game_state['turn']}"
        , True, (0,0,0)) # create text surface  
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
                

        card_surface.blit(self.CARD_TEXTURES['select'],(cursor_x*20 + 10,cursor_y*30))

        screen.blit(card_surface)
        screen.blit(c_text,(100,10))    
        pass
