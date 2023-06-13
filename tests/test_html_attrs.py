import pytest
from jinjax.html_attrs import HTMLAttrs


def test_parse_initial_attrs():
    attrs = HTMLAttrs({
        "title": "hi",
        "data-position": "top",
        "class": "z4 c3 a1 z4 b2",
        "open": True,
        "disabled": False,
    })
    assert attrs.classes == "a1 b2 c3 z4"
    assert attrs.get("class") == "a1 b2 c3 z4"
    assert attrs.get("data-position") == "top"
    assert attrs.get("data_position") == "top"
    assert attrs.get("title") == "hi"
    assert attrs.get("open") is True
    assert attrs.get("disabled", "meh") == "meh"


def test_getattr():
    attrs = HTMLAttrs({
        "title": "hi",
        "class": "z4 c3 a1 z4 b2",
        "open": True,
    })
    assert attrs["class"] == "a1 b2 c3 z4"
    assert attrs["title"] == "hi"
    assert attrs["open"] is True
    assert attrs["lorem"] is None


def test_deltattr():
    attrs = HTMLAttrs({
        "title": "hi",
        "class": "z4 c3 a1 z4 b2",
        "open": True,
    })
    assert attrs["class"] == "a1 b2 c3 z4"
    del attrs["title"]
    assert attrs["title"] is None


def test_render():
    attrs = HTMLAttrs({
        "title": "hi",
        "data-position": "top",
        "class": "z4 c3 a1 z4 b2",
        "open": True,
        "disabled": False,
    })
    assert 'class="a1 b2 c3 z4" data-position="top" title="hi" open' == attrs.render()


def test_set():
    attrs = HTMLAttrs({})
    attrs.set(title="hi", data_position="top")
    attrs.set(open=True)
    assert 'data-position="top" title="hi" open' == attrs.render()

    attrs.set(title=False, open=False)
    assert 'data-position="top"' == attrs.render()


def test_class_management():
    attrs = HTMLAttrs({
        "class": "z4 c3 a1 z4 b2",
    })
    attrs.set(classes="lorem bipsum lorem a1")

    assert attrs.classes == "a1 b2 bipsum c3 lorem z4"

    attrs.remove_class("bipsum")
    assert attrs.classes == "a1 b2 c3 lorem z4"

    attrs.set(classes=None)
    attrs.set(classes="meh")
    assert attrs.classes == "meh"


def test_setdefault():
    attrs = HTMLAttrs({
        "title": "hi",
    })
    attrs.setdefault(
        title="default title",
        data_lorem="ipsum",
        open=True,
        disabled=False,
    )
    assert 'data-lorem="ipsum" title="hi"' == attrs.render()


def test_as_dict():
    attrs = HTMLAttrs({
        "title": "hi",
        "data-position": "top",
        "class": "z4 c3 a1 z4 b2",
        "open": True,
        "disabled": False,
    })
    assert attrs.as_dict == {
        "class": "a1 b2 c3 z4",
        "data-position": "top",
        "title": "hi",
        "open": True,
    }


def test_as_dict_no_classes():
    attrs = HTMLAttrs({
        "title": "hi",
        "data-position": "top",
        "open": True,
    })
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
    result = attrs.render(**{
        "title": "Hi&Stuff",
        "class": "ipsum",
    })
    print(result)
    assert expected == result


def test_do_escape_quotes_inside_attrs():
    attrs = HTMLAttrs({
        "class": "lorem text-['red']",
        "title": 'I say "hey"',
        "open": True,
    })
    expected = """class="lorem text-['red']" title='I say "hey"' open"""
    result = attrs.render()
    print(result)
    assert expected == result


def test_additional_attributes_are_lazily_evaluated_to_strings():
    class TestObject:
        def __str__(self):
            raise RuntimeError("Should not be called unless rendered.")

    attrs = HTMLAttrs({
        "some_object": TestObject(),
    })

    with pytest.raises(RuntimeError):
        attrs.render()
