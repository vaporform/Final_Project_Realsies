from .BaseScene import Scene

from Objects import Timer
from AssetHelper import *

import pygame

class End(Scene):
    def __init__(self):
        self.cursor = 0
        self.change_scenes = False
        self.fade_in_timer = Timer(1000)
        self.key_allow_timer = Timer(5000)
        self.fade_out_timer = None

    def update(self, dt):
        if self.fade_out_timer != None and self.fade_out_timer.is_finished():
            if self.change_scenes:
                from Scenes.TitleScreen import TitleScreen
                return TitleScreen()
            
        return None

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and not self.change_scenes:
                if event.key == pygame.K_SPACE:
                    if self.fade_in_timer.is_finished():
                        self.change_scenes = True
                        if self.fade_out_timer == None:
                            self.fade_out_timer = Timer(1000)
                
        return self

    def draw(self, screen: pygame.Surface):
        screen.fill((0,0,0))
        # text here        
        sw, sh = screen.get_size()
        text_surf = text_to_surface("THE END","Jacquard24-Regular",32,(255,255,255))
        
        rect = text_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text_surf, rect)
        
        if self.key_allow_timer.is_finished():
            t = text_to_surface('[SPACE to Continue]',"Tiny5-Regular",8,(255,255,255))
            x = (sw - t.get_width()) // 2
            screen.blit(t,(x,sh-20))
            
        dithers = [2,5,1,6,3,4,7]
        
        if self.change_scenes and self.fade_out_timer.is_finished():
            screen.fill((0,0,0))
        else:
            if self.fade_out_timer != None:
                p = self.fade_out_timer.get_p()
                index = min(int(p * len(dithers)), len(dithers) - 1)
                cf = dithers[index]
                screen.blit(AssetLib.get_sprite(f"dither_screen{cf}"),(0,0))

        if not self.fade_in_timer.is_finished():
            p = self.fade_in_timer.get_p()
            index = min(int(p * len(dithers)), len(dithers) - 1)
            dithers.reverse()
            cf = dithers[index]
            screen.blit(AssetLib.get_sprite(f"dither_screen{cf}"),(0,0))