import pygame
import GraphicHelper
from .BaseScene import Scene
from .GameSession import GameSession

class TitleScreen(Scene):
    def __init__(self):
        self.a = pygame.image.load('assets/sprites/placeholder.jpg').convert()
        self.logo = pygame.image.load('assets/sprites/logo.png').convert_alpha()
        self.countdown = 0
        self.tick = 0
        
    def update(self, dt):
        '''
        Called every frame. Returns new State or None.
        Move things, check timers.
        '''
        self.countdown += dt
        if self.countdown <= 3:
            self.tick += 1
        
        if self.countdown >= 1:
            return GameSession()
        return None

    def draw(self, screen:pygame.Surface):
        text = GraphicHelper.text_to_surface("Hello","Arial",16)
        screen.blit(text,(0,0))
        screen.blit(self.logo,(0,self.tick))