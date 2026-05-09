import pygame
from AssetHelper import *
# TEXTURE list

class BaseCard:
    base_sprite_front = None
    base_sprite_back = None

    @classmethod
    def load_graphics(cls):
        cls.base_sprite_front = AssetLib.get_sprite('cards/card_blank')
        cls.base_sprite_back = AssetLib.get_sprite('cards/back')

    def __init__(self, value=1, x=0,y=0,owner="None"):
        self.flipped = False
        self.effects = [] # stuff to store effects :P
        self.value = value
        self.lock = False # *stops u from picking me >:D*
        # Additional info
        self.x = x
        self.y = y

        self.owner = owner
        # drawing stuff...

    def flip(self):
        if not self.lock:
            self.flipped = not self.flipped
    
    @staticmethod
    def deck_creator(rates, values, owner):
        deck = []
        for index, r in enumerate(rates):
            deck.extend([values[index]] * r)
        
        return [BaseCard(value=i,owner=owner) for i in deck]

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"{self.value}"