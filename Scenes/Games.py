from .GameSession import GameSession
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
            "After you act, the demon takes their turn. Watch the scale.",
            "Try to complete a row, column or diagonal for bonus points. It refills with cards from your deck.",
            "Move to the right to browse Helpers. Each have their own unique skills. Go back to cancel.",
            "Beat the tutorial."
        ]
        self.next_scene = Dialogue(Game1,STAGE_1,"Tiny5-Regular",10)
        
    def update(self, dt):
        if self.demon.round < len(self.text_list):
            self.demon.description = self.text_list[self.demon.round]
        return super().update(dt)

class Game1(GameSession):
    def __init__(self):
        super().__init__('Imp')
        self.demon = Imp(BaseCard.deck_creator([16, 6, 2], [1,2,3], "demon"),[Lock])
        self.next_scene = Dialogue(Game2,STAGE_2,"Tiny5-Regular",10)
    
    def update(self, dt):
        result = super().update(dt)
        
        # If player lost, restart
        if self.scale.who_won() == "demon":
            self.next_scene = Game1()
        
        return result
    
class Game2(GameSession):
    def __init__(self):
        super().__init__('Fafnir')
        self.demon = Fafnir(BaseCard.deck_creator([10, 6, 3, 2], [1,2,3,4], "demon"),[Pass_On])
        self.next_scene = Dialogue(Game3,STAGE_3,"Tiny5-Regular",10)

    def update(self, dt):
        result = super().update(dt)
        
        # If player lost, restart
        if self.scale.who_won() == "demon":
            self.next_scene = Game2()
        
        return result
    
class Game3(GameSession):
    def __init__(self):
        super().__init__('Abigor')
        self.demon = Abigor(BaseCard.deck_creator([4,11,6,3], [-1,1,2,3], "demon"),[Pass_On])
        self.next_scene = Dialogue(Game4,STAGE_4,"Tiny5-Regular",10)

    def update(self, dt):
        result = super().update(dt)
        
        # If player lost, restart
        if self.scale.who_won() == "demon":
            self.next_scene = Game3()
        
        return result
    
class Game4(GameSession):
    def __init__(self):
        super().__init__('Baphomet')
        self.demon = Baphomet(BaseCard.deck_creator([18, 4, 3,2,1], [1,2,3,4,5], "demon"),[Pass_On])
        self.next_scene = Dialogue(End,STAGE_5,"Tiny5-Regular",10)

    def update(self, dt):
        result = super().update(dt)
        
        # If player lost, restart
        if self.scale.who_won() == "demon":
            self.next_scene = Game4()
        
        return result