import pygame

from Scenes.TitleScreen import TitleScreen

class GameApp:
    def __init__(self):
        '''
        Initialize the game.
        '''
        pygame.init() # Inititalize the game!
        self.render_resolution = (320,180)
         
        # The actual screen that the user will see.
        self.screen = pygame.display.set_mode(self.render_resolution, pygame.SCALED, vsync=1)

        pygame.display.set_caption("Game")  
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_scene = None
        self.dt = 0.1
    
    def run(self):
        while self.running:
            all_events = pygame.event.get()
            # enable the 'x' button lol
            for event in all_events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            next_scene_input = self.current_scene.handle_input(all_events)
            next_scene_update = self.current_scene.update(self.dt) 

            # Determine which scene to use next
            # Priority: Update logic > Input logic > Current Scene
            if next_scene_update != None:
                next_scene = next_scene_update
            elif next_scene_input != self.current_scene and next_scene_input != None:
                next_scene = next_scene_input
            else:
                next_scene = self.current_scene
            
            # Switch!
            if next_scene != self.current_scene:
                self.current_scene.exit() # Clean up old scene
                self.current_scene = next_scene
                self.current_scene.enter() # Setup new scene
            
            self.screen.fill("pink")
            self.current_scene.draw(self.screen)
            pygame.display.flip()

            self.dt = self.clock.tick(24)/1000
        pygame.quit()

if  __name__ == '__main__':

    instance = GameApp()
    instance.current_scene = TitleScreen()
    #instance.current_scene = D1()
    instance.run()


