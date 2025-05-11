import jinja2
import pytest

from jinjax import JinjaX


VALID_DATA = (
    # Simple case
    (
        """<Foo bar="baz">content</Foo>""",
        """{% call(_slot="") catalog.irender("Foo", __prefix=__prefix, **{"bar":"baz"}) -%}content{%- endcall %}""",
    ),
    # Self-closing tag
    (
        """<Alert type="success" message="Success!" />""",
        """{{ catalog.irender("Alert", __prefix=__prefix, **{"type":"success", "message":"Success!"}) }}""",
    ),
    # No attributes
    (
        """<Foo>content</Foo>""",
        """{% call(_slot="") catalog.irender("Foo", __prefix=__prefix, **{}) -%}content{%- endcall %}""",
    ),
    # No attributes, self-closing tag
    (
        """<Foo />""",
        """{{ catalog.irender("Foo", __prefix=__prefix, **{}) }}""",
    ),
    # Line breaks
    (
        """<Foo
          bar="baz"
          lorem="ipsum"
        >content</Foo>""",
        """{% call(_slot="") catalog.irender("Foo", __prefix=__prefix, **{"bar":"baz", "lorem":"ipsum"}) -%}content{%- endcall %}""",
    ),
    # Line breaks, self-closing tag
    (
        """<Foo
          bar="baz"
          lorem="ipsum"
          green
        />""",
        """{{ catalog.irender("Foo", __prefix=__prefix, **{"bar":"baz", "lorem":"ipsum", "green":True}) }}""",
    ),
    # Subfolder in tag name
    (
        """<sub.Alert type="success">content</sub.Alert>""",
        """{% call(_slot="") catalog.irender("sub.Alert", __prefix=__prefix, **{"type":"success"}) -%}content{%- endcall %}""",
    ),
    # Python expression in attribute and boolean attributes
    (
        """<Foo bar={{ 42 + 4 }} green large>content</Foo>""",
        """{% call(_slot="") catalog.irender("Foo", __prefix=__prefix, **{"bar":42 + 4, "green":True, "large":True}) -%}content{%- endcall %}""",
    ),
    # Prefix in tag name and `'}}'` in attribute
    (
        """<ui:Button lorem={{ 'ipsum }}' }} foo="bar">content</ui:Button>""",
        """{% call(_slot="") catalog.irender("ui:Button", __prefix=__prefix, **{"lorem":'ipsum }}', "foo":"bar"}) -%}content{%- endcall %}""",
    ),
    # `>` in expression
    (
        """<CloseBtn disabled={{ num > 4 }} />""",
        """{{ catalog.irender("CloseBtn", __prefix=__prefix, **{"disabled":num > 4}) }}""",
    ),
    # `>` in attribute value
    (
        """<CloseBtn data-closer-action="click->closer#close" />""",
        """{{ catalog.irender("CloseBtn", __prefix=__prefix, **{"data_closer_action":"click->closer#close"}) }}""",
    ),
)


@pytest.mark.parametrize("source, expected", VALID_DATA)
def test_process_valid_tags(source, expected):
    # Test the process_tags method of the JinjaX extension
    env = jinja2.Environment()
    jinjax = JinjaX(env)
    result = jinjax.process_tags(source)
    print(result)
    assert result == expected


INVALID_DATA = (
    # Tag not closed
    (
        """<Foo bar="baz">content aslasals ls,als,as""",
        jinja2.TemplateSyntaxError,
        "Unclosed component",
    ),
    # String attribute not closed
    (
        """<Foo bar="baz>content lorem ipsumsdsd""",
        jinja2.TemplateSyntaxError,
        "Syntax error",
    ),
    # Expression not closed
    (
        """<Foo bar={{ 42 + 4>content</Foo>""",
        jinja2.TemplateSyntaxError,
        "Syntax error",
    ),
    # Expression not opem
    (
        """<Foo bar=42 + 4}}>content</Foo>""",
        jinja2.TemplateSyntaxError,
        "Syntax error",
    ),
)


@pytest.mark.parametrize("source, exception, match", INVALID_DATA)
def test_process_invalid_tags(source, exception, match):
    # Test the process_tags method of the JinjaX extension
    env = jinja2.Environment()
    jinjax = JinjaX(env)
    with pytest.raises(exception, match=f".*{match}.*"):
        jinjax.process_tags(source)


def test_process_nested_Same_tag():
    # Test the process_tags method for the same tag nested
    env = jinja2.Environment()
    jinjax = JinjaX(env)
    source = """
<Card class="card">
  WTF
  <Card class="card-header">abc</Card>
  <Card class="card-body">
    <div><Card>Text</Card></div>
  </Card>
</Card>
    """
    expected = """
{% call(_slot="") catalog.irender("Card", __prefix=__prefix, **{"class":"card"}) -%}
  WTF
  {% call(_slot="") catalog.irender("Card", __prefix=__prefix, **{"class":"card-header"}) -%}abc{%- endcall %}
  {% call(_slot="") catalog.irender("Card", __prefix=__prefix, **{"class":"card-body"}) -%}
    <div>{% call(_slot="") catalog.irender("Card", __prefix=__prefix, **{}) -%}Text{%- endcall %}</div>
  {%- endcall %}
{%- endcall %}
"""
    result = jinjax.process_tags(source)
    print(result)
    assert result.strip() == expected.strip()
