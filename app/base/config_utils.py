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
        "DB": int(path or 0),
        "PASSWORD": url.password or None,
        "HOST": url.hostname or "localhost",
        "PORT": int(url.port or 6379),
    }

    return config
