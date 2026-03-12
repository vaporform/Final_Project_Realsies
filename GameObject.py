import pygame
from .GameMath import Position

class Object:
    def __init__(self, position: Position, sprite:pygame.Surface):
        self.position = position
        self.surface = sprite
        pass