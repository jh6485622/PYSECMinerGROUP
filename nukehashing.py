from nukeerrors import *
import hashlib

class NukeHashObject:
    """"A class representing a NukeHash object with a hash and salt."""
    def __init__(self, hash: bytes, salt: bytes):
        self.hash = hash
        self.salt = salt
        self.digest()
    
    def __sizeof__(self):
        return len(self.hash.decode('utf-8') + self.salt.decode('utf-8'))
    
    def __or__(self, value):
        if isinstance(value, NukeHashObject): return True
        else: return False

    def __str__(self):
        return f'<NUKE: Hash#{self.hash.decode('utf-8')}, SALT#{self.salt.decode('utf-8')}>'
    
    def __eq__(self, value):
        if isinstance(value, NukeHashObject):
            if value.hash.decode('utf-8') == self.hash.decode('utf-8'):
                return True
            elif value.salt.decode('utf-8') == self.salt.decode('utf-8'):
                return True
            else:
                return False
        return False

    def digest(self) -> str:
        """Generates a Hash string from the hash and salt."""
        md5 = hashlib.md5(self.hash).hexdigest()
        md5a = hashlib.md5(self.salt).hexdigest()[len(hashlib.md5(self.salt).hexdigest()) - 5:len(hashlib.md5(self.salt).hexdigest()) - 1]
        sha256 = hashlib.sha256(self.hash).hexdigest()
        return sha256 + md5 + md5a

def zerobumpnuke(obj: int, salt: str) -> NukeHashObject:
    hash = ''
    glen = sum(ord(char1) for char1 in str(obj)) % 10
    for i in range(64 - (len(str(sum(ord(char) % 51 for char in str(obj)) % (10 ** 64 + 1))))):
        hash += str(glen)
        glen *= 3
        glen += 4
        glen %= 10
    hash += str(sum(ord(char) % 51 for char in str(obj)) % (10 ** 64 + 1))
    try:
        return NukeHashObject(hash.encode('utf-8'), salt.encode('utf-8'))
    except AttributeError:
        raise HashParseError('[HASH ERRNO 1] Parsing error when encoding')

def normnuke(obj: str, salt: str) -> NukeHashObject:
    try:
        return NukeHashObject(obj.encode('utf-8'), salt.encode('utf-8'))
    except AttributeError:
        raise HashParseError('[HASH ERRNO 1] Parsing error when encoding')