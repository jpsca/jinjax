import typing as t

from whitenoise import WhiteNoise  # type: ignore

if t.TYPE_CHECKING:
    from whitenoise.responders import Redirect, StaticFile  # type: ignore


class ComponentsMiddleware(WhiteNoise):
    """WSGI middleware for serving components assets"""
    allowed_ext: tuple[str, ...]

    def __init__(self, **kwargs) -> None:
        self.allowed_ext = kwargs.pop("allowed_ext", tuple())
        super().__init__(**kwargs)

    def find_file(self, url: str) -> "StaticFile|Redirect|None":
        if not self.allowed_ext or url.endswith(self.allowed_ext):
            return super().find_file(url)
        return None

    def add_file_to_dictionary(self, url: str, path: str, stat_cache: t.Any) -> None:
        if not self.allowed_ext or url.endswith(self.allowed_ext):
            super().add_file_to_dictionary(url, path, stat_cache)
