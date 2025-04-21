"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
import re
import typing as t
from collections import UserString
from functools import cached_property

from markupsafe import Markup


CLASS_KEY = "class"
CLASS_ALT_KEY = "classes"
CLASS_KEYS = (CLASS_KEY, CLASS_ALT_KEY)


def split(ssl: str) -> list[str]:
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
    """
    Behave like regular strings, but the actual casting of the initial value
    is deferred until the value is actually required.
    """

    __slots__ = ("_seq",)

    def __init__(self, seq):
        self._seq = seq

    @cached_property
    def data(self):  # type: ignore
        return str(self._seq)


class HTMLAttrs:
    """
    Contains all the HTML attributes/properties (a property is an
    attribute without a value) passed to a component but that weren't
    in the declared attributes list.

    For HTML classes you can use the name "classes" (instead of "class")
    if you need to.

    **NOTE**: The string values passed to this class, are not cast to `str` until
    the string representation is actually needed, for example when
    `attrs.render()` is invoked.

    """

    def __init__(self, attrs: "dict[str, t.Any| LazyString]") -> None:
        attributes: "dict[str, str | LazyString]" = {}
        properties: set[str] = set()

        class_names = split(" ".join([
            str(attrs.pop(CLASS_KEY, "")),
            str(attrs.get(CLASS_ALT_KEY, "")),
        ]))
        self.__classes = {name for name in class_names if name}

        for name, value in attrs.items():
            if name.startswith("__"):
                continue
            name = name.replace("_", "-")
            if value is True:
                properties.add(name)
            elif value is not False and value is not None:
                attributes[name] = LazyString(value)

        self.__attributes = attributes
        self.__properties = properties

    @property
    def classes(self) -> str:
        """
        All the HTML classes alphabetically sorted and separated by a space.

        Example:

            ```python
            attrs = HTMLAttrs({"class": "italic bold bg-blue wide abcde"})
            attrs.set(class="bold text-white")
            print(attrs.classes)
            abcde bg-blue bold italic text-white wide
            ```

        """
        return " ".join(sorted((self.__classes)))

    @property
    def as_dict(self) -> dict[str, t.Any]:
        """
        An ordered dict of all the attributes and properties, both
        sorted by name before join.

        Example:

            ```python
            attrs = HTMLAttrs({
            "class": "lorem ipsum",
            "data_test": True,
            "hidden": True,
            "aria_label": "hello",
            "id": "world",
            })
            attrs.as_dict
            {
                "aria_label": "hello",
                "class": "ipsum lorem",
                "id": "world",
                "data_test": True,
                "hidden": True
            }
            ```

        """
        attributes = self.__attributes.copy()
        classes = self.classes
        if classes:
            attributes[CLASS_KEY] = classes

        out: dict[str, t.Any] = dict(sorted(attributes.items()))
        for name in sorted((self.__properties)):
            out[name] = True
        return out

    def __getitem__(self, name: str) -> t.Any:
        return self.get(name)

    def __delitem__(self, name: str) -> None:
        self._remove(name)

    def __str__(self) -> str:
        return str(self.as_dict)

    def set(self, **kw) -> None:
        """
        Sets an attribute or property

        - Pass a name and a value to set an attribute (e.g. `type="text"`)
        - Use `True` as a value to set a property (e.g. `disabled`)
        - Use `False` to remove an attribute or property
        - If the attribute is "class", the new classes are appended to
          the old ones (if not repeated) instead of replacing them.
        - The underscores in the names will be translated automatically to dashes,
          so `aria_selected` becomes the attribute `aria-selected`.

        Example:

            ```python
            attrs = HTMLAttrs({"secret": "qwertyuiop"})
            attrs.set(secret=False)
            attrs.as_dict
            {}

            attrs.set(unknown=False, lorem="ipsum", count=42, data_good=True)
            attrs.as_dict
            {"count":42, "lorem":"ipsum", "data_good": True}

            attrs = HTMLAttrs({"class": "b c a"})
            attrs.set(class="c b f d e")
            attrs.as_dict
            {"class": "a b c d e f"}
            ```

        """
        for name, value in kw.items():
            name = name.replace("_", "-")
            if value is False or value is None:
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
        Adds an attribute, but only if it's not already present.

        The underscores in the names will be translated automatically to dashes,
        so `aria_selected` becomes the attribute `aria-selected`.

        Example:

            ```python
            attrs = HTMLAttrs({"lorem": "ipsum"})
            attrs.setdefault(tabindex=0, lorem="meh")
            attrs.as_dict
            # "tabindex" changed but "lorem" didn't
            {"lorem": "ipsum", tabindex: 0}
            ```

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
        """
        Adds one or more classes to the list of classes, if not already present.

        Example:

            ```python
            attrs = HTMLAttrs({"class": "a b c"})
            attrs.add_class("c", "d")
            attrs.as_dict
            {"class": "a b c d"}
            ```

        """
        for names in values:
            for name in split(names):
                self.__classes.add(name)

    def remove_class(self, *names: str) -> None:
        """
        Removes one or more classes from the list of classes.

        Example:

            ```python
            attrs = HTMLAttrs({"class": "a b c"})
            attrs.remove_class("c", "d")
            attrs.as_dict
            {"class": "a b"}
            ```

        """
        for name in names:
            self.__classes.remove(name)

    def get(self, name: str, default: t.Any = None) -> t.Any:
        """
        Returns the value of the attribute or property,
        or the default value if it doesn't exists.

        Example:

            ```python
            attrs = HTMLAttrs({"lorem": "ipsum", "hidden": True})

            attrs.get("lorem", defaut="bar")
            'ipsum'

            attrs.get("foo")
            None

            attrs.get("foo", defaut="bar")
            'bar'

            attrs.get("hidden")
            True
            ```

        """
        name = name.replace("_", "-")
        if name in CLASS_KEYS:
            return self.classes
        if name in self.__attributes:
            return self.__attributes[name]
        if name in self.__properties:
            return True
        return default

    def render(self, **kw) -> str:
        """
        Renders the attributes and properties as a string.

        Any arguments you use with this function are merged with the existing
        attibutes/properties by the same rules as the `HTMLAttrs.set()` function:

        - Pass a name and a value to set an attribute (e.g. `type="text"`)
        - Use `True` as a value to set a property (e.g. `disabled`)
        - Use `False` to remove an attribute or property
        - If the attribute is "class", the new classes are appended to
          the old ones (if not repeated) instead of replacing them.
        - The underscores in the names will be translated automatically to dashes,
          so `aria_selected` becomes the attribute `aria-selected`.

        To provide consistent output, the attributes and properties
        are sorted by name and rendered like this:
        `<sorted attributes> + <sorted properties>`.

        Example:

            ```python
            attrs = HTMLAttrs({"class": "ipsum", "data_good": True, "width": 42})

            attrs.render()
            'class="ipsum" width="42" data-good'

            attrs.render(class="abc", data_good=False, tabindex=0)
            'class="abc ipsum" width="42" tabindex="0"'
            ```

        """
        if kw:
            self.set(**kw)

        attributes = self.__attributes.copy()

        classes = self.classes
        if classes:
            attributes[CLASS_KEY] = classes

        attributes = dict(sorted(attributes.items()))
        properties = sorted((self.__properties))

        html_attrs = [
            f"{name}={quote(str(value))}"
            for name, value in attributes.items()
        ]
        html_attrs.extend(properties)

        return Markup(" ".join(html_attrs))

    # Private

    def _remove(self, name: str) -> None:
        """
        Removes an attribute or property.
        """
        if name in CLASS_KEYS:
            self.__classes = set()
        if name in self.__attributes:
            del self.__attributes[name]
        if name in self.__properties:
            self.__properties.remove(name)
