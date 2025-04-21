"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
import ast
import re
import typing as t
from keyword import iskeyword
from pathlib import Path

from jinja2 import Template
from markupsafe import Markup

from .exceptions import (
    DuplicateDefDeclaration,
    InvalidArgument,
    MissingRequiredArgument,
)
from .utils import ARGS_PREFIX, get_url_prefix


if t.TYPE_CHECKING:
    from typing_extensions import Self

RX_COMMA = re.compile(r"\s*,\s*")

RX_ARGS_START = re.compile(r"{#-?\s*def\s+")
RX_CSS_START = re.compile(r"{#-?\s*css\s+")
RX_JS_START = re.compile(r"{#-?\s*js\s+")

# This regexp matches the meta declarations (`{#def .. #}``, `{#css .. #}``,
# and `{#js .. #}`) and regular Jinja comments AT THE BEGINNING of the components source.
# You can also have comments inside the declarations.
RX_META_HEADER = re.compile(r"^(\s*{#.*?#})+", re.DOTALL)

# This regexep matches comments (everything after a `#`)
# Used to remove them from inside meta declarations
RX_INTER_COMMENTS = re.compile(r"\s*#[^\n]*")


ALLOWED_NAMES_IN_EXPRESSION_VALUES = {
    "len": len,
    "max": max,
    "min": min,
    "pow": pow,
    "sum": sum,
    # Jinja allows using lowercase booleans, so we do it too for consistency
    "false": False,
    "true": True,
}


def eval_expression(input_string):
    code = compile(input_string, "<string>", "eval")
    for name in code.co_names:
        if name not in ALLOWED_NAMES_IN_EXPRESSION_VALUES:
            raise InvalidArgument(f"Use of {name} not allowed")
    try:
        return eval(code, {"__builtins__": {}}, ALLOWED_NAMES_IN_EXPRESSION_VALUES)
    except NameError as err:
        raise InvalidArgument(err) from err


def is_valid_variable_name(name):
    return name.isidentifier() and not iskeyword(name)


class Component:
    """Internal class
    """
    __slots__ = (
        "name",
        "prefix",
        "url_prefix",
        "required",
        "optional",
        "css",
        "js",
        "path",
        "relpath",
        "mtime",
        "tmpl",
    )

    def __init__(
        self,
        *,
        name: str,
        prefix: str = "",
        url_prefix: str = "",
        source: str = "",
        mtime: float = 0,
        tmpl: "Template | None" = None,
        path: "Path | None" = None,
        relpath: "Path | None" = None,
    ) -> None:
        self.name = name
        self.prefix = prefix
        self.url_prefix = url_prefix or get_url_prefix(prefix)
        self.required: list[str] = []
        self.optional: dict[str, t.Any] = {}
        self.css: list[str] = []
        self.js: list[str] = []

        if path is not None:
            source = source or path.read_text()
            mtime = mtime or path.stat().st_mtime
        if source:
            self.load_metadata(source)

        if path is not None and relpath is not None:
            default_css = str(relpath.with_suffix(".css").as_posix())
            if (path.with_suffix(".css")).is_file():
                self.css.extend(self.parse_files_expr(default_css))

            default_js = str(relpath.with_suffix(".js").as_posix())
            if (path.with_suffix(".js")).is_file():
                self.js.extend(self.parse_files_expr(default_js))

        self.path = path
        self.relpath = relpath
        self.mtime = mtime
        self.tmpl = tmpl

    @classmethod
    def from_cache(
        cls,
        cache: dict[str, t.Any],
        auto_reload: bool = True,
        globals: "t.MutableMapping[str, t.Any] | None" = None,
    ) -> "Self | None":
        path = cache["path"]
        mtime = cache["mtime"]

        if auto_reload:
            if not path.is_file() or path.stat().st_mtime != mtime:
                return None

        self = cls(name=cache["name"])
        self.prefix = cache["prefix"]
        self.url_prefix = cache["url_prefix"]
        self.required = cache["required"]
        self.optional = cache["optional"]
        self.css = cache["css"]
        self.js = cache["js"]
        self.path = path
        self.mtime = cache["mtime"]
        self.tmpl = cache["tmpl"]

        if globals:
            # Create a copy of the globals dictionary to ensure thread safety
            globals_copy = self.tmpl.globals.copy()
            globals_copy.update(globals)
            self.tmpl.globals = globals_copy

        return self

    def serialize(self) -> dict[str, t.Any]:
        return {
            "name": self.name,
            "prefix": self.prefix,
            "url_prefix": self.url_prefix,
            "required": self.required,
            "optional": self.optional,
            "css": self.css,
            "js": self.js,
            "path": self.path,
            "mtime": self.mtime,
            "tmpl": self.tmpl,
        }

    def load_metadata(self, source: str) -> None:
        match = RX_META_HEADER.match(source)
        if not match:
            return

        header = match.group(0)
        # Reversed because I will use `header.pop()`
        header = header.split("#}")[:-1][::-1]
        def_found = False

        while header:
            item = header.pop().strip(" -\n")

            expr = self.read_metadata_item(item, RX_ARGS_START)
            if expr:
                if def_found:
                    raise DuplicateDefDeclaration(self.name)
                self.required, self.optional = self.parse_args_expr(expr)
                def_found = True
                continue

            expr = self.read_metadata_item(item, RX_CSS_START)
            if expr:
                expr = RX_INTER_COMMENTS.sub("", expr).replace("\n", " ")
                self.css = [*self.css, *self.parse_files_expr(expr)]
                continue

            expr = self.read_metadata_item(item, RX_JS_START)
            if expr:
                expr = RX_INTER_COMMENTS.sub("", expr).replace("\n", " ")
                self.js = [*self.js, *self.parse_files_expr(expr)]
                continue

    def read_metadata_item(self, source: str, rx_start: re.Pattern) -> str:
        start = rx_start.match(source)
        if not start:
            return ""
        return source[start.end():].strip()

    def parse_args_expr(self, expr: str) -> tuple[list[str], dict[str, t.Any]]:
        expr = expr.strip(" *,/")
        required = []
        optional = {}

        try:
            p = ast.parse(f"def component(*,\n{expr}\n): pass")
        except SyntaxError as err:
            raise InvalidArgument(err) from err

        args = p.body[0].args  # type: ignore
        arg_names = [arg.arg for arg in args.kwonlyargs]
        for name, value in zip(arg_names, args.kw_defaults):  # noqa: B905
            if value is None:
                required.append(name)
                continue
            expr = ast.unparse(value)
            optional[name] = eval_expression(expr)

        return required, optional

    def parse_files_expr(self, expr: str) -> list[str]:
        files = []
        for url in RX_COMMA.split(expr):
            url = url.strip("\"'").rstrip("/")
            if not url:
                continue
            if url.startswith(("/", "http://", "https://")):
                files.append(url)
            else:
                files.append(f"{self.url_prefix}{url}")
        return files

    def filter_args(
        self, kw: dict[str, t.Any]
    ) -> tuple[dict[str, t.Any], dict[str, t.Any]]:
        args = {}

        for key in self.required:
            if key not in kw:
                raise MissingRequiredArgument(self.name, key)
            args[key] = kw.pop(key)

        for key in self.optional:
            args[key] = kw.pop(key, self.optional[key])
        extra = kw.copy()
        return args, extra

    def render(self, **kwargs):
        assert self.tmpl, f"Component {self.name} has no template"
        kwargs.setdefault(ARGS_PREFIX, self.prefix)
        html = self.tmpl.render(**kwargs).strip()
        return Markup(html)

    def __repr__(self) -> str:
        return f'<Component "{self.name}">'
