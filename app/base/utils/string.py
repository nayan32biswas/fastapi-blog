import re
from random import choice
from string import ascii_lowercase, digits

pattern = re.compile(r"(?<!^)(?=[A-Z])")


def rand_str(N=12):
    return "".join(choice(ascii_lowercase + digits) for _ in range(N))


def camel_to_snake(string: str) -> str:
    return pattern.sub("_", string).lower()
