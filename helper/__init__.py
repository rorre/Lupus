import random
import string

def generate_random_name(n):
    return "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(n)
    )