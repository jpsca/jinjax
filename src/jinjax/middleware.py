import typing as t

from whitenoise import WhiteNoise  # type: ignore

if t.TYPE_CHECKING:
    from whitenoise.responders import Redirect, StaticFile  # type: ignore


class ComponentsMiddleware(WhiteNoise):
    """WSGI middleware for serving components assets"""
    allowed_ext = None

    def __init__(self) -> None:
        super().__init__(application=None)

    def configure(
        self,
        *,
        application: t.Optional[t.Callable] = None,
        allowed_ext: t.Optional[tuple[str, ...]] = None,
        **kw
    ):
        if application:  # pragma: no cover
            self.application = application
        if allowed_ext:  # pragma: no cover
            self.allowed_ext = tuple(allowed_ext)
        for attr in self.config_attrs:
            if attr in kw:
                setattr(self, attr, kw[attr])

    def find_file(self, url: str) -> "t.Union[StaticFile, Redirect, None]":
        if not self.allowed_ext or url.endswith(self.allowed_ext):
            return super().find_file(url)
        return None

    def add_file_to_dictionary(self, url: str, path: str, stat_cache: t.Any) -> None:
        if not self.allowed_ext or url.endswith(self.allowed_ext):
            super().add_file_to_dictionary(url, path, stat_cache)
