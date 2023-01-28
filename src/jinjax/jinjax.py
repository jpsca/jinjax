import re
import typing as t
from uuid import uuid4

from jinja2.ext import Extension
from jinja2.exceptions import TemplateSyntaxError

from .utils import logger


RENDER_CMD = "catalog.render"
BLOCK_CALL = '{% call [CMD]("[TAG]"[ATTRS]) -%}\n[CONTENT]\n{%- endcall %}'
BLOCK_CALL = BLOCK_CALL.replace("[CMD]", RENDER_CMD)
INLINE_CALL = '{{ [CMD]("[TAG]"[ATTRS]) }}'
INLINE_CALL = INLINE_CALL.replace("[CMD]", RENDER_CMD)
ATTR_START = "{"
ATTR_END = "}"

re_raw = r"\{%-?\s*raw\s*-?%\}.+?\{%-?\s*endraw\s*-?%\}"
RX_RAW = re.compile(re_raw, re.DOTALL)

re_tag_name = r"([0-9A-Za-z_-]+\.)*[A-Z][0-9A-Za-z_-]*"
re_raw_attrs = r"(?P<attrs>[^\>]*)"
re_content = r"(?P<content>.*?)"
re_tag = rf"<(?P<tag>{re_tag_name}){re_raw_attrs}(/>|>{re_content}</{re_tag_name}>)"
RX_TAG = re.compile(re_tag, re.DOTALL)

re_uncloded = rf"<(?P<tag>{re_tag_name}){re_raw_attrs}>"
RX_UNCLOSED = re.compile(re_uncloded, re.DOTALL)

re_attr_name = r"(?P<name>[a-zA-Z_][0-9a-zA-Z_-]*)"
re_equal = r"\s*=\s*"
re_attr = rf"""
{re_attr_name}
(?:
    {re_equal}
    (?P<value>".*?"|'.*?'|\{ATTR_START}.*?\{ATTR_END})
)?
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
        source = self._replace_raw_blocks(source)
        source = self._process_tags(source)
        self._check_for_unclosed(source, name, filename)
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
            start, end = match.span(0)
            repl = self._process_tag(match)
            source = f"{source[:start]}{repl}{source[end:]}"

        return source

    def _process_tag(self, match: re.Match) -> str:
        tag = match.group("tag")
        attrs = (match.group("attrs") or "").strip()
        content = (match.group("content") or "").strip()
        logger.debug(f"{tag} {attrs} {'inline' if not content else ''}")
        attrs_list = self._parse_attrs(attrs)
        return self._build_call(tag, attrs_list, content)

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
            if not value:
                attrs.append(f"{name}=True")
            else:
                attrs.append(f"{name}={value.strip(' {}')}")

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

    def _check_for_unclosed(
        self,
        source: str,
        name: t.Optional[str] = None,
        filename: t.Optional[str] = None,
    ) -> None:
        match = RX_UNCLOSED.search(source)
        if match:
            raise TemplateSyntaxError(
                message=f"Unclosed component {match.group(0)}",
                lineno=source[:match.start(0)].count("\n") + 1,
                name=name,
                filename=filename
            )
