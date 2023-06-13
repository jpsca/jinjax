import re
from collections import UserString
from functools import cached_property
from typing import Any


CLASS_KEY = "class"
CLASS_ALT_KEY = "classes"
CLASS_KEYS = (CLASS_KEY, CLASS_ALT_KEY)


def split(ssl: str) -> "list[str]":
    return re.split(r"\s+", ssl.strip())


def quote(text: str) -> str:
    if '"' in text:
        if "'" in text:
            text = text.replace('"', "&quot;")
            return f'"{text}"'
        else:
            return f"'{text}'"

    return f'"{text}"'


class LazyString(UserString):
    """Behave like regular strings, but the actual casting of the initial value
    is deferred until the value is actually required."""

    __slots__ = ("_seq",)

    def __init__(self, seq):
        self._seq = seq

    @cached_property
    def data(self):
        return str(self._seq)


class HTMLAttrs:
    def __init__(self, attrs) -> None:
        attributes: "dict[str, str|LazyString]" = {}
        properties: "set[str]" = set()

        class_names = split(" ".join([
            attrs.pop(CLASS_KEY, ""),
            attrs.get(CLASS_ALT_KEY, ""),
        ]))
        self.__classes = {name for name in class_names if name}

        for name, value in attrs.items():
            name = name.replace("_", "-")
            if value is True:
                properties.add(name)
            elif value not in (False, None):
                attributes[name] = LazyString(value)

        self.__attributes = attributes
        self.__properties = properties

    @property
    def classes(self) -> str:
        return " ".join(sorted(list(self.__classes)))

    @property
    def as_dict(self) -> dict[str, Any]:
        attributes = self.__attributes.copy()
        classes = self.classes
        if classes:
            attributes[CLASS_KEY] = classes

        out: dict[str, Any] = dict(sorted(attributes.items()))
        for name in sorted(list(self.__properties)):
            out[name] = True
        return out

    def __getitem__(self, name: str) -> Any:
        return self.get(name)

    def __delitem__(self, name: str) -> None:
        self._remove(name)

    def set(self, **kw) -> None:
        """
        Sets an attribute or property:
        - Pass a name and a value to set an attribute
        - Use `True` as value to set a property
        - Use `False` to remove an attribute or property

        If the attribute is "class", the new classes are appended to
        the old ones instead of replacing them.
        """
        for name, value in kw.items():
            name = name.replace("_", "-")
            if value in (False, None):
                self._remove(name)
                continue

            if name in CLASS_KEYS:
                self.add_class(value)
            elif value is True:
                self.__properties.add(name)
            else:
                self.__attributes[name] = value

    def setdefault(self, **kw) -> None:
        """
        Adds an attribute or sets a property, but only if it's not
        already present. Doesn't work with properties.
        """
        for name, value in kw.items():
            if value in (True, False, None):
                continue

            if name in CLASS_KEYS:
                if not self.__classes:
                    self.add_class(value)

            name = name.replace("_", "-")
            if name not in self.__attributes:
                self.set(**{name: value})

    def add_class(self, *values: str) -> None:
        for names in values:
            for name in split(names):
                self.__classes.add(name)

    def remove_class(self, *names: str) -> None:
        for name in names:
            self.__classes.remove(name)

    def get(self, name: str, default: Any = None) -> Any:
        """
        Returns the value of the attribute or property,
        or the default value if it doesn't exists."""
        name = name.replace("_", "-")
        if name in CLASS_KEYS:
            return self.classes
        if name in self.__attributes:
            return self.__attributes[name]
        if name in self.__properties:
            return True
        return default

    def _remove(self, name: str) -> None:
        """
        Removes an attribute or property."""
        if name in CLASS_KEYS:
            self.__classes = set()
        if name in self.__attributes:
            del self.__attributes[name]
        if name in self.__properties:
            self.__properties.remove(name)

    def render(self, **kw) -> str:
        """
        Renders the attributes and properties as a string.
        To provide consistent output, the attributes and properties
        are sorted by name and rendered like this:
        `<sorted attributes> + <sorted properties>`.
        """
        if kw:
            self.set(**kw)

        attributes = self.__attributes.copy()

        classes = self.classes
        if classes:
            attributes[CLASS_KEY] = classes

        attributes = dict(sorted(attributes.items()))
        properties = sorted(list(self.__properties))

        html_attrs = [
            f"{name}={quote(str(value))}"
            for name, value in attributes.items()
        ]
        html_attrs.extend(properties)

        return " ".join(html_attrs)
