class Grid:
    def __init__(self, size,thing=1):
        self.size = size
        self.grid = self.create_grid(self.size,thing)
    
    def create_grid(self,size,thing=1):       
        temp_grid = []
        # create cards.
        for i in range(size):
            if isinstance(thing,list):
                temp_grid.append(
                    [thing[j+(i*size)] for j in range(size)]
                )
            else:
                temp_grid.append(
                    [thing for j in range(size)]
                )
        return temp_grid
    
    def get_item(self,x,y): # just grab the item at index lol 
        return self.grid[y][x]

    def get_related_coords(self,x,y): 
        # get related row and columns
        row = [[i,y] for i in range(self.size)]
        column = [[x,i] for i in range(self.size)]

        # get diagonals
        #diag_to_left = [grid.get_item(x,i)]
        return row, column
    
    def get_tiles_from_coords(self, coords):
        temp = []
        errors = 0
        for coord in coords:
            try:
                x,y = coord[0], coord[1]
                temp.append(self.get_item(x,y))
            except Exception:
                # founds an error
                errors += 1
        
        return temp, errors

    def set_tiles_from_coords(self, coords, items):
        errors = 0
        for index, coord in enumerate(coords):
            try:
                x,y = coord[0], coord[1]
                self.grid[y][x] = items[index]
            except Exception as e:
                # founds an error
                print(f"err {index}, {coord} {items[index]}",e)
                errors += 1
        
        return errors
    
class BaseCard:
    def __init__(self, value=1, x=0,y=0):
        self.flipped = False
        self.value = value
        # Additional info
        self.x = x
        self.y = y
    
    def flip(self):
        self.flipped = not self.flipped

class HelperCard:
    def __init__(self, n, d):
        self.name = n
        self.description = d
    
    def play(self, game_state):
        pass

class Player:
    def __init__(self,deck=[],hand=[]):
        self.deck = deck
        self.hand = hand
    
    def get_input(self):
        pass

class Demon(Player):
    def __init__(self, deck=[], hand=[]):
        super().__init__(deck,hand)
        pass

    def get_input(self): # Method Overriding!
        # maybe decide?
        pass

class Scale:
    def __init__(self, ts=0):
        self.player_score = 0
        self.demon_score = 0
    
        self.threshold = ts

    def get_delta_score(self):
        return self.player_score - self.demon_score
    
    def is_win(self):
        pass

class Game:
    def __init__(self):
        self.game_state:string
        self.turn:string
    
    def change_scene(self):
        pass

if __name__ == "__main__":
    import pygame
    
    a = Grid(4)
    print(a.grid)

    background_colour = (255,255,255)
    (width, height) = (300, 200)
    screen = pygame.display.set_mode((width, height))

    screen.fill(background_colour)
    pygame.display.flip()
    running = True
    card_surface = pygame.Surface((100,100))
    
    card = pygame.image.load("assets/sprites/cards/select.png").convert()
    cardrect = card.get_rect()
    # so, this is the card sprite...
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Now, blit the card things.
        for y in range(4):
            for x in range(4):
                card_surface.blit(card, (x*20 + 10,y*20 +10))
        
        screen.blit(card_surface)
        pygame.display.flip()