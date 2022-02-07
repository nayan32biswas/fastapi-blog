from typing import List

import urllib.parse as urlparse


def comma_separated_str_to_list(comma_separated_str: str) -> List[str]:
    return comma_separated_str.split(",")


def parse_redis_url(url) -> dict:
    """Parses a database URL."""

    config = {}

    url = urlparse.urlparse(url)

    # Remove query strings.
    path = url.path[1:]
    path = path.split("?", 2)[0]

    # Update with environment configuration.
    config = {
        "db": int(path or 0),
        "password": url.password or None,
        "host": url.hostname or "localhost",
        "port": int(url.port or 6379),
    }

    return config
