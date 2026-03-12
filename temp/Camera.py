import random
import pygame
import math

from .GameMath import Position

class Camera:
    def __init__(self,pos:Position=Position(0,0),offset:Position=Position(0,0),size=(1920,1080)):
        self.position = pos
        self.offset = offset
        self.surface = pygame.Surface(size)
        # Juice!
        self.shake_duration = 0
        self.shake_intensity = 0
    
    def shake(self,intensity=10,duration=0.3):
        self.shake_duration = duration
        self.shake_intensity = intensity
        pass
    
    def add_to_render(self,arr):
        # FIRST IN FIRST OUT STYLE!
        shake_offset = Position(0,0)
        if self.shake_duration > 0:
            shake_offset = self.get_shake_offset()
            
        for stuff in arr:
            # ITEM, POS
            new_pos = stuff[1] - Position.round_pos(self.position) + self.offset + shake_offset
            self.surface.blit(stuff[0], 
                              (new_pos.x,new_pos.y)
                            )
        
    def update(self,dt):
        self.is_tracking = False
        if self.shake_duration > 0:
            self.shake_duration -= dt
        else:
            self.shake_intensity = 0
    
    def get_shake_offset(self):
        '''
        Get current shake offset
        
        :return: Position offset from shake
        '''
        if self.shake_intensity > 0:
            #print(self.shake_intensity)
            x_offset = random.randint(-self.shake_intensity, self.shake_intensity)
            y_offset = random.randint(-self.shake_intensity, self.shake_intensity)
            return Position(x_offset, y_offset)
        return Position(0, 0)