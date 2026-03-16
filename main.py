import pygame
import random
from Objects import Grid, Card
gane_grid = Grid(4)

pygame.init()
render_resolution = (320,180)
#render_resolution = (640,480)
#screen_resolution = (640,480)
screen = pygame.display.set_mode(render_resolution,pygame.SCALED)
clock = pygame.time.Clock()
running = True

# LOAD CARDS
CARD_TEXTURES = {
    "backside":pygame.image.load("assets/sprites/cards/test.png").convert(),
    "select":pygame.image.load("assets/sprites/cards/select.png").convert_alpha(),
    "1":pygame.image.load("assets/sprites/cards/1.png").convert(),
    "2":pygame.image.load("assets/sprites/cards/2.png").convert(),
    "3":pygame.image.load("assets/sprites/cards/3.png").convert(),
}

card_surface = pygame.Surface((200,200))

font = pygame.font.Font(None, 16)        # load default font

cursor_x = 0
cursor_y = 0

game_state = { 
    "turn":"player",
    "scale":0,
    "player_score":0,
    "demon_score":0,
}
GRID_SIZE = 4
grid = Grid(GRID_SIZE, [ Card(random.randint(1,3),i%GRID_SIZE, i//GRID_SIZE) for i in range(GRID_SIZE**2)])

valid = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state['turn'] == 'player':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and cursor_y != 0:
                    cursor_y -= 1
                elif event.key == pygame.K_DOWN and cursor_y != GRID_SIZE-1:
                    cursor_y += 1
                
                if event.key == pygame.K_LEFT and cursor_x != 0:
                    cursor_x -= 1
                elif event.key == pygame.K_RIGHT and cursor_x != GRID_SIZE-1:
                    cursor_x += 1
                
                if event.key == pygame.K_SPACE:
                    # try to select the card
                    selected = grid.get_item(cursor_x,cursor_y)
                    if not selected.flipped:
                        game_state['scale'] += selected.value
                        selected.flip()

                        # now check for combos
                        row_coords, col_coords = grid.get_related_coords(cursor_x,cursor_y)
                        row_cards,_  = grid.get_tiles_from_coords(row_coords)
                        col_cards,_ = grid.get_tiles_from_coords(col_coords)

                        new_cards = []
                        valid_coords = []

                        if sum([int(b.flipped) for b in col_cards]) == GRID_SIZE: #OK!
                            for i in col_coords:
                                if i not in valid_coords:
                                    valid_coords.append(i)

                        if sum([int(b.flipped) for b in row_cards]) == GRID_SIZE: #OK!
                            for i in row_coords:
                                if i not in valid_coords:
                                    valid_coords.append(i)
                        
                        for i in valid_coords:
                            new_cards.append(Card(random.randint(1,3), i[0], i[1]))
                        
                        grid.set_tiles_from_coords(valid_coords,new_cards) 
                    #print(grid.grid[cursor_y][cursor_x])
                    pass

    screen.fill((255, 255, 255))          # clear screen each frame
    card_surface.fill((255,255,255))

    c_text = font.render(f"{cursor_x,cursor_y}\nScale: {game_state['scale'], game_state['turn']}", True, (0,0,0)) # create text surface
    # Now, blit the card things.
    
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            card = grid.grid[y][x]
            if card.flipped:
                card_surface.blit(CARD_TEXTURES[str(card.value)], (x*20 + 10,y*30))
            else:
                card_surface.blit(CARD_TEXTURES['backside'], (x*20 + 10,y*30))

    card_surface.blit(CARD_TEXTURES['select'],(cursor_x*20 + 10,cursor_y*30))

    screen.blit(card_surface)
    screen.blit(c_text,(100,10))    
    pygame.display.flip()            # push frame to screen
    clock.tick(60)                   # cap framerate

pygame.quit()