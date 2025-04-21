"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""

class ComponentNotFound(Exception):
    """
    Raised when JinjaX can't find a component by name in none of the
    added folders, probably because of a typo.
    """

    def __init__(self, name: str, file_ext: str) -> None:
        msg = f"Unable to find component `{name}` with file extension `*{file_ext}`"
        super().__init__(msg)


class MissingRequiredArgument(Exception):
    """
    Raised when a component is used/invoked without passing one or more
    of its required arguments (those without a default value).
    """

    def __init__(self, component: str, arg: str) -> None:
        msg = f"`{component}` component requires a `{arg}` argument"
        super().__init__(msg)


class DuplicateDefDeclaration(Exception):
    """
    Raised when a component has more then one `{#def ... #}` declarations.
    """

    def __init__(self, component: str) -> None:
        msg = "`" + str(component) + "` has two `{#def ... #}` declarations"
        super().__init__(msg)


class InvalidArgument(Exception):
    """
    Raised when the arguments passed to the component cannot be parsed
    by JinjaX because of an invalid syntax.
    """


class UnknownPrefix(Exception):
    """
    Raised when a component is used/invoked with a prefix that is
    not registered.
    """

    def __init__(self, name: str) -> None:
        msg = f"The prefix `{name}` is not registered"
        super().__init__(msg)
