import re
import typing as t

from jinja2.ext import Extension
from jinja2.exceptions import TemplateSyntaxError

from .utils import logger


RENDER_CMD = "catalog.render"
BLOCK_CALL = '{% call <CMD>("<TAG>"<ATTRS>) -%}\n<CONTENT>\n{%- endcall %}'
BLOCK_CALL = BLOCK_CALL.replace("<CMD>", RENDER_CMD)
INLINE_CALL = '{{ <CMD>("<TAG>"<ATTRS>) }}'
INLINE_CALL = INLINE_CALL.replace("<CMD>", RENDER_CMD)
ATTR_START = "{"
ATTR_END = "}"

re_raw = r"\{%-?\s*raw\s*-?%\}.+\{%-?\s*endraw\s*-?%\}"
RX_RAW = re.compile(re_raw, re.VERBOSE | re.DOTALL)

re_tag_name = r"([0-9A-Za-z_-]+\.)*[A-Z][0-9A-Za-z_-]*"
re_raw_attrs = r"(?P<attrs>[^\>]*)"
re_content = r"(?P<content>.*)"
re_tag = rf"<(?P<tag>{re_tag_name}){re_raw_attrs}(/>|>{re_content}</{re_tag_name}>)"
RX_TAG = re.compile(re_tag, re.VERBOSE | re.DOTALL)

re_uncloded = rf"<(?P<tag>{re_tag_name}){re_raw_attrs}>"
RX_UNCLOSED = re.compile(re_uncloded, re.VERBOSE | re.DOTALL)

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

MSG_UNCLOSED_TAG = "Unclosed component {TAG}"

TRawRanges = list[tuple[int, int]]


class JinjaX(Extension):
    def preprocess(
        self,
        source: str,
        name: t.Optional[str] = None,
        filename: t.Optional[str] = None,
    ) -> str:
        raw_ranges = self._get_raw_ranges(source)
        pos = 0
        while True:
            match = RX_TAG.search(source, pos=pos)
            if not match:
                break
            tag_start = match.start(0)
            for start, end in raw_ranges:
                if start <= tag_start <= end:
                    pos = end
                    break
            else:
                source = RX_TAG.sub(self._process_tag, source)

        self._check_for_unclosed(source, raw_ranges, name, filename)
        return source

    def _get_raw_ranges(self, source: str) -> TRawRanges:
        return [m.span(0) for m in RX_RAW.finditer(source) if m]

    def _process_tag(self, match: re.Match) -> str:
        tag = match.group("tag")
        attrs = (match.group("attrs") or "").strip()
        content = (match.group("content") or "").strip()
        logger.debug(f"<{tag}> {attrs} {'inline' if not content else ''}")
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
        logger.debug(f"<{tag}> {attrs_list} {'inline' if not content else ''}")
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
            call = INLINE_CALL.replace("<TAG>", tag).replace("<ATTRS>", str_attrs)
        else:
            call = (
                BLOCK_CALL.replace("<TAG>", tag)
                .replace("<ATTRS>", str_attrs)
                .replace("<CONTENT>", content)
            )

        logger.debug(f"-> {call}")
        return call

    def _check_for_unclosed(
        self,
        source: str,
        raw_ranges: TRawRanges,
        name: t.Optional[str] = None,
        filename: t.Optional[str] = None,
    ) -> None:
        pos = 0
        while True:
            match = RX_UNCLOSED.search(source, pos=pos)
            if not match:
                break
            tag_start = match.start(0)
            for start, end in raw_ranges:
                if start <= tag_start <= end:
                    pos = end
                    break
            else:
                raise TemplateSyntaxError(
                    message=MSG_UNCLOSED_TAG.format(TAG=match.group(0)),
                    lineno=source[:tag_start].count("\n") + 1,
                    name=name,
                    filename=filename
                )
