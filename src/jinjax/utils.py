"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
import logging
import re
import uuid


logger = logging.getLogger("jinjax")

DELIMITER = "."
SLASH = "/"

ARGS_PREFIX = "__prefix"


def get_url_prefix(prefix: str) -> str:
    url_prefix = prefix.strip().strip(f"{DELIMITER}{SLASH}").replace(DELIMITER, SLASH)
    if url_prefix:
        url_prefix = f"{url_prefix}{SLASH}"
    return url_prefix


def get_random_id(prefix="id") -> str:
    return f"{prefix}-{str(uuid.uuid4().hex)}"


def kebab_case(word: str) -> str:
    """Returns the lowercased kebab-cases form of `word`.
    Returns the right result even whith acronyms::

        >>> kebab_case("DeviceType")
        'device-type'
        >>> kebab_case("IOError")
        'io-error'
        >>> kebab_case("HTML")
        'html'
        >>> kebab_case("ui.AwesomeDialog")
        'ui.awesome-dialog'
        >>> kebab_case("MyFolder/DeviceType")
        'my-folder/device-type'
        >>> kebab_case("MyFolder.DeviceType")
        'my-folder.device-type'

    """
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", word)
    word = re.sub(r"([a-z\d])([A-Z])", r"\1-\2", word)
    word = word.replace("_", "-")
    return word.lower()
