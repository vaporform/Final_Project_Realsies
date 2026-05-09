import pygame
import math

class AssetLib:
    textures = {}
    fonts = {}
    sounds = {}
    cache = {}
    
    @classmethod
    def get_sprite(cls, key):
        if key not in cls.textures.keys():
            #print(f"TEXTURE NOT FOUND ({key})! ATTEMPTING TO LOAD FROM DISK!")
            try:
                full_path = f"assets/sprites/{key}.png"
                surface = pygame.image.load(full_path).convert_alpha()
                cls.textures[key] = surface
            except:
                print("TEXTURE DNE!",key)
                if 'placeholder' not in cls.textures.keys():
                    AssetLib.get_sprite('placeholder')
                cls.textures[key] = cls.textures['placeholder']
        return cls.textures[key]

    @classmethod
    def add_to_cache(cls, key, surf):
        cls.cache[key] = surf
    
    @classmethod
    def get_cache(cls,key):
        if key in cls.cache.keys():
            return cls.cache[key]
        return None
    
    @classmethod
    def clear_cache(cls):
        cls.cache = {}
    
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
    
    @classmethod
    def get_sound(cls, key):
        if key not in cls.sounds.keys():
            print(f"SOUND NOT FOUND ({key})! ATTEMPTING TO LOAD FROM DISK!")
            try:
                full_path = f"assets/sounds/{key}"
                cls.sounds[key] = pygame.mixer.Sound(full_path)
            except:
                print("SOUND DNE!",key)
                return None
        return cls.sounds[key]
    
    @classmethod
    def play_sfx(cls, key, loop=False):
        # Like in the good ol' days, you can only do so much with the sound system... 
        if key == None or key == '': # assume we clear it up chat
            for i in cls.sounds:
                asset = AssetLib.get_sound(i)
                if asset:
                    asset.stop()
                else:
                    break # there's nothing!
            return
            
        asset = AssetLib.get_sound(key)
        if asset != None:
            if not loop:
                asset.play()
            else:
                asset.play(-1)

    @classmethod
    def preload_sprites(cls,names):
        for name in names:
            cls.get_sprite(name)
        
    @staticmethod
    def load_graphics(image_path:dict):
        new = {}
        for i,v in image_path.items():
            new[i] = pygame.image.load(v).convert_alpha()
        return new

# ==================
def palette_swap(surf, old_c, new_c):        
    img_copy = pygame.Surface(surf.get_size(),pygame.SRCALPHA)
    img_copy.fill(new_c)

    surf_with_key = surf.copy()
    surf_with_key.set_colorkey(old_c)

    img_copy.blit(surf_with_key, (0, 0))
    return img_copy

def text_to_surface(text, font_name='test', size=16, color=(0,0,0), outline_width=0,outline_color=(255,255,255)):
    # sneaky ahh
    cache_key = f'{text}{font_name}{size}{color}{outline_width}{outline_color}'
    if cache_key in AssetLib.cache.keys():
        return AssetLib.get_cache(cache_key)
    
    font = AssetLib.get_font(font_name,size)

    main_surface = font.render(str(text),False,color)
    if outline_width <= 0:
        AssetLib.add_to_cache(cache_key,main_surface)
        return main_surface
    
    outline_surface = font.render(str(text),False,outline_color)
    width, height = outline_surface.get_size()

    canvas = pygame.Surface((width + 2 * outline_width, height + 2 * outline_width), pygame.SRCALPHA)
    
    for x,y in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        canvas.blit(outline_surface, (outline_width + x * outline_width, outline_width + y * outline_width))
    
    canvas.blit(main_surface, (outline_width, outline_width))
    AssetLib.add_to_cache(cache_key,canvas)
    return canvas

def lerp(start,end,amount):
    '''
    AMOUNT SHOULD BE FROM 0 to 1
    '''
    return start + (end - start) * amount

def get_live_value(start, end, duration_ms, mode="linear",current_time=None):
    '''
    Function to get value based on.. well, time!
    used for animating stuff :P
    options:linear, yoyo, ease_out, ease_in, bounce, step, smooth, elastic, back_in, breathe, shake, swing
    '''
    if current_time == None:
        current_time = pygame.time.get_ticks()
    t = (current_time % duration_ms) / duration_ms
    
    match mode:
        case "linear":
            progress = t
        case "yoyo":
            # Smooth sine wave 0 -> 1 -> 0
            progress = (math.sin(t * math.pi * 2 - math.pi / 2) + 1) / 2
        case "ease_out":
            # Fast start, slow end
            progress = 1 - (1 - t) * (1 - t)
        case "ease_in":
            # Slow start, fast end
            progress = t * t
        case "bounce":
            # Good for a repetitive "hop"
            progress = abs(math.sin(t * math.pi))
        case "step":
            # Moves in 5 distinct "ticks"
            progress = math.floor(t * 5) / 5
        case "smooth":
            # 3t^2 - 2t^3
            progress = t * t * (3 - 2 * t)
        case "elastic":
            p = 0.3 # period
            progress = math.pow(2, -10 * t) * math.sin((t - p / 4) * (2 * math.pi) / p) + 1
        case "back_in":
            s = 1.70158 # "overshoot" amount
            progress = t * t * ((s + 1) * t - s)
        case "breathe":
            # Smooth oscillation using cosine
            progress = (1 - math.cos(t * math.pi * 2)) / 2
        case "shake":
            # Rapidly oscillates 4 times per duration
            progress = math.sin(t * math.pi * 8)
        case "swing":
            # Ping-pong time logic
            tp = 1.0 - abs(t * 2.0 - 1.0)
            # Apply a smooth-step to the ping-ponged value
            progress = tp * tp * (3 - 2 * tp)
        case _:
            progress = t
        
    return start + (end - start) * progress

def basic_text_wrap(text, char_lim):
    # very basic yes
    words = text.split()
    lines = []
    line = ''
    
    for word in words:
        if len(line) + len(word) + 1 <= char_lim:
            line += word + ' '
        else:
            # over ze limit!
            lines.append(line.strip())
            line = word + ' '
    
    # leftover
    lines.append(line.strip())
    return lines