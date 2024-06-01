import logging


logger = logging.getLogger("jinjax")

DELIMITER = "."
SLASH = "/"


def get_url_prefix(prefix: str) -> str:
    url_prefix = (
        prefix.strip().strip(f"{DELIMITER}{SLASH}").replace(DELIMITER, SLASH)
    )
    if url_prefix:
        url_prefix = f"{url_prefix}{SLASH}"
    return url_prefix
