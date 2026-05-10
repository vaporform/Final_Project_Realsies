from .BaseScene import Scene
from .GameSession import GameSession

from Objects import Timer
from AssetHelper import *

import pygame

class Dialogue(Scene):
    
    def __init__(self, ts:Scene,
                dialogue_data=[{"text":"TEST","sprite":"placeholder.png","color":(255,255,255)}],
                font='test', size='16'):
        self.change_scenes = False
        self.key_allow_timer = Timer(2500)
        self.dialogue = dialogue_data
        self.fade_in_timer = Timer(1000)
        self.fade_out_timer = None
        self.target_scene = ts
        self.text_index = 0
        self.font = font
        self.size = size
        self.spacing = 0

    def update(self, dt):
        if self.fade_out_timer != None and self.fade_out_timer.is_finished():
            self.text_index += 1
            self.fade_out_timer = None
            self.fade_in_timer = Timer(1000)
            if self.change_scenes:
                return self.target_scene()
            
        return None

    def exit(self):
        AssetLib.play_sfx('')
        
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and not self.change_scenes:
                if event.key == pygame.K_SPACE:
                    if self.fade_in_timer.is_finished():
                        if self.text_index >= len(self.dialogue)-1:
                            self.change_scenes = True
                            
                        if self.fade_out_timer == None:
                            AssetLib.play_sfx('hitHurt.wav')
                            self.fade_out_timer = Timer(1000)
                
        return self

    def draw(self, screen: pygame.Surface):
        screen.fill((0,0,0))
        # text here        
        sw, sh = screen.get_size()
        dialogue = self.dialogue[self.text_index]
        
        texts = basic_text_wrap(dialogue["text"],50)
        line_surface = [text_to_surface(text,self.font,self.size,dialogue['color']) for text in texts]
        total_h = sum(s.get_height() for s in line_surface)
        y = (sh - total_h) // 2
        
        if dialogue['sprite'] != None:
            pic = AssetLib.get_sprite(dialogue['sprite'])
            self.spacing = pic.get_height()//2
            x = (sw - pic.get_width()) // 2
            screen.blit(pic,(x,5))
        else:
            self.spacing = 0
            
        for s in line_surface:
            x = (sw - s.get_width()) // 2  # center each line horizontally
            screen.blit(s, (x, y+self.spacing))
            y += s.get_height()
        
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

# I'm sorry bro :sob:
# sesh 1: intro
INTRO_DIALOGUE = [
        {"text":"Dude, it actually worked! No more tutors, no more failing... With this power, those top grades are as easy as pie!","sprite":"Summon_1","color":(255,255,255)},
        {"text":"Wait... why aren't you moving?! STOP! This isn't what I asked for!","sprite":"Summon_2","color":(255,255,255)},
        {"text":"Quiet, mortal. He was merely the price of admission. It was all in the fine print... which you clearly didn't bother to read.","sprite":None,"color":(255,0,0)},
        {"text":"GIVE HIM BACK! I challenge you to a game. If I win, my friend goes FREE!","sprite":None,"color":(255,255,255)},
        {"text":"A game? Very well... but we play by my rules. Survive my three servants first. Only then I'll reconsider your offering.","sprite":None,"color":(255,0,0)}
    ]

STAGE_1 = [
    {"text":"Hehehe... seems like my master got a new prey to toy with...! I shall think my luck will serve me well.","sprite":None,"color":(255,0,210)},
    {"text":"ACT I: The Lowly Imp","sprite":"portrait","color":(255,255,255)},
] 

STAGE_2 = [
    {"text":"ROARRR! YOU'VE GOT SOME GUTS, MORTAL! BUT CAN YOU SURVIVE FAFNIR'S SHINY-GLISTERING SCALES?!","sprite":None,"color":(200,0,210)},
    {"text":"ACT II: Scales and Stones ","sprite":"Fafnir","color":(255,255,255)},
]

STAGE_3 = [
    {"text":"Seems like we've underestimated you... No worries, I'll make sure you're dead before you reach HIM...","sprite":None,"color":(255,0,210)},
    {"text":"ACT III: Powerlong","sprite":"Abigor","color":(255,255,255)},
]

STAGE_4 = [
    {"text":"Bravo, summoner! You've come so far... I applaud you! But it seems like this... is your end.","sprite":None,"color":(255,0,0)},
    {"text":"ACT IV: Judgement Day","sprite":"Baphomet","color":(255,255,255)},
]

STAGE_5 = [
    {"text":"H-Hey! Are you okay man? I've finally defeated the boss!","sprite":"tunnel","color":(255,255,255)},
    {"text":"Argh! You little-! COME BACK HERE! I, THE DEMON KING IS NOT DONE WITH YOU MORTALS YET!","sprite":"Baphomet","color":(255,0,0)},
    {"text":"GAH! DUDE, RUN! LET'S GET OUTTA HERE!","sprite":"tunnel","color":(255,255,255)},
    {"text":"NEVER DO SKETCHY RITUALS AGAIN MAN!","sprite":"tunnel","color":(255,255,255)},
]