import pygame
from GraphicHelper import *
from .BaseScene import Scene
from .GameSession import GameSession

class TitleScreen(Scene):
    def __init__(self):
        super().__init__()
        self.cursor = 0
        self.change_scenes = False

    def update(self, dt):        
        if self.change_scenes:
            if not self.anim_manager.animations:
                return GameSession()

        return super().update(dt)

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and not self.change_scenes:
                if event.key == pygame.K_UP and self.cursor != 0:
                    self.cursor -= 1
                elif event.key == pygame.K_DOWN and self.cursor != 2:
                    self.cursor += 1
                elif event.key == pygame.K_SPACE:
                    match self.cursor:
                        case 0:
                            self.change_scenes = True
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
                size = 5
                
                img_left = pygame.transform.scale(AssetLib.get_sprite('human_token'), (size, size))
                img_right = pygame.transform.scale(AssetLib.get_sprite('demon_token'), (size, size))
                
                rect_left = img_left.get_rect(center=(text_rect.left - 20, text_rect.centery))
                rect_right = img_right.get_rect(center=(text_rect.right + 20, text_rect.centery))

                screen.blit(img_left, rect_left)
                screen.blit(img_right, rect_right)
    
        if self.change_scenes and not self.anim_manager.animations:
            screen.fill((0,0,0))
        
        super().draw(screen)