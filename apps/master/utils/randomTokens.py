import time
import random
import string
import secrets

def generate_id():
    def to_base36(num):
        chars = string.digits + string.ascii_lowercase
        result = ""
        while num > 0:
            num, i = divmod(num, 36)
            result = chars[i] + result
        return result or "0"


    # Equivalent to Date.now().toString(36)
    timestamp_part = to_base36(int(time.time() * 1000))
    
    # Equivalent to Math.random().toString(36).slice(2, 6)
    random_part = to_base36(int(random.random() * (36**6))).zfill(6)[2:6]
    
    
    return timestamp_part + random_part + hex(int(time.time() * 1000))[2:] + secrets.token_hex(2)