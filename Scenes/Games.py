from .GameSession import GameSession
from AssetHelper import AssetLib
from .Dialogue import *
from .EndScreen import End

from Players import *
from HelperCard import *
from BaseCard import BaseCard

class Tutorial(GameSession):
    def __init__(self):
        super().__init__(None)
        self.demon = TutorialDemon(BaseCard.deck_creator([16, 6, 2], [1,2,3], "demon"),[Pass_On])
        self.text_list = [
            "Use arrow keys to move between cards. Press Space to pick a card or confirm an action...",
            "Picking a card scores its value, tipping the scale. Tip it past the threshold to win.",
            "Any colored cards still give you points, but you won't get any helper cards.",
            "After you act, the demon takes their turn. Some demons might play something nasty!",
            "Complete a row, column or diagonal for bonus points. It refills cards from your deck.",
            "If you or demon drained all of their cards, it refills with bad (spooky) cards...",
            "Move to the right to browse Helpers. Each have their own unique skills. Go back to cancel.",
            "Note that you can't get helpers after you used one or more...",
            "Beat the tutorial."
        ]
        self.next_scene = Dialogue(Game1,STAGE_1,"Tiny5-Regular",10)
        #self.next_scene = Dialogue(Game4,STAGE_1,"Tiny5-Regular",10)
    
    def enter(self):
        super().enter()
        AssetLib.play_sfx('RainyFoothills.wav',True)

    def update(self, dt):
        if self.demon.round < len(self.text_list):
            self.demon.description = self.text_list[self.demon.round]
        return super().update(dt)

    def exit(self):
        super().exit()
        AssetLib.play_sfx('Typecast.wav',True)

class Game1(GameSession):
    def __init__(self):
        super().__init__('Imp')
        self.demon = Imp(BaseCard.deck_creator([16, 6, 2], [1,2,3], "demon"),[Pass_On])
        self.next_scene = Dialogue(Game2,STAGE_2,"Tiny5-Regular",10)
    
    def enter(self):
        super().enter()
        AssetLib.play_sfx('thewall.wav',True)

    def update(self, dt):
        result = super().update(dt)
        
        # If player lost, restart
        if self.scale.who_won() == "demon":
            self.next_scene = Game1()
        
        return result

    def exit(self):
        super().exit()
        AssetLib.play_sfx('Typecast.wav',True)
    
class Game2(GameSession):
    def __init__(self):
        super().__init__('Fafnir')
        self.demon = Fafnir(BaseCard.deck_creator([10, 6, 3, 2], [1,2,3,4], "demon"),[Lock])
        self.next_scene = Dialogue(Game3,STAGE_3,"Tiny5-Regular",10)
    
    def enter(self):
        super().enter()
        AssetLib.play_sfx('thewall.wav',True)

    def update(self, dt):
        result = super().update(dt)
        
        # If player lost, restart
        if self.scale.who_won() == "demon":
            self.next_scene = Game2()
        
        return result
    
    def exit(self):
        super().exit()
        AssetLib.play_sfx('Typecast.wav',True)
    
class Game3(GameSession):
    def __init__(self):
        super().__init__('Abigor')
        self.demon = Abigor(BaseCard.deck_creator([4,11,6,3], [-1,1,2,3], "demon"))
        self.next_scene = Dialogue(Game4,STAGE_4,"Tiny5-Regular",10)

    def enter(self):
        super().enter()
        AssetLib.play_sfx('thewall.wav',True)

    def update(self, dt):
        result = super().update(dt)
        
        # If player lost, restart
        if self.scale.who_won() == "demon":
            self.next_scene = Game3()
        
        return result
    
    def exit(self):
        super().exit()
        AssetLib.play_sfx('Typecast.wav',True)

class Game4(GameSession):
    def __init__(self):
        super().__init__('Baphomet')
        self.demon = Baphomet(BaseCard.deck_creator([18, 4, 3,2,1], [1,2,3,4,5], "demon"),[Lock,Bounty,Trap,Curse])
        self.next_scene = Dialogue(End,STAGE_5,"Tiny5-Regular",10)
        self.scale = Scale(30)

    def enter(self):
        super().enter()
        AssetLib.play_sfx('lichboss.wav',True)

    def update(self, dt):
        result = super().update(dt)
        
        # If player lost, restart
        if self.scale.who_won() == "demon":
            self.next_scene = Game4()
        
        return result
    
    def exit(self):
        super().exit()
        AssetLib.play_sfx('VictoryLap.wav', True)