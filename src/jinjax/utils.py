import logging
import uuid


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


def get_random_id(prefix="id") -> str:
    return f"{prefix}-{str(uuid.uuid4().hex)}"
