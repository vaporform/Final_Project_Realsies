import pygame

class Game:
    def __init__(self):
        '''
        Initialize the game.
        
        :param self: Description
        '''
        pygame.init() # Inititalize the game!
        self.render_resolution = (320,180)
        self.screen_resolution = (640,480)

        # The actual screen that the user will see.
        self.real_screen = pygame.display.set_mode(self.screen_resolution,
                                            pygame.SCALED,
                                            vsync=1)

        pygame.display.set_caption("Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0.1
    
    def update_system_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
    def run(self):
        '''
        Run the game
        
        :param self: Description
        '''
        card = pygame.image.load("assets/sprites/Untitled.png").convert()
        cardrect = card.get_rect()
        while self.running:
            self.update_system_events()

            


            self.screen.fill((255,255,255))
            pygame.display.flip()
            pass
            
        pygame.quit()

# Start the game!
game = Game()
game.run()