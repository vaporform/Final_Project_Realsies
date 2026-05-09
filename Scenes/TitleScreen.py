import pygame
from AssetHelper import *
from .BaseScene import Scene

from .GameSession import GameSession
from .Games import Tutorial
from .Dialogue import *
from Objects import Timer

class TitleScreen(Scene):
    def __init__(self):
        self.cursor = 0
        self.change_scenes = False
        self.fade_in_timer = Timer(1000)
        self.fade_out_timer = None

    def update(self, dt):        
        if self.change_scenes:
            if self.fade_out_timer != None and self.fade_out_timer.is_finished():
                return Dialogue(Tutorial,INTRO_DIALOGUE,"Tiny5-Regular",10)
        return None

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and not self.change_scenes:
                if event.key == pygame.K_UP and self.cursor != 0:
                    self.cursor -= 1
                elif event.key == pygame.K_DOWN and self.cursor != 2:
                    self.cursor += 1
                elif event.key == pygame.K_r and self.cursor == 1:
                    # reset data!
                    from TkStats import nuke_csv
                    nuke_csv("data/helper_cards.csv", ["card_name", "times_played"])
                    nuke_csv("data/board_cards.csv", ["turn", "player_cards", "demon_cards"])
                    nuke_csv("data/board_values.csv", ["board_value"])
                    nuke_csv("data/points_gained.csv", ["points_gained"])
                    nuke_csv("data/points_diff.csv", ["points_diff"])
                    print("############## CLEARED DATA! #############")
                elif event.key == pygame.K_SPACE and self.fade_in_timer.is_finished():
                    match self.cursor:
                        case 0:
                            self.change_scenes = True
                            self.fade_out_timer = Timer(1000)
                        case 1:
                            import subprocess, sys, os
                            subprocess.Popen([
                                sys.executable,
                                os.path.join(os.path.dirname(__file__), '..', 'TkStats.py'),
                                'data'
                            ])
                        case 2:
                            pygame.quit()
                
        return self

    def draw(self, screen: pygame.Surface):
        bob_offset = get_live_value(-3,3,3000,"yoyo")
        title = text_to_surface("Devils' Gambit", "Jacquard24-Regular", 36,(0,0,0),1)
        wing = AssetLib.get_sprite('wings')
        
        screen.blit(wing, wing.get_rect(center=(screen.get_width() // 2 - 40, 40)))
        screen.blit(pygame.transform.flip(wing, True, False), wing.get_rect(center=(screen.get_width() // 2 + 40, 40)))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 40 + bob_offset)))

        # Menu options
        play = text_to_surface("Start Gambit", "AlmendraSC-Regular", 18)
        stats = text_to_surface("Statistics", "AlmendraSC-Regular", 18)
        get_out = text_to_surface("Quit", "AlmendraSC-Regular", 18)
        
        for index, value in enumerate((play, stats, get_out)):
            text_rect = value.get_rect(center=(screen.get_width() // 2, 100 + (index * 25)))
            screen.blit(value, text_rect)
            
            if index == self.cursor:
                size = get_live_value(15,20,1000,"breathe")
                
                img_left = pygame.transform.scale(AssetLib.get_sprite('human_token'), (size, size))
                img_right = pygame.transform.scale(AssetLib.get_sprite('demon_token'), (size, size))
                
                rect_left = img_left.get_rect(center=(text_rect.left - 15, text_rect.centery))
                rect_right = img_right.get_rect(center=(text_rect.right + 15, text_rect.centery))

                screen.blit(img_left, rect_left)
                screen.blit(img_right, rect_right)

        dithers = [2,5,1,6,3,4,7]
        if self.change_scenes  and self.fade_out_timer.is_finished():
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