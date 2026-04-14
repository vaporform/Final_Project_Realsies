import pygame

class AssetLib:
    textures = {
    }
    
    fonts = {
    }

    @classmethod
    def get_sprite(cls, key):
        if key not in cls.textures.keys():
            print(f"TEXTURE NOT FOUND ({key})! ATTEMPTING TO LOAD FROM DISK!")
            try:
                full_path = f"assets/sprites/{key}.png"
                surface = pygame.image.load(full_path)
                # Only convert_alpha() if display is initialized
                if pygame.display.get_surface() is not None:
                    surface = surface.convert_alpha()
                cls.textures[key] = surface
            except:
                print("TEXTURE DNE!",key)
                if 'placeholder' not in cls.textures.keys():
                    AssetLib.get_sprite('placeholder')
                cls.textures[key] = cls.textures['placeholder']
        return cls.textures[key]
    
    @classmethod
    def get_font(cls,key,size):
        if f"{key}{size}" not in cls.fonts.keys():
            print(f"FONT NOT FOUND ({key}{size})! ATTEMPTING TO LOAD FROM DISK!")
            try:
                #assets/fonts/wizzta.regular.ttf
                full_path = f"assets/fonts/{key}.ttf"
                cls.fonts[f"{key}{size}"] = pygame.font.Font(full_path, size)
            except:
                print("FONT DNE!",key)
                if 'test16' not in cls.fonts.keys():
                    cls.fonts['test16'] = pygame.font.Font(None, 16)
                cls.fonts[f"{key}{size}"] = cls.fonts['test16']
        return cls.fonts[f"{key}{size}"]
    
    @staticmethod
    def load_graphics(image_path:dict):
        new = {}
        for i,v in image_path.items():
            new[i] = pygame.image.load(v).convert_alpha()
        return new

def palette_swap(surf, old_c, new_c):
    img_copy = pygame.Surface(surf.get_size(),pygame.SRCALPHA)
    img_copy.fill(new_c)

    surf_with_key = surf.copy()
    surf_with_key.set_colorkey(old_c)

    img_copy.blit(surf_with_key, (0, 0))
    return img_copy

def text_to_surface(text, font_name='test', size=16, color=(0,0,0)):
    font = AssetLib.get_font(font_name,size)
    return font.render(str(text),False,color) # returns text surface

def lerp(start,end,amount):
    '''
    AMOUNT SHOULD BE FROM 0 to 1
    '''
    return start + (end - start) * amount

class AniManager:
    def __init__(self):
        self.animations = []
    
    def add(self, duration, on_update, on_complete=None):
        '''
        Add an animation.
        NOTE: on_update MUST have a parameter to pass one var!
        '''
        self.animations.append(
            {
                'progress':0.0,
                'duration':duration,
                'on_update':on_update,
                'on_complete':on_complete,
                'active': True
            }
        )
    
    def update(self,dt):
        for animation in self.animations.copy():
            if animation['active']:
                animation['progress'] += dt/animation['duration']

                if animation['progress'] > 1:
                    anim['progress'] = 1
                
                anim['on_update'](anim['progress'])

                if animation['progress'] >= 1:
                    anim['active'] = False
                    if anim['on_complete'] != None:
                        anim['on_complete']()
            
        self.animations = [i for i in self.animations if i['active']]
                