"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
import os
import typing as t
from collections import UserString
from contextvars import ContextVar
from hashlib import sha256
from pathlib import Path

import jinja2
from markupsafe import Markup

from .component import Component
from .exceptions import ComponentNotFound, InvalidArgument, UnknownPrefix
from .html_attrs import HTMLAttrs
from .jinjax import JinjaX
from .utils import (
    ARGS_PREFIX,
    DELIMITER,
    SLASH,
    get_random_id,
    get_url_prefix,
    kebab_case,
    logger,
)


if t.TYPE_CHECKING:
    from .middleware import ComponentsMiddleware


DEFAULT_URL_ROOT = "/static/components/"
ALLOWED_EXTENSIONS = (".css", ".js", ".mjs")
DEFAULT_PREFIX = ""
DEFAULT_EXTENSION = ".jinja"
ARGS_ATTRS = "attrs"
ARGS_CONTENT = "content"
PREFIX_SEP = ":"

# Create ContextVars containers at module level
collected_css: dict[int, ContextVar[list[str]]] = {}
collected_js: dict[int, ContextVar[list[str]]] = {}
tmpl_globals: dict[int, ContextVar[dict[str, t.Any]]] = {}

RelPath = Path


class CallerWrapper(UserString):
    _content = ""

    def __init__(self, caller: t.Callable | None, content: str = "") -> None:
        self._caller = caller
        # Pre-calculate the defaut content so the assets are loaded
        self._content = caller("") if caller else Markup(content)

    def __call__(self, slot: str = "") -> str:
        if slot and self._caller:
            return self._caller(slot)
        return self._content

    def __html__(self) -> str:
        return self.__call__()

    def __repr__(self) -> str:
        return self._content

    @property
    def data(self) -> str:  # type: ignore
        return self.__call__()


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
        "_cache",
        "_key",
    )

    def __init__(
        self,
        *,
        globals: dict[str, t.Any] | None = None,
        filters: dict[str, t.Any] | None = None,
        tests: dict[str, t.Any] | None = None,
        extensions: list | None = None,
        jinja_env: jinja2.Environment | None = None,
        root_url: str = DEFAULT_URL_ROOT,
        file_ext: str = DEFAULT_EXTENSION,
        use_cache: bool = True,
        auto_reload: bool = True,
        fingerprint: bool = False,
    ) -> None:
        self.prefixes: dict[str, jinja2.FileSystemLoader] = {}
        self.file_ext = file_ext or DEFAULT_EXTENSION
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
        globals["get_random_id"] = get_random_id
        filters["catalog"] = self
        filters["random_id"] = get_random_id

        for ext in extensions:
            env.add_extension(ext)
        env.globals.update(globals)
        env.filters.update(filters)
        env.tests.update(tests)
        env.extend(catalog=self)

        self.jinja_env = env

        self._cache: dict[str, dict] = {}
        self._key = id(self)

    def __del__(self) -> None:
        # Safely clean up context variables associated with this catalog
        try:
            key = self._key
            # Clean up the collected_css
            if key in collected_css:
                del collected_css[key]

            # Clean up the collected_js
            if key in collected_js:
                del collected_js[key]

            # Clean up the tmpl_globals
            if key in tmpl_globals:
                del tmpl_globals[key]
        except Exception:
            # Ignore exceptions during cleanup
            pass

    @property
    def collected_css(self) -> list[str]:
        key = self._key
        if key not in collected_css:
            name = f"collected_css_{key}"
            collected_css[key] = ContextVar(name)
            value = []
            collected_css[key].set(value)
            return value

        try:
            # Make a defensive copy to avoid shared references
            return list(collected_css[key].get())
        except (KeyError, LookupError):
            # Handle case where the ContextVar exists but no value was set
            value = []
            collected_css[key].set(value)
            return value

    @collected_css.setter
    def collected_css(self, value: list[str]) -> None:
        key = self._key
        if key not in collected_css:
            name = f"collected_css_{key}"
            collected_css[key] = ContextVar(name)

        # Make a defensive copy to avoid shared references
        collected_css[key].set(list(value))

    @property
    def collected_js(self) -> list[str]:
        key = self._key
        if key not in collected_js:
            name = f"collected_js_{key}"
            collected_js[key] = ContextVar(name)
            value = []
            collected_js[key].set(value)
            return value

        try:
            # Make a defensive copy to avoid shared references
            return list(collected_js[key].get())
        except (KeyError, LookupError):
            # Handle case where the ContextVar exists but no value was set
            value = []
            collected_js[key].set(value)
            return value

    @collected_js.setter
    def collected_js(self, value: list[str]) -> None:
        key = self._key
        if key not in collected_js:
            name = f"collected_js_{key}"
            collected_js[key] = ContextVar(name)

        # Make a defensive copy to avoid shared references
        collected_js[key].set(list(value))

    @property
    def tmpl_globals(self) -> dict[str, t.Any]:
        key = self._key
        if key not in tmpl_globals:
            name = f"tmpl_globals_{key}"
            tmpl_globals[key] = ContextVar(name)
            value = {}
            tmpl_globals[key].set(value)
            return value

        try:
            # Make a defensive copy to avoid shared references
            return dict(tmpl_globals[key].get())
        except (KeyError, LookupError):
            # Handle case where the ContextVar exists but no value was set
            value = {}
            tmpl_globals[key].set(value)
            return value

    @tmpl_globals.setter
    def tmpl_globals(self, value: dict[str, t.Any]) -> None:
        key = self._key
        if key not in tmpl_globals:
            name = f"tmpl_globals_{key}"
            tmpl_globals[key] = ContextVar(name)

        # Make a defensive copy to avoid shared references
        tmpl_globals[key].set(dict(value))

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
        root_path: str | Path,
        *,
        prefix: str = DEFAULT_PREFIX,
    ) -> None:
        """
        Add a folder path from which to search for components, optionally under a prefix.

        Arguments:

            root_path:
                Absolute path of the folder with component files.

            prefix:
                Optional prefix that all the components in the folder will have.
                The default is empty.

        The prefix acts like a namespace. For example, the name of a
        `Card.jinja` component is, by default, "Card", but under
        the prefix "common", it becomes "common.Card".

        An important caveat is that when a component under a prefix calls another
        component without a prefix, the called component is searched **first**
        under the caller's prefix and then under the empty prefix.

        The rule for subfolders remains the same: a `components/wrappers/Card.jinja`
        name is, by default, "wrappers.Card", but under the prefix "common", it becomes
        "common.wrappers.Card".

        The prefixes take precedence over subfolders, so don't create a subfolder with
        the same name as a prefix because it will be ignored.

        If **under the same prefix** (including the empty one), there are more than one
        component with the same name in multiple added folders, the one in the folder
        added **first** takes precedence. You can use this to override components loaded
        from a library: just add your folder first.

        """
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

    def add_module(self, module: t.Any, *, prefix: str = DEFAULT_PREFIX) -> None:
        """
        DEPRECATED
        Reads an absolute path from `module.components_path` and then calls
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
        self.add_folder(module.components_path, prefix=prefix)

    def render(
        self,
        /,
        __name: str,
        *,
        caller: t.Callable | None = None,
        **kw,
    ) -> str:
        """
        Resets the `collected_css` and `collected_js` lists and renders the
        component and subcomponents inside of it.

        This is the method you should call to render a parent component from a
        view/controller in your app.

        """
        # Clear any existing assets
        self.collected_css = []
        self.collected_js = []
        self.tmpl_globals = kw.pop("_globals", kw.pop("__globals", None)) or {}
        return self.irender(__name, caller=caller, **kw)

    def irender(
        self,
        /,
        __name: str,
        *,
        caller: t.Callable | None = None,
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

        component = self._get_component(__name, **kw)
        root_path = component.path.parent if component.path else None

        # Get current assets lists
        css_list = self.collected_css
        js_list = self.collected_js

        # Process CSS assets
        css_to_add = []
        for url in component.css:
            if (
                root_path
                and self.fingerprint
                and not url.startswith(("http://", "https://"))
            ):
                url = self._fingerprint(root_path, url)

            if url not in css_list:
                css_to_add.append(url)

        # Update CSS assets in one operation if needed
        if css_to_add:
            new_css = list(css_list)
            new_css.extend(css_to_add)
            self.collected_css = new_css

        # Process JS assets
        js_to_add = []
        for url in component.js:
            if (
                root_path
                and self.fingerprint
                and not url.startswith(("http://", "https://"))
            ):
                url = self._fingerprint(root_path, url)

            if url not in js_list:
                js_to_add.append(url)

        # Update JS assets in one operation if needed
        if js_to_add:
            new_js = list(js_list)
            new_js.extend(js_to_add)
            self.collected_js = new_js

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
        allowed_ext: t.Iterable[str] | None = ALLOWED_EXTENSIONS,
        **kwargs,
    ) -> "ComponentsMiddleware":
        """
        Wraps you application with
        [Withenoise](https://whitenoise.readthedocs.io/),
        a static file serving middleware.

        Tecnically not necessary if your components doesn't use static assets
        or if you serve them by other means. Requires the `whitenoise` python
        package to be installed.

        Arguments:

            application:
                A WSGI application

            allowed_ext:
                A list of file extensions the static middleware is allowed to
                read and return. By default, is just ".css", ".js", and ".mjs".

        """
        from .middleware import ComponentsMiddleware

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
        file_ext: str = "",
    ) -> str:
        """
        A helper method that returns the source file of a component.
        """
        file_ext = file_ext or self.file_ext
        prefix, name = self._split_name(cname)
        paths = self._get_component_path(prefix, name, file_ext=file_ext)
        if not paths:
            raise ComponentNotFound(cname, file_ext)
        return paths[0].read_text()

    def render_assets(self) -> str:
        """
        Uses the `collected_css` and `collected_js` lists to generate
        an HTML fragment with `<link rel="stylesheet" href="{url}">`
        and `<script type="module" src="{url}"></script>` tags.

        The URLs are prepended by `root_url` unless they begin with
        "http://" or "https://".
        """
        html_css = []
        # Use a set to track rendered URLs to avoid duplicates
        rendered_urls = set()

        for url in self.collected_css:
            if not url.startswith(("http://", "https://")):
                full_url = f"{self.root_url}{url}"
            else:
                full_url = url

            if full_url not in rendered_urls:
                html_css.append(f'<link rel="stylesheet" href="{full_url}">')
                rendered_urls.add(full_url)

        html_js = []
        for url in self.collected_js:
            if not url.startswith(("http://", "https://")):
                full_url = f"{self.root_url}{url}"
            else:
                full_url = url

            if full_url not in rendered_urls:
                html_js.append(f'<script type="module" src="{full_url}"></script>')
                rendered_urls.add(full_url)

        return Markup("\n".join(sorted(html_css) + sorted(html_js)))

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

    def _get_component(self, cname: str, **kw) -> Component:
        source = kw.pop("_source", kw.pop("__source", ""))
        file_ext = kw.pop("_file_ext", kw.pop("__file_ext", "")) or self.file_ext
        caller_prefix = kw.pop(ARGS_PREFIX, "")

        prefix, name = self._split_name(cname)
        component = None

        if source:
            logger.debug("Rendering from source %s", cname)
            self.jinja_env.loader = self.prefixes[prefix]
            return self._get_from_source(prefix=prefix, name=name, source=source)

        logger.debug("Rendering from cache or file %s", cname)
        get_from = self._get_from_cache if self.use_cache else self._get_from_file
        if caller_prefix:
            self.jinja_env.loader = self.prefixes[caller_prefix]
            component = get_from(
                prefix=caller_prefix,
                name=cname,
                file_ext=file_ext
            )
        if not component:
            self.jinja_env.loader = self.prefixes[prefix]
            component = get_from(
                prefix=prefix,
                name=name,
                file_ext=file_ext
            )
        if component:
            return component
        raise ComponentNotFound(cname, file_ext)

    def _get_from_source(
        self,
        *,
        prefix: str,
        name: str,
        source: str,
    ) -> Component:
        tmpl = self.jinja_env.from_string(source, globals=self.tmpl_globals)
        component = Component(prefix=prefix, name=name, source=source, tmpl=tmpl)
        return component

    def _get_from_cache(
        self,
        *,
        prefix: str,
        name: str,
        file_ext: str,
    ) -> Component | None:
        key = f"{prefix}.{name}{file_ext}"
        cache = self._from_cache(key)

        if cache:
            component = Component.from_cache(
                cache, auto_reload=self.auto_reload, globals=self.tmpl_globals
            )
            if component:
                return component

        logger.debug("Loading %s", key)
        component = self._get_from_file(prefix=prefix, name=name, file_ext=file_ext)
        if not component:
            return
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

    def _get_from_file(self, *, prefix: str, name: str, file_ext: str) -> Component | None:
        paths = self._get_component_path(prefix, name, file_ext=file_ext)
        if not paths:
            return
        path, relpath = paths
        component = Component(name=name, prefix=prefix, path=path, relpath=relpath)
        component.tmpl = self.jinja_env.get_template(str(relpath.as_posix()), globals=self.tmpl_globals)
        return component

    def _split_name(self, cname: str) -> tuple[str, str]:
        cname = cname.strip().strip(DELIMITER)
        if PREFIX_SEP not in cname:
            return DEFAULT_PREFIX, cname

        prefix, cname = cname.split(PREFIX_SEP, 1)
        if prefix not in self.prefixes:
            raise UnknownPrefix(prefix)
        return prefix, cname

    def _get_component_path(
        self,
        prefix: str,
        name: str,
        file_ext: str,
    ) -> tuple[Path, RelPath] | None:
        root_paths = self.prefixes[prefix].searchpath

        name = name.replace(DELIMITER, SLASH)
        kebab_name = kebab_case(name)
        dot_names = (f"{name}.", f"{kebab_name}.")

        for root_path in root_paths:
            for curr_folder, _, files in os.walk(
                root_path, topdown=False, followlinks=True
            ):
                relfolder = os.path.relpath(curr_folder, root_path).strip(".")
                if relfolder:
                    if not (
                        name.startswith(relfolder)
                        or kebab_name.startswith(relfolder)
                    ):
                        continue

                    # Allow for index.jinja files in subfolders
                    # to be called with just the folder name
                    if relfolder in (name, kebab_name):
                        filename = f"index{file_ext}"
                        fullpath = Path(curr_folder) / filename
                        if fullpath.is_file():
                            relpath = Path(f"{relfolder}/{filename}")
                            return fullpath, relpath

                for filename in files:
                    if relfolder:
                        filepath = f"{relfolder}/{filename}"
                    else:
                        filepath = filename

                    if filepath.startswith(dot_names) and filepath.endswith(file_ext):
                        fullpath = Path(curr_folder) / filename
                        relpath = Path(filepath)
                        if fullpath.is_file():
                            return fullpath, relpath

    def _render_attrs(self, attrs: dict[str, t.Any]) -> Markup:
        html_attrs = []
        for name, value in attrs.items():
            if value != "":
                html_attrs.append(f"{name}={value}")
            else:
                html_attrs.append(name)
        return Markup(" ".join(html_attrs))
