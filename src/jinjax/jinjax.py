import re
import typing as t
from uuid import uuid4

from jinja2.ext import Extension
from jinja2.exceptions import TemplateSyntaxError

from .utils import logger


RENDER_CMD = "catalog.irender"
BLOCK_CALL = '{% call [CMD]("[TAG]"[ATTRS]) -%}[CONTENT]{%- endcall %}'
BLOCK_CALL = BLOCK_CALL.replace("[CMD]", RENDER_CMD)
INLINE_CALL = '{{ [CMD]("[TAG]"[ATTRS]) }}'
INLINE_CALL = INLINE_CALL.replace("[CMD]", RENDER_CMD)

re_raw = r"\{%-?\s*raw\s*-?%\}.+?\{%-?\s*endraw\s*-?%\}"
RX_RAW = re.compile(re_raw, re.DOTALL)

re_tag_name = r"([0-9A-Za-z_-]+\.)*[A-Z][0-9A-Za-z_-]*"
re_raw_attrs = r"(?P<attrs>[^\>]*)"
re_tag = rf"<(?P<tag>{re_tag_name}){re_raw_attrs}\s*/?>"
RX_TAG = re.compile(re_tag)

ATTR_START = "{"
ATTR_END = "}"
re_attr_name = r""
re_equal = r""
re_attr = r"""
(?P<name>[a-zA-Z_][0-9a-zA-Z_-]*)
(?:
    \s*=\s*
    (?P<value>".*?"|'.*?'|\{.*?\})
)?
(?:\s+|/|$)
"""
RX_ATTR = re.compile(re_attr, re.VERBOSE | re.DOTALL)


class JinjaX(Extension):
    def preprocess(
        self,
        source: str,
        name: t.Optional[str] = None,
        filename: t.Optional[str] = None,
    ) -> str:
        self.__raw_blocks = {}
        self._name = name
        self._filename = filename
        source = self._replace_raw_blocks(source)
        source = self._process_tags(source)
        source = self._restore_raw_blocks(source)
        self.__raw_blocks = {}
        return source

    def _replace_raw_blocks(self, source: str) -> str:
        while True:
            match = RX_RAW.search(source)
            if not match:
                break
            start, end = match.span(0)
            repl = self._replace_raw_block(match)
            source = f"{source[:start]}{repl}{source[end:]}"

        return source

    def _replace_raw_block(self, match: re.Match) -> str:
        uid = f"--RAW-{uuid4().hex}--"
        self.__raw_blocks[uid] = match.group(0)
        return uid

    def _restore_raw_blocks(self, source: str) -> str:
        for uid, code in self.__raw_blocks.items():
            source = source.replace(uid, code)
        return source

    def _process_tags(self, source: str) -> str:
        while True:
            match = RX_TAG.search(source)
            if not match:
                break
            source = self._process_tag(source, match)
        return source

    def _process_tag(self, source: str, match: re.Match) -> str:
        start, end = match.span(0)
        tag = match.group("tag")
        attrs = (match.group("attrs") or "").strip()
        inline = match.group(0).endswith("/>")
        logger.debug(f"{tag} {attrs} {'inline' if not inline else ''}")

        if inline:
            content = ""
        else:
            end_tag = f"</{tag}>"
            index = source.find(end_tag, end, None)
            if index == -1:
                raise TemplateSyntaxError(
                    message=f"Unclosed component {match.group(0)}",
                    lineno=source[:start].count("\n") + 1,
                    name=self._name,
                    filename=self._filename
                )
            content = source[end:index]
            end = index + len(end_tag)

        attrs_list = self._parse_attrs(attrs)
        repl = self._build_call(tag, attrs_list, content)
        return f"{source[:start]}{repl}{source[end:]}"

    def _parse_attrs(self, attrs: str) -> list[tuple[str, str]]:
        attrs = attrs.replace("\n", " ").strip()
        if not attrs:
            return []
        return RX_ATTR.findall(attrs)

    def _build_call(
        self,
        tag: str,
        attrs_list: list[tuple[str, str]],
        content: str = "",
    ) -> str:
        logger.debug(f"{tag} {attrs_list} {'inline' if not content else ''}")
        attrs = []
        for name, value in attrs_list:
            name = name.strip().replace("-", "_")
            value = value.strip()
            if not value:
                attrs.append(f"{name}=True")
            else:
                if value.startswith(ATTR_START) and value.endswith(ATTR_END):
                    value = value[1:-1].strip()
                attrs.append(f"{name}={value}")

        str_attrs = ", ".join(attrs)
        if str_attrs:
            str_attrs = f", {str_attrs}"

        if not content:
            call = INLINE_CALL.replace("[TAG]", tag).replace("[ATTRS]", str_attrs)
        else:
            call = (
                BLOCK_CALL.replace("[TAG]", tag)
                .replace("[ATTRS]", str_attrs)
                .replace("[CONTENT]", content)
            )
        return call
