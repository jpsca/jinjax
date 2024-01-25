import re
import typing as t
from pathlib import Path

from whitenoise import WhiteNoise  # type: ignore

if t.TYPE_CHECKING:
    from whitenoise.responders import Redirect, StaticFile  # type: ignore


RX_FINGERPRINT = re.compile("(.*)-([abcdef0-9]{64})")


class ComponentsMiddleware(WhiteNoise):
    """WSGI middleware for serving components assets"""
    allowed_ext: tuple[str, ...]

    def __init__(self, **kwargs) -> None:
        self.allowed_ext = kwargs.pop("allowed_ext", tuple())
        super().__init__(**kwargs)

    def find_file(self, url: str) -> "StaticFile|Redirect|None":

        if self.allowed_ext and not url.endswith(self.allowed_ext):
            return None

        # Ignore the fingerprint in the filename
        # since is only for managing the cache in the client
        relpath = Path(url)
        ext = "".join(relpath.suffixes)
        stem = relpath.name.removesuffix(ext)
        fingerprinted = RX_FINGERPRINT.match(stem)
        if fingerprinted:
            stem = fingerprinted.group(1)
            relpath = relpath.with_name(f"{stem}{ext}")

        return super().find_file(str(relpath))

    def add_file_to_dictionary(self, url: str, path: str, stat_cache: t.Any) -> None:
        if not self.allowed_ext or url.endswith(self.allowed_ext):
            super().add_file_to_dictionary(url, path, stat_cache)
