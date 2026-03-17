import pygame
from .BaseScene import Scene
from .GameSession import GameSession

class TitleScreen(Scene):
    def __init__(self):
        self.a = pygame.image.load('assets/sprites/placeholder.jpg').convert()
        self.countdown = 0

    def update(self, dt):
        '''
        Called every frame. Returns new State or None.
        Move things, check timers.
        '''
        self.countdown += dt
        if self.countdown >= 10:
            print("Aye aye!")
            return GameSession()
        return None

    def draw(self, screen:pygame.Surface):
        screen.blit(self.a,(0,0))