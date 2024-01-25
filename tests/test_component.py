import pytest

from jinjax import Component, InvalidArgument


def test_load_args():
    com = Component(
        name="Test.jinja",
        source='{#def message, lorem=4, ipsum="bar" -#}\n',
    )
    assert com.required == ["message"]
    assert com.optional == {
        "lorem": 4,
        "ipsum": "bar",
    }


def test_expression_args():
    com = Component(
        name="Test.jinja",
        source="{#def expr=1 + 2 + 3, a=1 -#}\n",
    )
    assert com.required == []
    assert com.optional == {
        "expr": 6,
        "a": 1,
    }


def test_dict_args():
    com = Component(
        name="Test.jinja",
        source="{#def expr={'a': 'b', 'c': 'd'} -#}\n",
    )
    assert com.optional == {
        "expr": {"a": "b", "c": "d"},
    }

    com = Component(
        name="Test.jinja",
        source='{#def a=1, expr={"a": "b", "c": "d"} -#}\n',
    )
    assert com.optional == {
        "a": 1,
        "expr": {"a": "b", "c": "d"},
    }


def test_lowercase_booleans():
    com = Component(
        name="Test.jinja",
        source="{#def a=false, b=true -#}\n",
    )
    assert com.optional == {
        "a": False,
        "b": True,
    }


def test_no_args():
    com = Component(
        name="Test.jinja",
        source="\n",
    )
    assert com.required == []
    assert com.optional == {}


def test_fails_when_invalid_name():
    with pytest.raises(InvalidArgument):
        source = "{#def 000abc -#}\n"
        co = Component(name="", source=source)
        print(co.required, co.optional)


def test_fails_when_missing_comma_between_args():
    with pytest.raises(InvalidArgument):
        source = "{#def lorem ipsum -#}\n"
        co = Component(name="", source=source)
        print(co.required, co.optional)


def test_fails_when_missing_quotes_arround_default_value():
    with pytest.raises(InvalidArgument):
        source = "{#def lorem=ipsum -#}\n"
        co = Component(name="", source=source)
        print(co.required, co.optional)


def test_fails_when_prop_is_expression():
    with pytest.raises(InvalidArgument):
        source = "{#def a-b -#}\n"
        co = Component(name="", source=source)
        print(co.required, co.optional)


def test_fails_when_extra_comma_between_args():
    with pytest.raises(InvalidArgument):
        source = "{#def a, , b -#}\n"
        co = Component(name="", source=source)
        print(co.required, co.optional)


def test_comma_in_default_value():
    com = Component(
        name="Test.jinja",
        source="{#def a='lorem, ipsum' -#}\n",
    )
    assert com.optional == {"a": "lorem, ipsum"}


def test_load_assets():
    com = Component(
        name="Test.jinja",
        url_prefix="/static/",
        source="""
        {#css a.css, "b.css", c.css -#}
        {#js a.js, b.js, c.js -#}
        """,
    )
    assert com.css == ["/static/a.css", "/static/b.css", "/static/c.css"]
    assert com.js == ["/static/a.js", "/static/b.js", "/static/c.js"]


def test_no_comma_in_assets_list_is_your_problem():
    com = Component(
        name="Test.jinja",
        source="{#js a.js b.js c.js -#}\n",
        url_prefix="/static/"
    )
    assert com.js == ["/static/a.js b.js c.js"]


def test_load_metadata_in_any_order():
    com = Component(
        name="Test.jinja",
        source="""
        {#css a.css #}
        {#def lorem, ipsum=4 #}
        {#js a.js #}
        """,
    )
    assert com.required == ["lorem"]
    assert com.optional == {"ipsum": 4}
    assert com.css == ["a.css"]
    assert com.js == ["a.js"]


def test_ignore_metadata_if_not_first():
    com = Component(
        name="Test.jinja",
        source="""
        I am content
        {#css a.css #}
        {#def lorem, ipsum=4 #}
        {#js a.js #}
        """,
    )
    assert com.required == []
    assert com.optional == {}
    assert com.css == []
    assert com.js == []


def test_ignore_repeated_args_declaration_and_everything_after():
    com = Component(
        name="Test.jinja",
        source="""
        {#def lorem, ipsum=4 #}
        {#def a, b, c, ipsum="nope" #}
        {#css a.css #}
        {#js a.js #}
        """,
    )
    assert com.required == ["lorem"]
    assert com.optional == {"ipsum": 4}
    assert com.css == []
    assert com.js == []


def test_ignore_repeated_css_declaration_and_everything_after():
    com = Component(
        name="Test.jinja",
        source="""
        {#css a.css #}
        {#def lorem, ipsum=4 #}
        {#css b.css #}
        {#js a.js #}
        """,
    )
    assert com.required == ["lorem"]
    assert com.optional == {"ipsum": 4}
    assert com.css == ["a.css"]
    assert com.js == []


def test_ignore_repeated_js_declaration_and_everything_after():
    com = Component(
        name="Test.jinja",
        source="""
        {#css a.css #}
        {#js a.js #}
        {#js b.js #}
        {#def lorem, ipsum=4 #}
        """,
    )
    assert com.required == []
    assert com.optional == {}
    assert com.css == ["a.css"]
    assert com.js == ["a.js"]


def test_linejump_in_args_decl():
    com = Component(
        name="Test.jinja",
        source='{#def\n  message,\n  lorem=4,\n  ipsum="bar"\n#}\n',
    )
    assert com.required == ["message"]
    assert com.optional == {
        "lorem": 4,
        "ipsum": "bar",
    }


def test_global_assets():
    com = Component(
        name="Test.jinja",
        source="""
        {#css a.css, /static/shared/b.css, http://example.com/cdn.css #}
        {#js "http://example.com/cdn.js", a.js, /static/shared/b.js #}
        """,
    )
    assert com.css == ["a.css", "/static/shared/b.css", "http://example.com/cdn.css"]
    assert com.js == ["http://example.com/cdn.js", "a.js", "/static/shared/b.js"]
