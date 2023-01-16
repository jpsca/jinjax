import pytest

import jinjax


def test_render_simple(catalog, folder):
    (folder / "Greeting.jinja").write_text("""
{#def message #}
<div class="greeting">{{ message }}</div>
    """)
    html = catalog.render("Greeting", message="Hello world!")
    assert html == '<div class="greeting">Hello world!</div>'


def test_render_source(catalog):
    source = """
{#def message #}
<div class="greeting">{{ message }}</div>
    """
    html = catalog.render("Greeting", message="Hello world!", __source=source)
    assert html == '<div class="greeting">Hello world!</div>'


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


def test_extension(catalog, folder):
    (folder / "Greeting.jinja").write_text("""
{#def message #}
<div class="greeting">{{ message }}</div>
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
<div class="greeting">Hello</div>
<button type="button">Close</button>
<button type="button" disabled>&times;</button>
</section>
""".strip() in html


def test_render_assets(catalog, folder):
    (folder / "Greeting.jinja").write_text("""
{#def message #}
{#css greeting.css #}
{#js greeting.js #}
<div class="greeting">{{ message }}</div>
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
<div class="greeting">Hello</div>
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
