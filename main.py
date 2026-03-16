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

        self.player = Player()
        self.demons = [
            Demon("Imp","An annoying low-level demon")
        ]

        self.CARD_TEXTURES = {
    "backside":pygame.image.load("assets/sprites/cards/test.png").convert(),
    "select":pygame.image.load("assets/sprites/cards/select.png").convert_alpha(),
    "1":pygame.image.load("assets/sprites/cards/1.png").convert(),
    "2":pygame.image.load("assets/sprites/cards/2.png").convert(),
    "3":pygame.image.load("assets/sprites/cards/3.png").convert(),
}
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
                        attempt, points = self.select_attempt(self.player.cursor_x,self.player.cursor_y)
                        if attempt:
                            # OK! change to next player turn...
                            self.game_state['player_score'] += points
                            self.game_state['turn'] = 'DEMON'
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
                choice_type, data = self.demons[0].decide(self.grid)
                match choice_type:
                    case "CARD":
                        x,y = self.grid.get_coords_from_tiles(data)
                        attempt, points = self.select_attempt(x,y)
                        if attempt:
                            # OK! change to next player turn...
                            self.game_state['demon_score'] += points
                            self.game_state['turn'] = 'PLAYER'

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
        
        c_text = font.render(f"{cursor_x,cursor_y}\nplayer:{self.game_state['player_score']}\ndemon:{self.game_state['demon_score']}\nturn:{self.game_state['turn']}", True, (0,0,0)) # create text surface
        
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

    def select_attempt(self,x,y):
        cursor_x = x
        cursor_y = y
        points = 0
        
        try:
            selected = self.grid.get_item(cursor_x,cursor_y)
        except Exception:
            print("ERROR!")
            return False, points

        if not selected.flipped:
            points += selected.value
            selected.flip()

            # now check for combos
            row_coords, col_coords = self.grid.get_related_coords(cursor_x,cursor_y)
            row_cards,_  = self.grid.get_tiles_from_coords(row_coords)
            col_cards,_ = self.grid.get_tiles_from_coords(col_coords)

            new_cards = []
            valid_coords = []

            if sum([int(b.flipped) for b in col_cards]) == self.grid.size: #OK!
                for i in col_coords:
                    if i not in valid_coords:
                        valid_coords.append(i)
        
            if sum([int(b.flipped) for b in row_cards]) == self.grid.size: #OK!
                for i in row_coords:
                    if i not in valid_coords:
                        valid_coords.append(i)
            
            for i in valid_coords:
                card = BaseCard(random.randint(1,3), i[0], i[1])
                new_cards.append(card)
            
            self.grid.set_tiles_from_coords(valid_coords,new_cards)
            
            return True, points
        return False, points

# Start the game!
game = Game()
game.run()