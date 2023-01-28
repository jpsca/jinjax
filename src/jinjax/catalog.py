import os
import typing as t
from pathlib import Path

import jinja2
from markupsafe import Markup

from .component import Component
from .exceptions import ComponentNotFound, InvalidArgument
from .jinjax import JinjaX
from .middleware import ComponentsMiddleware
from .html_attrs import HTMLAttrs
from .utils import logger


if t.TYPE_CHECKING:
    TFileExt = t.Union[tuple[str, ...], str]


DEFAULT_URL_ROOT = "/static/components/"
ALLOWED_EXTENSIONS = (".css", ".js")
DEFAULT_PREFIX = ""
DEFAULT_EXTENSION = ".jinja"
DELIMITER = "."
SLASH = "/"
PROP_ATTRS = "attrs"
PROP_CONTENT = "content"


class Catalog:
    __slots__ = (
        "components",
        "prefixes",
        "root_url",
        "file_ext",
        "jinja_env",
        "collected_css",
        "collected_js",
    )

    def __init__(
        self,
        *,
        globals: "t.Optional[dict[str,t.Any]]" = None,
        filters: "t.Optional[dict[str,t.Any]]" = None,
        tests: "t.Optional[dict[str,t.Any]]" = None,
        extensions: "t.Optional[list]" = None,
        root_url: str = DEFAULT_URL_ROOT,
        file_ext: "TFileExt" = DEFAULT_EXTENSION,
    ) -> None:
        self.components: "dict[str,Component]" = {}
        self.prefixes: "dict[str,jinja2.FileSystemLoader]" = {}
        self.collected_css: "list[str]" = []
        self.collected_js: "list[str]" = []
        self.file_ext = file_ext

        root_url = root_url.strip().rstrip(SLASH)
        self.root_url = f"{root_url}{SLASH}"

        extensions = (extensions or []) + ["jinja2.ext.do", JinjaX]
        jinja_env = jinja2.Environment(
            extensions=extensions,
            undefined=jinja2.StrictUndefined,
        )
        globals = globals or {}
        globals["catalog"] = self
        jinja_env.globals.update(globals)
        jinja_env.filters.update(filters or {})
        jinja_env.tests.update(tests or {})
        jinja_env.extend(catalog=self)
        self.jinja_env = jinja_env

    def add_folder(
        self,
        root_path: "t.Union[str,Path]",
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

    def add_module(self, module: "t.Any", *, prefix: str = "") -> None:
        if hasattr(module, "components_path"):
            prefix = prefix or getattr(module, "prefix", DEFAULT_PREFIX)
            self.add_folder(module.components_path, prefix=prefix)
            return

        for mprefix, path in module.components.items():
            self.add_folder(path, prefix=prefix or mprefix)

    def render(
        self,
        __name: str,
        *,
        caller: "t.Optional[t.Callable]" = None,
        **kw,
    ) -> str:
        content = (kw.pop("__content", "") or "").strip()
        attrs = kw.pop("__attrs", None) or {}
        file_ext = kw.pop("__file_ext", "")
        source = kw.pop("__source", "")
        prefix, name = self._split_name(__name)
        url_prefix = self._get_url_prefix(prefix)
        self.jinja_env.loader = self.prefixes[prefix]

        if source:
            logger.debug("Rendering from source %s", __name)
            tmpl = self.jinja_env.from_string(source)
        else:
            root_path, path = self._get_component_path(prefix, name, file_ext=file_ext)
            tmpl_name = str(path.relative_to(root_path))
            logger.debug("Rendering %s", tmpl_name)
            tmpl = self.jinja_env.get_template(tmpl_name)
            source = path.read_text()

        component = Component(name=__name, url_prefix=url_prefix, source=source)
        for css in component.css:
            if css not in self.collected_css:
                self.collected_css.append(css)
        for js in component.js:
            if js not in self.collected_js:
                self.collected_js.append(js)

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

        props[PROP_CONTENT] = content if content or not caller else caller().strip()
        return tmpl.render(**props).strip()

    def get_middleware(
        self,
        application: "t.Callable",
        allowed_ext: "t.Optional[t.Iterable[str]]" = ALLOWED_EXTENSIONS,
        **kwargs,
    ) -> ComponentsMiddleware:
        middleware = ComponentsMiddleware(
            application=application,
            allowed_ext=tuple(allowed_ext or []),
            **kwargs
        )

        for prefix, loader in self.prefixes.items():
            url_prefix = self._get_url_prefix(prefix)
            url = f"{self.root_url}{url_prefix}"
            for root in loader.searchpath[::-1]:
                middleware.add_files(root, url)

        return middleware

    def get_source(self, cname: str, file_ext: "TFileExt" = "") -> str:
        prefix, name = self._split_name(cname)
        _root_path, path = self._get_component_path(prefix, name, file_ext=file_ext)
        return Path(path).read_text()

    def render_assets(self) -> str:
        html_css = [
            f'<link rel="stylesheet" href="{self.root_url}{css}">'
            for css in self.collected_css
        ]
        html_js = [
            f'<script src="{self.root_url}{js}" defer></script>'
            for js in self.collected_js
        ]
        return Markup("\n".join(html_css + html_js))

    # Private

    def _split_name(self, cname: str) -> "tuple[str, str]":
        cname = cname.strip().strip(DELIMITER)
        if DELIMITER not in cname:
            return DEFAULT_PREFIX, cname
        for prefix in self.prefixes.keys():
            _prefix = f"{prefix}{DELIMITER}"
            if cname.startswith(_prefix):
                return prefix, cname.removeprefix(_prefix)
        return DEFAULT_PREFIX, cname

    def _get_url_prefix(self, prefix: str) -> str:
        url_prefix = (
            prefix.strip().strip(f"{DELIMITER}{SLASH}").replace(DELIMITER, SLASH)
        )
        if url_prefix:
            url_prefix = f"{url_prefix}{SLASH}"
        return url_prefix

    def _get_component_path(
        self, prefix: str, name: str, file_ext: "TFileExt" = ""
    ) -> "tuple[Path, Path]":
        name = name.replace(DELIMITER, SLASH)
        name_dot = f"{name}."
        file_ext = file_ext or self.file_ext
        root_paths = self.prefixes[prefix].searchpath

        for root_path in root_paths:
            for curr_folder, _folders, files in os.walk(
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
                        return Path(root_path), Path(curr_folder) / filename

        raise ComponentNotFound(
            f"Unable to found a file named {name}{file_ext} "
            f"nor one following the pattern {name_dot}*{file_ext}"
        )

    def _render_attrs(self, attrs: dict) -> "Markup":
        html_attrs = []
        for name, value in attrs.items():
            if value != "":
                html_attrs.append(f"{name}={value}")
            else:
                html_attrs.append(name)
        return Markup(" ".join(html_attrs))
