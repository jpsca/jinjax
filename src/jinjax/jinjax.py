import typing as t

from jinja2 import Environment, nodes
from jinja2.ext import Extension
from jinja2.parser import Parser

if t.TYPE_CHECKING:
    from jinja2.nodes import Node
    from markupsafe import Markup


class JinjaX(Extension):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        ext = self

        class Extensions(dict):
            def get(self, key):
                return super().get(key, ext._parse_component)

        def _parse(source: str, name: str | None, filename: str | None) -> nodes.Template:
            """Overwrited internal parsing function used by `parse` and `compile`."""
            parser = Parser(environment, source, name, filename)
            parser.extensions = Extensions(parser.extensions)
            return parser.parse()

        environment._parse = _parse

    def _parse_component(self, parser: Parser) -> "Node":
        # the first token is the token that started the tag.
        # We get the line number so that we can give
        # that line number to the nodes we create by hand.
        lineno = parser.stream.current.lineno
        tag_name = parser.stream.current.value
        parser.stream.skip(1)

        args, kwargs, has_content = self._parse_args(parser)
        args.insert(0, nodes.Const(tag_name))

        if has_content:
            body = parser.parse_statements((f"name:end{tag_name}", ), drop_needle=True)
            call_node = self.call_method("_render_component", args, kwargs)
            return nodes.CallBlock(call_node, [], [], body).set_lineno(lineno)
        else:
            call_node = self.call_method("_render_component", args, kwargs)
            call = nodes.MarkSafe(call_node, lineno=lineno)
            return nodes.Output([call], lineno=lineno)

    def _parse_args(self, parser: Parser) -> tuple[list, list, bool]:
        args = []
        kwargs = []
        require_comma = False
        has_content = True

        while parser.stream.current.type != 'block_end':
            if require_comma and not parser.stream.current.test("name:end"):
                parser.stream.expect('comma')
                if parser.stream.current.type == 'block_end':
                    break

            if (
                parser.stream.current.type == 'name'
                and parser.stream.look().type == 'assign'
            ):
                key = parser.stream.current.value
                parser.stream.skip(2)
                value = parser.parse_expression()
                kwargs.append(nodes.Keyword(key, value, lineno=value.lineno))
            else:
                if parser.stream.current.test("name:end"):
                    if parser.stream.look().type == 'block_end':
                        has_content = False
                        parser.stream.skip(1)
                        break
                    else:
                        parser.fail("Invalid argument syntax", parser.stream.current.lineno)

                if kwargs:
                    parser.fail("Invalid argument syntax", parser.stream.current.lineno)
                args.append(parser.parse_expression())

            require_comma = True

        return args, kwargs, has_content

    def _render_component(self, __name: str, *args, **kwargs) -> "Markup":
        return self.environment.catalog.render(__name, *args, **kwargs)  # type: ignore
