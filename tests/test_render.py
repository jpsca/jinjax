import pytest
from jinja2.exceptions import TemplateSyntaxError

import jinjax


def test_render_simple(catalog, folder):
    (folder / "Greeting.jinja").write_text("""
{#def message #}
<div class="greeting [&_a]:flex">{{ message }}</div>
    """)
    html = catalog.render("Greeting", message="Hello world!")
    assert html == '<div class="greeting [&_a]:flex">Hello world!</div>'


def test_render_source(catalog):
    source = """
{#def message #}
<div class="greeting [&_a]:flex">{{ message }}</div>
    """
    html = catalog.render("Greeting", message="Hello world!", __source=source)
    assert html == '<div class="greeting [&_a]:flex">Hello world!</div>'


def test_render_content(catalog, folder):
    (folder / "Card.jinja").write_text("""
<section class="card">
{{ content }}
</section>
    """)

    content = '<button type="button">Close</button>'
    html = catalog.render("Card", __content=content)
    print(html)
    assert html == f"""
<section class="card">
{content}
</section>""".strip()


@pytest.mark.parametrize(
    "source, expected",
    [
        ("<Title>Hi</Title><Title>Hi</Title>", '<h1>Hi</h1><h1>Hi</h1>'),
        ("<Icon /><Icon />", '<i class="icon"></i><i class="icon"></i>'),
        ("<Title>Hi</Title><Icon />", '<h1>Hi</h1><i class="icon"></i>'),
        ("<Icon /><Title>Hi</Title>", '<i class="icon"></i><h1>Hi</h1>'),
    ],
)
def test_render_mix_of_contentful_and_contentless_components(catalog, folder, source, expected):
    (folder / "Icon.jinja").write_text('<i class="icon"></i>')
    (folder / "Title.jinja").write_text("<h1>{{ content }}</h1>")
    (folder / "Page.jinja").write_text(source)

    html = catalog.render("Page")
    assert html == expected


def test_composition(catalog, folder):
    (folder / "Greeting.jinja").write_text("""
{#def message #}
<div class="greeting [&_a]:flex">{{ message }}</div>
""")

    (folder / "CloseBtn.jinja").write_text("""
{#def disabled=False -#}
<button type="button"{{ " disabled" if disabled else "" }}>&times;</button>
""")

    (folder / "Card.jinja").write_text("""
<section class="card">
{{ content }}
<CloseBtn disabled />
</section>
""")

    (folder / "Page.jinja").write_text("""
{#def message #}
<Card>
<Greeting message={message} />
<button type="button">Close</button>
</Card>
""")

    html = catalog.render("Page", message="Hello")
    print(html)
    assert """
<section class="card">
<div class="greeting [&_a]:flex">Hello</div>
<button type="button">Close</button>
<button type="button" disabled>&times;</button>
</section>
""".strip() in html


def test_just_properties(catalog, folder):
    (folder / "Lorem.jinja").write_text("""
{#def ipsum=False #}
<p>lorem {{ "ipsum" if ipsum else "lorem" }}</p>
""")

    (folder / "Layout.jinja").write_text("""
<main>
{{ content }}
</main>
""")

    (folder / "Page.jinja").write_text("""
<Layout>
<Lorem ipsum />
<p>meh</p>
<Lorem />
</Layout>
""")

    html = catalog.render("Page")
    print(html)
    assert """
<main>
<p>lorem ipsum</p>
<p>meh</p>
<p>lorem lorem</p>
</main>
""".strip() in html


def test_render_assets(catalog, folder):
    (folder / "Greeting.jinja").write_text("""
{#def message #}
{#css greeting.css #}
{#js greeting.js #}
<div class="greeting [&_a]:flex">{{ message }}</div>
""")

    (folder / "Card.jinja").write_text("""
{#css card.css #}
{#js card.js, shared.js #}
<section class="card">
{{ content }}
</section>
""")

    (folder / "Layout.jinja").write_text("""
<html>
{{ catalog.render_assets() }}
{{ content }}
</html>
""")

    (folder / "Page.jinja").write_text("""
{#def message #}
{#js shared.js #}
<Layout>
<Card>
<Greeting message={message} />
<button type="button">Close</button>
</Card>
</Layout>
""")

    html = catalog.render("Page", message="Hello")
    print(html)
    assert """
<html>
<link rel="stylesheet" href="/static/components/card.css">
<link rel="stylesheet" href="/static/components/greeting.css">
<script src="/static/components/shared.js" defer></script>
<script src="/static/components/card.js" defer></script>
<script src="/static/components/greeting.js" defer></script>
<section class="card">
<div class="greeting [&_a]:flex">Hello</div>
<button type="button">Close</button>
</section>
</html>
""".strip() in html


def test_global_values(catalog, folder):
    (folder / "Global.jinja").write_text("""{{ globalvar }}""")
    message = "Hello world!"
    catalog.jinja_env.globals["globalvar"] = message
    html = catalog.render("Global")
    print(html)
    assert message in html


def test_required_attr_are_required(catalog, folder):
    (folder / "Greeting.jinja").write_text("""
{#def message #}
<div class="greeting">{{ message }}</div>
""")

    with pytest.raises(jinjax.MissingRequiredArgument):
        catalog.render("Greeting")


def test_subfolder(catalog, folder):
    sub = folder / "UI"
    sub.mkdir()
    (folder / "Meh.jinja").write_text("<UI.Tab>Meh</UI.Tab>")
    (sub / "Tab.jinja").write_text('<div class="tab">{{ content }}</div>')

    html = catalog.render("Meh")
    assert html == '<div class="tab">Meh</div>'


def test_default_attr(catalog, folder):
    (folder / "Greeting.jinja").write_text("""
{#def message="Hello", world=False #}
<div>{{ message }}{% if world %} World{% endif %}</div>
""")

    (folder / "Page.jinja").write_text("""
<Greeting />
<Greeting message="Hi" />
<Greeting world={False} />
<Greeting world={True} />
<Greeting world />
""")

    html = catalog.render("Page", message="Hello")
    print(html)
    assert """
<div>Hello</div>
<div>Hi</div>
<div>Hello</div>
<div>Hello World</div>
<div>Hello World</div>
""".strip() in html


def test_raw_content(catalog, folder):
    (folder / "Code.jinja").write_text("""
<pre class="code">
{{ content|e }}
</pre>
""")

    (folder / "Page.jinja").write_text("""
<Code>
{% raw %}
{#def message="Hello", world=False #}
<Header />
<div>{{ message }}{% if world %} World{% endif %}</div>
{% endraw %}
</Code>
""")

    html = catalog.render("Page")
    print(html)
    assert """
<pre class="code">
{#def message=&#34;Hello&#34;, world=False #}
&lt;Header /&gt;
&lt;div&gt;{{ message }}{% if world %} World{% endif %}&lt;/div&gt;
</pre>
""".strip() in html


def test_multiple_raw(catalog, folder):
    (folder / "C.jinja").write_text("""
<div {{ attrs.render() }}></div>
""")

    (folder / "Page.jinja").write_text("""
<C id="1" />
{% raw -%}
<C id="2" />
{%- endraw %}
<C id="3" />
{% raw %}<C id="4" />{% endraw %}
<C id="5" />
""")

    html = catalog.render("Page", message="Hello")
    print(html)
    assert """
<div id="1"></div>
<C id="2" />
<div id="3"></div>
<C id="4" />
<div id="5"></div>
""".strip() in html


def test_check_for_unclosed(catalog, folder):
    (folder / "Lorem.jinja").write_text("""
{#def ipsum=False #}
<p>lorem {{ "ipsum" if ipsum else "lorem" }}</p>
""")

    (folder / "Page.jinja").write_text("""
<main>
<Lorem ipsum>
</main>
""")
    with pytest.raises(TemplateSyntaxError):
        try:
            catalog.render("Page")
        except TemplateSyntaxError as err:
            print(err)
            raise


def test_dict_as_attr(catalog, folder):
    (folder / "CitiesList.jinja").write_text("""
{#def cities #}
{% for city, country in cities.items() -%}
<p>{{ city }}, {{ country }}</p>
{%- endfor %}
""")

    (folder / "Page.jinja").write_text("""
<CitiesList cities={{
    "Lima": "Peru",
    "New York": "USA",
}}/>
""")

    html = catalog.render("Page")
    assert html == '<p>Lima, Peru</p><p>New York, USA</p>'
