import random
import string
import uuid

class KeyGenerator():
    
    def __init__(self, size=10):
        self.size = size
        
    def random_number(self):
        return random.choice([x for x in range(1,self.size+1)])
        
    def generate_unique_key(self, startswith=None):
        
        digits: str = string.digits
        alphabet: str = string.ascii_letters
        combined: str = digits + alphabet
        
        key = startswith if startswith is not None else ''
        for i in range(self.size):
            if i % self.random_number() == 0 or i % self.random_number() == 0:
                picked = random.choice(digits)
                key += picked
            else:
                picked = random.choice(alphabet)
                key += picked
        
        return key