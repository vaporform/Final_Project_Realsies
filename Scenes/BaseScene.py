import pygame

# State Machine strikes back!
class Scene:
    '''
    A class for handling scenes for the game. Ex. Title, Gameplay, Ending, etc.    
    '''
    def enter(self):
        '''
        Called once when entering this state.
        Reset music, set player positions, etc.
        For loading assets or heavy stuff, it is advisable to load via __init__ instead.
        '''
        pass

    def exit(self):
        '''
        Called once when leaving this state.
        Clean up the scene, preparing for a new one.
        '''
        pass
    
    def handle_input(self, events):
        ''' Process keys. Returns 'self' or a NEW Scene.'''
        return self

    def update(self, dt):
        '''
        Called every frame. Returns new State or None.
        Move things, check timers.
        '''
        return None

    def draw(self, screen:pygame.Surface):
        '''Called for rendering the scene.'''
        pass