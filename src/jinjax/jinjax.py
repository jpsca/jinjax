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
                if key in self.__dict__:
                    return self[key]
                if key.endswith("end"):
                    raise KeyError
                return lambda parser: ext._parse_component(parser, key)

        def _parse(source: str, name: str | None, filename: str | None) -> nodes.Template:
            """Overwrited internal parsing function used by `parse` and `compile`."""
            parser = Parser(environment, source, name, filename)
            parser.extensions = Extensions(parser.extensions)
            return parser.parse()

        environment._parse = _parse

    def _parse_component(self, parser: Parser, name: str) -> "Node":
        # the first token is the token that started the tag.
        # We get the line number so that we can give
        # that line number to the nodes we create by hand.
        lineno = next(parser.stream).lineno

        args, kwargs, has_content = self._parse_args(parser)
        args.insert(0, nodes.Const(name))

        if has_content:
            body = parser.parse_statements((f"name:end{name}", ), drop_needle=True)
        else:
            body = ""

        call_method = self.call_method("_render_component", args, kwargs)
        return nodes.CallBlock(call_method, [], [], body).set_lineno(lineno)

    def _parse_args(self, parser: Parser) -> tuple[list, list, bool]:
        args = []
        kwargs = []
        require_comma = False
        has_content = True

        while parser.stream.current.type != 'block_end':
            if parser.stream.current.test("name:end"):
                if parser.stream.look().type == 'block_end':
                    has_content = False
                    parser.stream.skip(1)
                    break
                else:
                    parser.fail("Invalid argument syntax", parser.stream.current.lineno)

            if require_comma:
                parser.stream.expect('comma')

                # support for trailing comma
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
                if kwargs:
                    parser.fail("Invalid argument syntax", parser.stream.current.lineno)
                args.append(parser.parse_expression())

            require_comma = True

        return args, kwargs, has_content

    def _render_component(self, __name: str, **kwargs) -> "Markup":
        return self.environment.catalog.render(__name, **kwargs)  # type: ignore
