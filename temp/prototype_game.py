class Card:
    def __init__(self):
        self.flipped = False
        self.player_marked = False
        self.monster_marked = False
        self.value = 1

    def is_p_marked(self):
        return self.player_marked
    
    def is_m_marked(self):
        return self.monster_marked
    
    def is_both_marked(self):
        return (self.player_marked and self.monster_marked)
    
    def flip(self):
        self.flip = (not self.flip)

class Grid:
    def __init__(self, size):
        self.size = size
        self.grid = self.create_grid(self.size)
    
    def create_grid(self,size):       
        temp_grid = []
        # create cards.
        for i in range(size):
            temp_grid.append(
                [Card() for _ in range(size)]
            )
        return temp_grid
    
    def peek_valid_monster(self):
        # get all valid tiles for monster.
        # return card instances. 
        valid = []
        for row in self.grid:
            for card in row:
                if not card.is_p_marked and not card.flipped:
                    valid.append(card) 
        return valid

    def show_grid(self):
        for i in self.grid:
            for j in i:
                print(f"[{j.flipped}]", end=" ")
            print()

class Player:
    def __init__(self):
        self.sanity = 5
        self.traps = 1
        self.body = ['leg', 'hand', 'arm', 'eye']
        self.upgrades = []
    
    def sacrifice(self,target):
        if target in self.body:
            self.body.remove(target)
            return True
        else: 
            print("invalid")
        return False

class AI:
    def __init__(self,name, df):
        self.name = name
        # How much to defeat?
        self.goal = 10
        self.decision_function = df
    
    def decide(self, game_grid:Grid):
        # decision maker stuff. Override this via decision_function.
        return self.decision_function(game_grid)


# Let's create a demon!
def imp(game_grid:Grid):
    for row in game_grid:
        for card in row:
        # linear drop.
            if not card.flipped and not card.monster_marked:
                card.flip()
                if card.is_p_marked:
                    #...
                    pass

    pass

    
player = Player()
grid = Grid(3)
# Game Loop 
while True:
    grid.show_grid()
    decision = input(f"Player's turn to place traps. AMOUNT {player.traps}: ").split()
    x,y = int(decision[0]), int(decision[1])
    grid.grid[y][x].player_marked = True
    # demon does something here ig


