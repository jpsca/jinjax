import os
import typing as t
from hashlib import sha256
from pathlib import Path

import jinja2
from markupsafe import Markup

from .component import Component
from .exceptions import ComponentNotFound, InvalidArgument
from .html_attrs import HTMLAttrs
from .jinjax import JinjaX
from .middleware import ComponentsMiddleware
from .utils import DELIMITER, SLASH, get_url_prefix, logger


TFileExt = t.Union[tuple[str, ...], str]

DEFAULT_URL_ROOT = "/static/components/"
ALLOWED_EXTENSIONS = (".css", ".js", ".mjs")
DEFAULT_PREFIX = ""
DEFAULT_EXTENSION = ".jinja"
PROP_ATTRS = "attrs"
PROP_CONTENT = "content"


class Catalog:
    """
    Attributes:

        globals:

        filters:

        tests:

        extensions:

        jinja_env:

        root_url:

        file_ext:

        fingerprint [False]:
            If True, adds, insert a hash of the updated time to the URL of the
            asset files (after the name of,but before the extension).
            This strategy encourages long-term caching while ensuring that new copies
            are only requested when the content changes, as any modification alter
            the fingerprint and thus the filename.

            *WARNING*: Only works if the server know how to filter the fingerprint
            to get the real name of the file.

    """

    __slots__ = (
        "prefixes",
        "root_url",
        "file_ext",
        "jinja_env",
        "fingerprint",
        "collected_css",
        "collected_js",
        "auto_reload",
        "tmpl_globals",
        "use_cache",
        "_cache",
    )

    def __init__(
        self,
        *,
        globals: "dict[str, t.Any] | None" = None,
        filters: "dict[str, t.Any] | None" = None,
        tests: "dict[str, t.Any] | None" = None,
        extensions: "list | None" = None,
        jinja_env: "jinja2.Environment | None" = None,
        root_url: str = DEFAULT_URL_ROOT,
        file_ext: TFileExt = DEFAULT_EXTENSION,
        use_cache: bool = True,
        auto_reload: bool = True,
        fingerprint: bool = False,
    ) -> None:
        self.prefixes: dict[str, jinja2.FileSystemLoader] = {}
        self.collected_css: list[str] = []
        self.collected_js: list[str] = []
        self.file_ext = file_ext
        self.use_cache = use_cache
        self.auto_reload = auto_reload
        self.fingerprint = fingerprint

        root_url = root_url.strip().rstrip(SLASH)
        self.root_url = f"{root_url}{SLASH}"

        env = jinja2.Environment(undefined=jinja2.StrictUndefined)
        extensions = [*(extensions or []), "jinja2.ext.do", JinjaX]
        globals = globals or {}
        filters = filters or {}
        tests = tests or {}

        if jinja_env:
            env.extensions.update(jinja_env.extensions)
            env.autoescape = jinja_env.autoescape
            globals.update(jinja_env.globals)
            filters.update(jinja_env.filters)
            tests.update(jinja_env.tests)
            jinja_env.globals["catalog"] = self
            jinja_env.filters["catalog"] = self

        globals["catalog"] = self
        filters["catalog"] = self

        for ext in extensions:
            env.add_extension(ext)
        env.globals.update(globals)
        env.filters.update(filters)
        env.tests.update(tests)
        env.extend(catalog=self)

        self.jinja_env = env

        self.tmpl_globals: "t.MutableMapping[str, t.Any] | None" = None
        self._cache: dict[str, dict] = {}

    @property
    def paths(self) -> list[Path]:
        _paths = []
        for loader in self.prefixes.values():
            _paths.extend(loader.searchpath)
        return _paths

    def add_folder(
        self,
        root_path: "str | Path",
        *,
        prefix: str = DEFAULT_PREFIX,
    ) -> None:
        prefix = prefix.strip().strip(f"{DELIMITER}{SLASH}").replace(SLASH, DELIMITER)

        root_path = str(root_path)
        if prefix in self.prefixes:
            loader = self.prefixes[prefix]
            if root_path in loader.searchpath:
                return
            logger.debug(f"Adding folder `{root_path}` with the prefix `{prefix}`")
            loader.searchpath.append(root_path)
        else:
            logger.debug(f"Adding folder `{root_path}` with the prefix `{prefix}`")
            self.prefixes[prefix] = jinja2.FileSystemLoader(root_path)

    def add_module(self, module: t.Any, *, prefix: str | None = None) -> None:
        mprefix = prefix if prefix is not None else getattr(module, "prefix", DEFAULT_PREFIX)
        self.add_folder(module.components_path, prefix=mprefix)

    def render(
        self,
        __name: str,
        *,
        caller: "t.Callable | None" = None,
        **kw,
    ) -> str:
        self.collected_css = []
        self.collected_js = []
        self.tmpl_globals = kw.pop("__globals", None)
        return self.irender(__name, caller=caller, **kw)

    def irender(
        self,
        __name: str,
        *,
        caller: "t.Callable | None" = None,
        **kw,
    ) -> str:
        content = (kw.pop("__content", "") or "").strip()
        attrs = kw.pop("__attrs", None) or {}
        file_ext = kw.pop("__file_ext", "")
        source = kw.pop("__source", "")

        prefix, name = self._split_name(__name)
        self.jinja_env.loader = self.prefixes[prefix]

        if source:
            logger.debug("Rendering from source %s", __name)
            component = self._get_from_source(name=name, prefix=prefix, source=source)
        elif self.use_cache:
            logger.debug("Rendering from cache or file %s", __name)
            component = self._get_from_cache(prefix=prefix, name=name, file_ext=file_ext)
        else:
            logger.debug("Rendering from file %s", __name)
            component = self._get_from_file(prefix=prefix, name=name, file_ext=file_ext)

        root_path = component.path.parent if component.path else None

        for url in component.css:
            if (
                root_path
                and self.fingerprint
                and not url.startswith(("http://", "https://"))
            ):
                url = self._fingerprint(root_path, url)

            if url not in self.collected_css:
                self.collected_css.append(url)

        for url in component.js:
            if (
                root_path
                and self.fingerprint
                and not url.startswith(("http://", "https://"))
            ):
                url = self._fingerprint(root_path, url)

            if url not in self.collected_js:
                self.collected_js.append(url)

        attrs = attrs.as_dict if isinstance(attrs, HTMLAttrs) else attrs
        attrs.update(kw)
        kw = attrs
        props, extra = component.filter_args(kw)
        try:
            props[PROP_ATTRS] = HTMLAttrs(extra)
        except Exception as exc:
            raise InvalidArgument(
                f"The arguments of the component <{component.name}>"
                f"were parsed incorrectly as:\n {str(kw)}"
            ) from exc

        props[PROP_CONTENT] = Markup(
            content if content or not caller else caller().strip()
        )
        return component.render(**props)

    def get_middleware(
        self,
        application: t.Callable,
        allowed_ext: "t.Iterable[str] | None" = ALLOWED_EXTENSIONS,
        **kwargs,
    ) -> ComponentsMiddleware:
        logger.debug("Creating middleware")
        middleware = ComponentsMiddleware(
            application=application, allowed_ext=tuple(allowed_ext or []), **kwargs
        )
        for prefix, loader in self.prefixes.items():
            url_prefix = get_url_prefix(prefix)
            url = f"{self.root_url}{url_prefix}"
            for root in loader.searchpath[::-1]:
                middleware.add_files(root, url)

        return middleware

    def get_source(self, cname: str, file_ext: TFileExt = "") -> str:
        prefix, name = self._split_name(cname)
        path, _ = self._get_component_path(prefix, name, file_ext=file_ext)
        return path.read_text()

    def render_assets(self, fingerprint: bool = False) -> str:
        html_css = []
        for url in self.collected_css:
            if not url.startswith(("http://", "https://")):
                url = f"{self.root_url}{url}"
            html_css.append(f'<link rel="stylesheet" href="{url}">')

        html_js = []
        for url in self.collected_js:
            if not url.startswith(("http://", "https://")):
                url = f"{self.root_url}{url}"
            html_js.append(f'<script type="module" src="{url}"></script>')

        return Markup("\n".join(html_css + html_js))

    # Private

    def _fingerprint(self, root: Path, filename: str) -> str:
        relpath = Path(filename.lstrip(os.path.sep))
        filepath = root / relpath
        if not filepath.is_file():
            return filename

        stat = filepath.stat()
        fingerprint = sha256(str(stat.st_mtime).encode()).hexdigest()

        ext = "".join(relpath.suffixes)
        stem = relpath.name.removesuffix(ext)
        parent = str(relpath.parent)
        parent = "" if parent == "." else f"{parent}/"

        return f"{parent}{stem}-{fingerprint}{ext}"

    def _get_from_source(self, *, name: str, prefix: str, source: str) -> Component:
        tmpl = self.jinja_env.from_string(source, globals=self.tmpl_globals)
        component = Component(name=name, prefix=prefix, source=source, tmpl=tmpl)
        return component

    def _get_from_cache(self, *, prefix: str, name: str, file_ext: str) -> Component:
        key = f"{prefix}.{name}.{file_ext}"
        cache = self._from_cache(key)
        if cache:
            component = Component.from_cache(
                cache, auto_reload=self.auto_reload, globals=self.tmpl_globals
            )
            if component:
                return component

        logger.debug("Loading %s", key)
        component = self._get_from_file(prefix=prefix, name=name, file_ext=file_ext)
        self._to_cache(key, component)
        return component

    def _from_cache(self, key: str) -> dict[str, t.Any]:
        if key not in self._cache:
            return {}
        cache = self._cache[key]
        logger.debug("Loading from cache %s", key)
        return cache

    def _to_cache(self, key: str, component: Component) -> None:
        self._cache[key] = component.serialize()

    def _get_from_file(self, *, prefix: str, name: str, file_ext: str) -> Component:
        path, tmpl_name = self._get_component_path(prefix, name, file_ext=file_ext)
        component = Component(name=name, prefix=prefix, path=path)
        component.tmpl = self.jinja_env.get_template(tmpl_name, globals=self.tmpl_globals)
        return component

    def _split_name(self, cname: str) -> tuple[str, str]:
        cname = cname.strip().strip(DELIMITER)
        if DELIMITER not in cname:
            return DEFAULT_PREFIX, cname
        for prefix in self.prefixes.keys():
            _prefix = f"{prefix}{DELIMITER}"
            if cname.startswith(_prefix):
                return prefix, cname.removeprefix(_prefix)
        return DEFAULT_PREFIX, cname

    def _get_component_path(
        self, prefix: str, name: str, file_ext: TFileExt = ""
    ) -> tuple[Path, str]:
        name = name.replace(DELIMITER, SLASH)
        root_paths = self.prefixes[prefix].searchpath
        name_dot = f"{name}."
        file_ext = file_ext or self.file_ext

        for root_path in root_paths:
            for curr_folder, _, files in os.walk(
                root_path, topdown=False, followlinks=True
            ):
                relfolder = os.path.relpath(curr_folder, root_path).strip(".")
                if relfolder and not name_dot.startswith(relfolder):
                    continue

                for filename in files:
                    if relfolder:
                        filepath = f"{relfolder}/{filename}"
                    else:
                        filepath = filename
                    if filepath.startswith(name_dot) and filepath.endswith(file_ext):
                        return Path(curr_folder) / filename, filepath

        raise ComponentNotFound(
            f"Unable to find a file named {name}{file_ext} "
            f"or one following the pattern {name_dot}*{file_ext}"
        )

    def _render_attrs(self, attrs: dict[str, t.Any]) -> Markup:
        html_attrs = []
        for name, value in attrs.items():
            if value != "":
                html_attrs.append(f"{name}={value}")
            else:
                html_attrs.append(name)
        return Markup(" ".join(html_attrs))
