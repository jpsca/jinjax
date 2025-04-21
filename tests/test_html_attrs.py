"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
import pytest

from jinjax.html_attrs import HTMLAttrs


def test_parse_initial_attrs():
    attrs = HTMLAttrs(
        {
            "title": "hi",
            "data-position": "top",
            "class": "z4 c3 a1 z4 b2",
            "open": True,
            "disabled": False,
            "value": 0,
            "foobar": None,
        }
    )
    assert attrs.classes == "a1 b2 c3 z4"
    assert attrs.get("class") == "a1 b2 c3 z4"
    assert attrs.get("data-position") == "top"
    assert attrs.get("data_position") == "top"
    assert attrs.get("title") == "hi"
    assert attrs.get("open") is True
    assert attrs.get("disabled", "meh") == "meh"
    assert attrs.get("value") == "0"

    assert attrs.get("disabled") is None
    assert attrs.get("foobar") is None

    attrs.set(data_value=0)
    attrs.set(data_position=False)
    assert attrs.get("data-value") == 0
    assert attrs.get("data-position") is None
    assert attrs.get("data_position") is None

def test_getattr():
    attrs = HTMLAttrs(
        {
            "title": "hi",
            "class": "z4 c3 a1 z4 b2",
            "open": True,
        }
    )
    assert attrs["class"] == "a1 b2 c3 z4"
    assert attrs["title"] == "hi"
    assert attrs["open"] is True
    assert attrs["lorem"] is None


def test_deltattr():
    attrs = HTMLAttrs(
        {
            "title": "hi",
            "class": "z4 c3 a1 z4 b2",
            "open": True,
        }
    )
    assert attrs["class"] == "a1 b2 c3 z4"
    del attrs["title"]
    assert attrs["title"] is None


def test_render():
    attrs = HTMLAttrs(
        {
            "title": "hi",
            "data-position": "top",
            "class": "z4 c3 a1 z4 b2",
            "open": True,
            "disabled": False,
        }
    )
    assert 'class="a1 b2 c3 z4" data-position="top" title="hi" open' == attrs.render()


def test_set():
    attrs = HTMLAttrs({})
    attrs.set(title="hi", data_position="top")
    attrs.set(open=True)
    assert 'data-position="top" title="hi" open' == attrs.render()

    attrs.set(title=False, open=False)
    assert 'data-position="top"' == attrs.render()


def test_class_management():
    attrs = HTMLAttrs(
        {
            "class": "z4 c3 a1 z4 b2",
        }
    )
    attrs.set(classes="lorem bipsum lorem a1")

    assert attrs.classes == "a1 b2 bipsum c3 lorem z4"

    attrs.remove_class("bipsum")
    assert attrs.classes == "a1 b2 c3 lorem z4"

    attrs.set(classes=None)
    attrs.set(classes="meh")
    assert attrs.classes == "meh"


def test_setdefault():
    attrs = HTMLAttrs(
        {
            "title": "hi",
        }
    )
    attrs.setdefault(
        title="default title",
        data_lorem="ipsum",
        open=True,
        disabled=False,
    )
    assert 'data-lorem="ipsum" title="hi"' == attrs.render()


def test_as_dict():
    attrs = HTMLAttrs(
        {
            "title": "hi",
            "data-position": "top",
            "class": "z4 c3 a1 z4 b2",
            "open": True,
            "disabled": False,
        }
    )
    assert attrs.as_dict == {
        "class": "a1 b2 c3 z4",
        "data-position": "top",
        "title": "hi",
        "open": True,
    }


def test_as_dict_no_classes():
    attrs = HTMLAttrs(
        {
            "title": "hi",
            "data-position": "top",
            "open": True,
        }
    )
    assert attrs.as_dict == {
        "data-position": "top",
        "title": "hi",
        "open": True,
    }


def test_render_attrs_lik_set():
    attrs = HTMLAttrs({"class": "lorem"})
    expected = 'class="ipsum lorem" data-position="top" title="hi" open'
    result = attrs.render(
        title="hi",
        data_position="top",
        classes="ipsum",
        open=True,
    )
    print(result)
    assert expected == result


def test_do_not_escape_tailwind_syntax():
    attrs = HTMLAttrs({"class": "lorem [&_a]:flex"})
    expected = 'class="[&_a]:flex ipsum lorem" title="Hi&Stuff"'
    result = attrs.render(
        **{
            "title": "Hi&Stuff",
            "class": "ipsum",
        }
    )
    print(result)
    assert expected == result


def test_do_escape_quotes_inside_attrs():
    attrs = HTMLAttrs(
        {
            "class": "lorem text-['red']",
            "title": 'I say "hey"',
            "open": True,
        }
    )
    expected = """class="lorem text-['red']" title='I say "hey"' open"""
    result = attrs.render()
    print(result)
    assert expected == result


def test_additional_attributes_are_lazily_evaluated_to_strings():
    class TestObject:
        def __str__(self):
            raise RuntimeError("Should not be called unless rendered.")

    attrs = HTMLAttrs(
        {
            "some_object": TestObject(),
        }
    )

    with pytest.raises(RuntimeError):
        attrs.render()


def test_additional_attributes_lazily_evaluated_has_string_methods():
    class TestObject:
        def __str__(self):
            return "test"

    attrs = HTMLAttrs({"some_object": TestObject()})

    assert attrs["some_object"].__str__
    assert attrs["some_object"].__repr__
    assert attrs["some_object"].__int__
    assert attrs["some_object"].__float__
    assert attrs["some_object"].__complex__
    assert attrs["some_object"].__hash__
    assert attrs["some_object"].__eq__
    assert attrs["some_object"].__lt__
    assert attrs["some_object"].__le__
    assert attrs["some_object"].__gt__
    assert attrs["some_object"].__ge__
    assert attrs["some_object"].__contains__
    assert attrs["some_object"].__len__
    assert attrs["some_object"].__getitem__
    assert attrs["some_object"].__add__
    assert attrs["some_object"].__radd__
    assert attrs["some_object"].__mul__
    assert attrs["some_object"].__mod__
    assert attrs["some_object"].__rmod__
    assert attrs["some_object"].capitalize
    assert attrs["some_object"].casefold
    assert attrs["some_object"].center
    assert attrs["some_object"].count
    assert attrs["some_object"].removeprefix
    assert attrs["some_object"].removesuffix
    assert attrs["some_object"].encode
    assert attrs["some_object"].endswith
    assert attrs["some_object"].expandtabs
    assert attrs["some_object"].find
    assert attrs["some_object"].format
    assert attrs["some_object"].format_map
    assert attrs["some_object"].index
    assert attrs["some_object"].isalpha
    assert attrs["some_object"].isalnum
    assert attrs["some_object"].isascii
    assert attrs["some_object"].isdecimal
    assert attrs["some_object"].isdigit
    assert attrs["some_object"].isidentifier
    assert attrs["some_object"].islower
    assert attrs["some_object"].isnumeric
    assert attrs["some_object"].isprintable
    assert attrs["some_object"].isspace
    assert attrs["some_object"].istitle
    assert attrs["some_object"].isupper
    assert attrs["some_object"].join
    assert attrs["some_object"].ljust
    assert attrs["some_object"].lower
    assert attrs["some_object"].lstrip
    assert attrs["some_object"].partition
    assert attrs["some_object"].replace
    assert attrs["some_object"].rfind
    assert attrs["some_object"].rindex
    assert attrs["some_object"].rjust
    assert attrs["some_object"].rpartition
    assert attrs["some_object"].rstrip
    assert attrs["some_object"].split
    assert attrs["some_object"].rsplit
    assert attrs["some_object"].splitlines
    assert attrs["some_object"].startswith
    assert attrs["some_object"].strip
    assert attrs["some_object"].swapcase
    assert attrs["some_object"].title
    assert attrs["some_object"].translate
    assert attrs["some_object"].upper
    assert attrs["some_object"].zfill

    assert attrs["some_object"].upper() == "TEST"
    assert attrs["some_object"].title() == "Test"
