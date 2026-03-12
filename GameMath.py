import math
import pygame

class Position:
    def __init__(self, x, y,warn=False):
        if not (isinstance(x, int) and isinstance(y, int)) and warn:
            print("WARNING! It is recommended to use INT!")
        self.x = x
        self.y = y
        
    @staticmethod
    def round_pos(pos):
        return Position(round(pos.x),round(pos.y))
    
    @staticmethod
    def to_vector(self):
        '''
        Convert position to a Vector2D object
        '''
        return Position(self.x, self.y)

    def __add__(self, other):
        if isinstance(other, Position):
            return Position(self.x + other.x,
                           self.y + other.y)
        else:
            raise TypeError("Not a valid position operation!")
        
    def __sub__(self, other):
        if isinstance(other, Position):
            return Position(self.x - other.x,
                           self.y - other.y)
        else:
            raise TypeError("Not a valid position operation!")
    
    def __mul__(self, other):
        if isinstance(other, Position):
            raise TypeError("Not a valid position operation!")
        return Position(x=self.x * other, y=self.y * other)

    def __truediv__(self, other):
        if isinstance(other, Position):
            raise TypeError("Not a valid position operation!")
        return Position(x=self.x / other, y=self.y / other)

    def __floordiv__(self, other):
        if isinstance(other, Position):
            raise TypeError("Not a valid position operation!")
        return Position(x=self.x // other, y=self.y // other)

    def __mod__(self, other):
        if isinstance(other, Position):
            raise TypeError("Not a valid position operation!")
        return Position(x=self.x % other, y=self.y % other)
    
    def __ceil__(self):
        return Position(math.ceil(self.x),
                        math.ceil(self.y))
                        
    def __floor__(self):
        return Position(math.floor(self.x),
                        math.floor(self.y))
                        
    def __eq__(self,other):
        return (self.x == other.x and self.y == other.y and isinstance(other,Position))
    
    def __str__(self):
        return f"({self.x},{self.y})"

    def __neg__(self):
        return Position(-1 * (self.x),
                        -1 *(self.y))

class Vector2D:
    def __init__(self,x,y):
        if isinstance(x,(int,float)) and isinstance(y,(int,float)):
            self.x = x
            self.y = y
        else:
            raise TypeError("Vector must be made from INT or FLOAT!")
    
    def __add__(self,other):
        if isinstance(other,Vector2D):
            return Vector2D(self.x + other.x,
                            self.y + other.y)
        else:
            raise TypeError("Not a valid vector operation!")
        
    def __sub__(self,other):
        if isinstance(other,Vector2D):
            return Vector2D(self.x - other.x,
                            self.y - other.y)
        else:
            raise TypeError("Not a valid vector operation!")
    
    def __mul__(self,other):
        if isinstance(other,Vector2D):
            raise TypeError("Not a valid vector operation!")
        return Vector2D(x=self.x * other,y=self.y * other)

    def __truediv__(self,other):
        if isinstance(other,Vector2D):
            raise TypeError("Not a valid vector operation!")
        return Vector2D(x=self.x / other,y=self.y / other)

    def __floordiv__(self,other):
        if isinstance(other,Vector2D):
            raise TypeError("Not a valid vector operation!")
        return Vector2D(x=self.x // other,y=self.y // other)

    def __mod__(self,other):
        if isinstance(other,Vector2D):
            raise TypeError("Not a valid vector operation!")
        return Vector2D(x=self.x % other,y=self.y % other)
        
    def __ceil__(self):
        return Vector2D(math.ceil(self.x),
                        math.ceil(self.y))
                        
    def __floor__(self):
        return Vector2D(math.floor(self.x),
                        math.floor(self.y))
                        
    def __eq__(self,other):
        return (self.x == other.x and self.y == other.y and isinstance(other,Vector2D))
    
    def __str__(self):
        return f"({self.x},{self.y})"

    def __neg__(self):
        return Vector2D(-1 * (self.x),
                        -1 *(self.y))
    
    @staticmethod 
    def dot(A,B):
        '''
        Creates a dot product between two vectors. Returns a scalar value.
        Useful for telling aligned two vectors are (Same direction? Perpendicular? Opposite?)

        :param self: Vector A
        :param other: Vector B
        
        '''
        if isinstance(B,Vector2D) and isinstance(A,Vector2D):
            return (A.x * B.x) + (A.y * B.y)
        else:
            raise TypeError("Not a valid vector operation!")
    
    @staticmethod
    def cross(A,B):
        '''
        Creates a cross product between two vectors. Returns a scalar value.
        USeful for telling which side a vector is on (Left or Right?) or how much it is "rotating."

        :param self: Vector A
        :param other: Vector B
        '''
        if isinstance(B,Vector2D) and isinstance(A,Vector2D):
            return (A.x * B.y) - (A.y * B.x)
        else:
            raise TypeError("Not a valid vector operation!")
    
    @staticmethod
    def magnitude(A):
        '''
        Calculates magnitude for a vector. Returns scalar.
        '''
        if isinstance(A,Vector2D):
            return math.sqrt(A.x ** 2 + A.y ** 2)
        else:
            raise TypeError("Not a valid vector operation!")
    
    @staticmethod
    def hadamard(A,B):
        '''
        Calculates a Vector2D based on hadamard operation.
        '''
        return Vector2D((A.x * B.x),(A.y * B.y))

    @staticmethod
    def to_position(self):
        '''
        Convert Vector2D to a Position object
        '''
        return Position(self.x, self.y)
    
    @staticmethod
    def lerp(start,end,amount):
        '''
        AMOUNT SHOULD BE FROM 0 to 1
        '''
        return start + (end - start) * amount

    @staticmethod
    def approach(start,end,shift):
        '''
        Moves a scalar towards another scalar by a set length (shift).
        '''
        if start < end:
            return min(start + shift, end)
        else:
            return max(start - shift, end)
    
    @staticmethod
    def approach_vec(start, end, shift: float):
        '''
        Moves a vector towards another vector by a set length (shift).
        Useful for homing missiles or cameras, NOT platformer player physics.
        '''
        diff = Vector2D(end.x - start.x, end.y - start.y)
        length = Vector2D.magnitude(diff)
        
        if length <= shift:
            return end
            
        # Normalize and scale
        scale = shift / length
        return Vector2D(start.x + diff.x * scale, start.y + diff.y * scale)