import ast
import re
import typing as t
from keyword import iskeyword
from pathlib import Path

from .exceptions import InvalidArgument, MissingRequiredArgument

if t.TYPE_CHECKING:
    from jinja2 import Template


RX_PROPS_START = re.compile(r"{#-?\s*def\s+")
RX_CSS_START = re.compile(r"{#-?\s*css\s+")
RX_JS_START = re.compile(r"{#-?\s*js\s+")
RX_META_END = re.compile(r"\s*-?#}")
RX_COMMA = re.compile(r"\s*,\s*")

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
        raise InvalidArgument(err)


def is_valid_variable_name(name):
    return name.isidentifier() and not iskeyword(name)


class Component:
    __slots__ = (
        "name",
        "url_prefix",
        "required",
        "optional",
        "css",
        "js",
        "path",
        "mtime",
        "tmpl",
    )

    def __init__(
        self,
        *,
        name: str,
        url_prefix: str = "",
        source: str = "",
        mtime: float = 0,
        tmpl: "Template | None" = None,
        path: "Path | None" = None,
    ) -> None:
        self.name = name
        self.url_prefix = url_prefix
        self.required: "list[str]" = []
        self.optional: "dict[str, t.Any]" = {}
        self.css: "list[str]" = []
        self.js: "list[str]" = []

        if path is not None:
            source = source or path.read_text()
            mtime = mtime or path.stat().st_mtime
        if source:
            self.load_metadata(source)

        self.path = path
        self.mtime = mtime
        self.tmpl = tmpl

    @classmethod
    def from_cache(cls, cache: "dict[str, t.Any]", auto_reload: bool = True) -> "Component | None":
        path = cache["path"]
        mtime = cache["mtime"]

        if auto_reload:
            if not path.is_file() or path.stat().st_mtime != mtime:
                return None

        self = cls(name=cache["name"])
        self.required = cache["required"]
        self.optional = cache["optional"]
        self.css = cache["css"]
        self.js = cache["js"]
        self.path = path
        self.mtime = cache["mtime"]
        self.tmpl = cache["tmpl"]
        return self

    def serialize(self) -> "dict[str, t.Any]":
        return {
            "name": self.name,
            "required": self.required,
            "optional": self.optional,
            "css": self.css,
            "js": self.js,
            "path": self.path,
            "mtime": self.mtime,
            "tmpl": self.tmpl,
        }

    def load_metadata(self, source: str) -> None:
        header = source.lstrip().split("#}", maxsplit=3)[:3][::-1]

        while header:
            line = header.pop()
            line = line.strip() + "#}"

            if not (self.required or self.optional):
                expr = self.read_metadata_line(line, RX_PROPS_START)
                if expr:
                    self.required, self.optional = self.parse_args_expr(expr)
                    continue

            if not self.css:
                expr = self.read_metadata_line(line, RX_CSS_START)
                if expr:
                    self.css = self.parse_files_expr(expr)
                    continue

            if not self.js:
                expr = self.read_metadata_line(line, RX_JS_START)
                if expr:
                    self.js = self.parse_files_expr(expr)
                    continue

            # Stop searching if the line didn't contain any parseable metadata
            break

    def read_metadata_line(self, source: str, rx_start: re.Pattern) -> str:
        start = rx_start.match(source)
        if not start:
            return ""
        end = RX_META_END.search(source, pos=start.end())
        if not end:
            raise InvalidArgument(self.name)
        return source[start.end() : end.start()].strip()

    def parse_args_expr(self, expr: str) -> "tuple[list[str], dict[str, t.Any]]":
        expr = expr.strip(" *,/")
        required = []
        optional = {}

        try:
            p = ast.parse(f"def component(*, {expr}): pass")
        except SyntaxError as err:
            raise InvalidArgument(err)
        args = p.body[0].args  # type: ignore
        arg_names = [arg.arg for arg in args.kwonlyargs]
        for name, value in zip(arg_names, args.kw_defaults):
            if value is None:
                required.append(name)
                continue
            expr = ast.unparse(value)
            optional[name] = eval_expression(expr)

        return required, optional

    def parse_files_expr(self, expr: str) -> "list[str]":
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
        self, kw: "dict[str, t.Any]"
    ) -> "tuple[dict[str, t.Any], dict[str, t.Any]]":
        props = {}

        for key in self.required:
            if key not in kw:
                raise MissingRequiredArgument(self.name, key)
            props[key] = kw.pop(key)

        for key in self.optional:
            props[key] = kw.pop(key, self.optional[key])
        extra = kw.copy()
        return props, extra

    def render(self, **kwargs):
        assert self.tmpl, f"Component {self.name} has no template"
        return self.tmpl.render(**kwargs).strip()

    def __repr__(self) -> str:
        return f'<Component "{self.name}">'
