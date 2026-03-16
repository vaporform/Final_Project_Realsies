import pygame
import random
from Objects import Grid
from Cards import BaseCard, HelperCard
from Players import Demon, Player

class Game:
    def __init__(self):
        '''
        Initialize the game.
        '''
        pygame.init() # Inititalize the game!
        self.render_resolution = (320,180)
        self.screen_resolution = (640,480)

        # The actual screen that the user will see.
        self.screen = pygame.display.set_mode(self.render_resolution,
                                            pygame.SCALED,
                                            vsync=1)

        pygame.display.set_caption("Game")
        self.clock = pygame.time.Clock()
        self.running = True

        ###############################
        # Now, the game stuff!
        self.game_state = { 
            "turn":"PLAYER",
            "player_score":0,
            "demon_score":0,
        }

        GRID_SIZE = 4
        self.grid = Grid(GRID_SIZE, [BaseCard(random.randint(1,3),i%GRID_SIZE, i//GRID_SIZE) for i in range(GRID_SIZE**2)])

        self.player = Player(deck=BaseCard.deck_creator(12,8,4,"Player"))
        self.demons = [
            Demon("Imp","An annoying low-level demon",BaseCard.deck_creator(16,6,2,"Demon"))
        ]

        self.CARD_TEXTURES = {
            "backside":pygame.image.load("assets/sprites/cards/test.png").convert(),
            "select":pygame.image.load("assets/sprites/cards/select.png").convert_alpha(),
            "1":pygame.image.load("assets/sprites/cards/1.png").convert(),
            "2":pygame.image.load("assets/sprites/cards/2.png").convert(),
            "3":pygame.image.load("assets/sprites/cards/3.png").convert(),
        }

        self.session_
    def update_system_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

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
                        valid_cards = self.grid.select_attempt(self.player.cursor_x,self.player.cursor_y)
                        if valid_cards != None:
                            # OK! change to next player turn...
                            self.evaluate_points(valid_cards,"player_score")
                            self.game_state['turn'] = 'DEMON'
                        pass

    def demon_turn(self):
        choice_type, data = self.demons[0].decide(self.grid)
        match choice_type:
            case "CARD":
                x,y= self.grid.get_coords_from_tiles(data)
                valid_cards = self.grid.select_attempt(x,y)
                if valid_cards != None :
                    # OK! change to next player turn...
                    self.evaluate_points(valid_cards,"demon_score")
                    self.game_state['turn'] = 'PLAYER'

    def evaluate_points(self,raw_cards,score):
        # might be the stupidest way to do ts
        for i in raw_cards:
            if isinstance(i,BaseCard):
                self.game_state[score] += i.value
            # or maybe it's actually an array of cards!
            else:
                s = 0
                for individual_card in i:
                    self.game_state[score] += individual_card.value
                    s += individual_card.value

                # Bonus!
                self.game_state[score] += 5
        
        pass

    def run(self):
        '''
        Run the game
        
        :param self: Description
        '''
        while self.running:
            self.update_system_events()
            # now for demons...
            if self.game_state["turn"] == "DEMON":
                # ask the Demon
                self.demon_turn()

            self.render()   
            self.clock.tick(24)
        pygame.quit()
    
    def render(self):
        cursor_x = self.player.cursor_x
        cursor_y = self.player.cursor_y

        card_surface = pygame.Surface((200,200))

        font = pygame.font.Font(None, 16) # load default font

        self.screen.fill((255, 255, 255))          # clear screen each frame
        card_surface.fill((255,255,255))
        c_text = font.render(f"{cursor_x,cursor_y}\nplayer:{self.game_state['player_score']}\ndemon:{self.game_state['demon_score']}\ndelta:{self.game_state['player_score']-self.game_state['demon_score']}\nturn:{self.game_state['turn']}", True, (0,0,0)) # create text surface  
        # Now, blit the BaseCard things.
        for y in range(self.grid.size):
            for x in range(self.grid.size):
                card = self.grid.grid[y][x]
                if card.flipped:
                    card_surface.blit(self.CARD_TEXTURES[str(card.value)], (x*20 + 10,y*30))
                else:
                    card_surface.blit(self.CARD_TEXTURES['backside'], (x*20 + 10,y*30))

        card_surface.blit(self.CARD_TEXTURES['select'],(cursor_x*20 + 10,cursor_y*30))

        self.screen.blit(card_surface)
        self.screen.blit(c_text,(100,10))    
        pygame.display.flip()            # push frame to screen

# Start the game!
game = Game()
game.run()