class ComponentNotFound(Exception):
    def __init__(self, name: str) -> None:
        msg = f"File with pattern `{name}` not found"
        super().__init__(msg)


class MissingRequiredArgument(Exception):
    def __init__(self, component: str, arg: str) -> None:
        msg = f"`{component}` component requires a `{arg}` argument"
        super().__init__(msg)


class InvalidArgument(Exception):
    pass
