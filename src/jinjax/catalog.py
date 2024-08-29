import os
import typing as t
from collections import UserString
from contextvars import ContextVar
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


DEFAULT_URL_ROOT = "/static/components/"
ALLOWED_EXTENSIONS = (".css", ".js", ".mjs")
DEFAULT_PREFIX = ""
DEFAULT_EXTENSION = ".jinja"
ARGS_ATTRS = "attrs"
ARGS_CONTENT = "content"

# Create ContextVars containers at module level
collected_css: dict[int, ContextVar[list[str]]] = {}
collected_js: dict[int, ContextVar[list[str]]] = {}


class CallerWrapper(UserString):
    def __init__(self, caller: t.Callable | None, content: str = "") -> None:
        self._caller = caller
        # Pre-calculate the defaut content so the assets are loaded
        self._content = caller("") if caller else Markup(content)

    def __call__(self, slot: str = "") -> str:
        if slot and self._caller:
            return self._caller(slot)
        return self._content

    def __html__(self) -> str:
        return self()

    @property
    def data(self) -> str:  # type: ignore
        return self()


class Catalog:
    """
    The object that manages the components and their global settings.

    Arguments:

        globals:
            Dictionary of Jinja globals to add to the Catalog's Jinja
            environment (or the one passed in `jinja_env`).

        filters:
            Dictionary of Jinja filters to add to the Catalog's Jinja
            environment (or the one passed in `jinja_env`).

        tests:
            Dictionary of Jinja tests to add to the Catalog's Jinja environment
            (or the one passed in `jinja_env`).

        extensions:
            List of Jinja extensions to add to the Catalog's Jinja environment
            (or the one passed in `jinja_env`). The `jinja2.ext.do` extension
            is always added at the end of these.

        jinja_env:
            Custom Jinja environment to use. This argument is useful to reuse
            an existing Jinja Environment from your web framework.

        root_url:
            Add this prefix to every asset URL of the static middleware.
            By default, it is `/static/components/`, so, for example,
            the URL of the CSS file of a `Card` component is
            `/static/components/Card.css`.

            You can also change this argument so the assets are requested from
            a Content Delivery Network (CDN) in production, for example,
            `root_url="https://example.my-cdn.com/"`.

        file_ext:
            The extensions the components files have. By default, ".jinja".

            This argument can also be a list to allow more than one type of
            file to be a component.

        use_cache:
            Cache the metadata of the component in memory.

        auto_reload:
            Used with `use_cache`. If `True`, the last-modified date of the
            component file is checked every time to see if the cache
            is up-to-date.

            Set to `False` in production.

        fingerprint:
            If `True`, inserts a hash of the updated time into the URL of the
            asset files (after the name but before the extension).

            This strategy encourages long-term caching while ensuring that
            new copies are only requested when the content changes, as any
            modification alters the fingerprint and thus the filename.

            **WARNING**: Only works if the server knows how to filter the
            fingerprint to get the real name of the file.

    Attributes:

        collected_css:
            List of CSS paths collected during a render.

        collected_js:
            List of JS paths collected during a render.

        prefixes:
            Mapping between folder prefixes and the Jinja loader that uses.

    """

    __slots__ = (
        "prefixes",
        "root_url",
        "file_ext",
        "jinja_env",
        "fingerprint",
        "auto_reload",
        "use_cache",
        "_tmpl_globals",
        "_cache",
        "_key",
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
        file_ext: "str | list[str] | tuple[str, ...]" = DEFAULT_EXTENSION,
        use_cache: bool = True,
        auto_reload: bool = True,
        fingerprint: bool = False,
    ) -> None:
        self.prefixes: dict[str, jinja2.FileSystemLoader] = {}
        if isinstance(file_ext, list):
            file_ext = tuple(file_ext)
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

        self._tmpl_globals: "t.MutableMapping[str, t.Any] | None" = None
        self._cache: dict[str, dict] = {}
        self._key = id(self)

    def __del__(self) -> None:
        name = f"collected_css_{self._key}"
        if name in collected_css:
            del collected_css[name]
        name = f"collected_js_{self._key}"
        if name in collected_js:
            del collected_js[name]

    @property
    def collected_css(self) -> list[str]:
        if self._key not in collected_css:
            name = f"collected_css_{self._key}"
            collected_css[self._key] = ContextVar(name, default=[])
        return collected_css[self._key].get()

    @collected_css.setter
    def collected_css(self, value: list[str]) -> None:
        if self._key not in collected_css:
            name = f"collected_css_{self._key}"
            collected_css[self._key] = ContextVar(name, default=[])
        collected_css[self._key].set(list(value))

    @property
    def collected_js(self) -> list[str]:
        if self._key not in collected_js:
            name = f"collected_js_{self._key}"
            collected_js[self._key] = ContextVar(name, default=[])
        return collected_js[self._key].get()

    @collected_js.setter
    def collected_js(self, value: list[str]) -> None:
        if self._key not in collected_js:
            name = f"collected_js_{self._key}"
            collected_js[self._key] = ContextVar(name, default=[])
        collected_js[self._key].set(list(value))

    @property
    def paths(self) -> list[Path]:
        """
        A helper property that returns a list of all the components
        folder paths.
        """
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
        """
        Add a folder path from where to search for components, optionally
        under a prefix.

        The prefix acts like a namespace. For example, the name of a
        `components/Card.jinja` component is, by default, "Card",
        but under the prefix "common", it becomes "common.Card".

        The rule for subfolders remains the same: a
        `components/wrappers/Card.jinja` name is, by default,
        "wrappers.Card", but under the prefix "common", it
        becomes "common.wrappers.Card".

        If there is more than one component with the same name in multiple
        added folders under the same prefix, the one in the folder added
        first takes precedence.

        Arguments:

            root_path:
                Absolute path of the folder with component files.

            prefix:
                Optional prefix that all the components in the folder will
                have. The default is empty.

        """
        prefix = (
            prefix.strip()
            .strip(f"{DELIMITER}{SLASH}")
            .replace(SLASH, DELIMITER)
        )

        root_path = str(root_path)
        if prefix in self.prefixes:
            loader = self.prefixes[prefix]
            if root_path in loader.searchpath:
                return
            logger.debug(
                f"Adding folder `{root_path}` with the prefix `{prefix}`"
            )
            loader.searchpath.append(root_path)
        else:
            logger.debug(
                f"Adding folder `{root_path}` with the prefix `{prefix}`"
            )
            self.prefixes[prefix] = jinja2.FileSystemLoader(root_path)

    def add_module(self, module: t.Any, *, prefix: str | None = None) -> None:
        """
        Reads an absolute path from `module.components_path` and an optional
        prefix from `module.prefix`, then calls
        `Catalog.add_folder(path, prefix)`.

        The prefix can also be passed as an argument instead of being read
        from the module.

        This method exists to make it easy and consistent to have
        components installable as Python libraries.

        Arguments:

            module:
                A Python module.

            prefix:
                An optional prefix that replaces the one the module
                might include.

        """
        mprefix = (
            prefix
            if prefix is not None
            else getattr(module, "prefix", DEFAULT_PREFIX)
        )
        self.add_folder(module.components_path, prefix=mprefix)

    def render(
        self,
        /,
        __name: str,
        *,
        caller: "t.Callable | None" = None,
        **kw,
    ) -> str:
        """
        Resets the `collected_css` and `collected_js` lists and renders the
        component and subcomponents inside of it.

        This is the method you should call to render a parent component from a
        view/controller in your app.

        """
        self.collected_css = []
        self.collected_js = []
        self._tmpl_globals = kw.pop("__globals", None)
        return self.irender(__name, caller=caller, **kw)

    def irender(
        self,
        /,
        __name: str,
        *,
        caller: "t.Callable | None" = None,
        **kw,
    ) -> str:
        """
        Renders the component and subcomponents inside of it **without**
        resetting the `collected_css` and `collected_js` lists.

        This is the method you should call to render individual components that
        are later inserted into a parent template.

        """
        content = (kw.pop("_content", kw.pop("__content", "")) or "").strip()
        attrs = kw.pop("_attrs", kw.pop("__attrs", None)) or {}
        file_ext = kw.pop("_file_ext", kw.pop("__file_ext", ""))
        source = kw.pop("_source", kw.pop("__source", ""))

        prefix, name = self._split_name(__name)
        self.jinja_env.loader = self.prefixes[prefix]

        if source:
            logger.debug("Rendering from source %s", __name)
            component = self._get_from_source(
                name=name, prefix=prefix, source=source
            )
        elif self.use_cache:
            logger.debug("Rendering from cache or file %s", __name)
            component = self._get_from_cache(
                prefix=prefix, name=name, file_ext=file_ext
            )
        else:
            logger.debug("Rendering from file %s", __name)
            component = self._get_from_file(
                prefix=prefix, name=name, file_ext=file_ext
            )

        root_path = component.path.parent if component.path else None

        css = self.collected_css
        js = self.collected_js

        for url in component.css:
            if (
                root_path
                and self.fingerprint
                and not url.startswith(("http://", "https://"))
            ):
                url = self._fingerprint(root_path, url)

            if url not in css:
                css.append(url)

        for url in component.js:
            if (
                root_path
                and self.fingerprint
                and not url.startswith(("http://", "https://"))
            ):
                url = self._fingerprint(root_path, url)

            if url not in js:
                js.append(url)

        attrs = attrs.as_dict if isinstance(attrs, HTMLAttrs) else attrs
        attrs.update(kw)
        kw = attrs
        args, extra = component.filter_args(kw)
        try:
            args[ARGS_ATTRS] = HTMLAttrs(extra)
        except Exception as exc:
            raise InvalidArgument(
                f"The arguments of the component <{component.name}>"
                f"were parsed incorrectly as:\n {str(kw)}"
            ) from exc

        args[ARGS_CONTENT] = CallerWrapper(caller=caller, content=content)
        return component.render(**args)

    def get_middleware(
        self,
        application: t.Callable,
        allowed_ext: "t.Iterable[str] | None" = ALLOWED_EXTENSIONS,
        **kwargs,
    ) -> ComponentsMiddleware:
        """
        Wraps you application with
        [Withenoise](https://whitenoise.readthedocs.io/),
        a static file serving middleware.

        Tecnically not neccesary if your components doesn't use static assets
        or if you serve them by other means.

        Arguments:

            application:
                A WSGI application

            allowed_ext:
                A list of file extensions the static middleware is allowed to
                read and return. By default, is just ".css", ".js", and ".mjs".

        """
        logger.debug("Creating middleware")
        middleware = ComponentsMiddleware(
            application=application,
            allowed_ext=tuple(allowed_ext or []),
            **kwargs,
        )
        for prefix, loader in self.prefixes.items():
            url_prefix = get_url_prefix(prefix)
            url = f"{self.root_url}{url_prefix}"
            for root in loader.searchpath[::-1]:
                middleware.add_files(root, url)

        return middleware

    def get_source(
        self,
        cname: str,
        file_ext: "tuple[str, ...] | str" = "",
    ) -> str:
        """
        A helper method that returns the source file of a component.
        """
        prefix, name = self._split_name(cname)
        path, _ = self._get_component_path(prefix, name, file_ext=file_ext)
        return path.read_text()

    def render_assets(self) -> str:
        """
        Uses the `collected_css` and `collected_js` lists to generate
        an HTML fragment with `<link rel="stylesheet" href="{url}">`
        and `<script type="module" src="{url}"></script>` tags.

        The URLs are prepended by `root_url` unless they begin with
        "http://" or "https://".
        """
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

    def _get_from_source(
        self,
        *,
        name: str,
        prefix: str,
        source: str,
    ) -> Component:
        tmpl = self.jinja_env.from_string(source, globals=self._tmpl_globals)
        component = Component(
            name=name, prefix=prefix, source=source, tmpl=tmpl
        )
        return component

    def _get_from_cache(
        self,
        *,
        prefix: str,
        name: str,
        file_ext: str,
    ) -> Component:
        key = f"{prefix}.{name}.{file_ext}"
        cache = self._from_cache(key)
        if cache:
            component = Component.from_cache(
                cache, auto_reload=self.auto_reload, globals=self._tmpl_globals
            )
            if component:
                return component

        logger.debug("Loading %s", key)
        component = self._get_from_file(
            prefix=prefix, name=name, file_ext=file_ext
        )
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

    def _get_from_file(
        self, *, prefix: str, name: str, file_ext: str
    ) -> Component:
        path, tmpl_name = self._get_component_path(
            prefix, name, file_ext=file_ext
        )
        component = Component(name=name, prefix=prefix, path=path)
        component.tmpl = self.jinja_env.get_template(
            tmpl_name, globals=self._tmpl_globals
        )
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
        self,
        prefix: str,
        name: str,
        file_ext: "tuple[str, ...] | str" = "",
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
                    if (
                        filepath.startswith(name_dot) and
                        filepath.endswith(file_ext)
                    ):
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
