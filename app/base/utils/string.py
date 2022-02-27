from random import choice
from string import ascii_lowercase, digits


def rand_str(N=12):
    return "".join(choice(ascii_lowercase + digits) for _ in range(N))
