"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
from pathlib import Path

import jinja2
import pytest
from markupsafe import Markup


@pytest.mark.parametrize("undefined", [jinja2.Undefined, jinja2.StrictUndefined])
@pytest.mark.parametrize("autoescape", [True, False])
def test_render_assets(catalog, folder, autoescape, undefined):
    catalog.jinja_env.autoescape = autoescape
    catalog.jinja_env.undefined = undefined

    (folder / "Greeting.jinja").write_text(
        """
{#def message #}
{#css greeting.css, http://example.com/super.css #}
{#js greeting.js #}
<div class="greeting [&_a]:flex">{{ message }}</div>
"""
    )

    (folder / "Card.jinja").write_text(
        """
{#css https://somewhere.com/style.css, card.css #}
{#js card.js, shared.js #}
<section class="card">
{{ content }}
</section>
"""
    )

    (folder / "Layout.jinja").write_text(
        """
<html>
{{ catalog.render_assets() }}
{{ content }}
</html>
"""
    )

    (folder / "Page.jinja").write_text(
        """
{#def message #}
{#js https://somewhere.com/blabla.js, shared.js #}
<Layout>
<Card>
<Greeting :message="message" />
<button type="button">Close</button>
</Card>
</Layout>
"""
    )

    html = catalog.render("Page", message="Hello")
    print(html)
    assert (
        """
<html>
<link rel="stylesheet" href="/static/components/card.css">
<link rel="stylesheet" href="/static/components/greeting.css">
<link rel="stylesheet" href="http://example.com/super.css">
<link rel="stylesheet" href="https://somewhere.com/style.css">
<script type="module" src="/static/components/card.js"></script>
<script type="module" src="/static/components/greeting.js"></script>
<script type="module" src="/static/components/shared.js"></script>
<script type="module" src="https://somewhere.com/blabla.js"></script>
<section class="card">
<div class="greeting [&_a]:flex">Hello</div>
<button type="button">Close</button>
</section>
</html>
""".strip()
        in html
    )


@pytest.mark.parametrize("undefined", [jinja2.Undefined, jinja2.StrictUndefined])
@pytest.mark.parametrize("autoescape", [True, False])
def test_cleanup_assets(catalog, folder, autoescape, undefined):
    catalog.jinja_env.autoescape = autoescape
    catalog.jinja_env.undefined = undefined

    (folder / "Layout.jinja").write_text("""
<html>
{{ catalog.render_assets() }}
{{ content }}
</html>
""")

    (folder / "Foo.jinja").write_text("""
{#js foo.js #}
<Layout>
<p>Foo</p>
</Layout>
""")

    (folder / "Bar.jinja").write_text("""
{#js bar.js #}
<Layout>
<p>Bar</p>
</Layout>
""")

    html = catalog.render("Foo")
    print(html, "\n")
    assert (
        """
<html>
<script type="module" src="/static/components/foo.js"></script>
<p>Foo</p>
</html>
""".strip()
        in html
    )

    html = catalog.render("Bar")
    print(html)
    assert (
        """
<html>
<script type="module" src="/static/components/bar.js"></script>
<p>Bar</p>
</html>
""".strip()
        in html
    )


@pytest.mark.parametrize("undefined", [jinja2.Undefined, jinja2.StrictUndefined])
@pytest.mark.parametrize("autoescape", [True, False])
def test_fingerprint_assets(catalog, folder: Path, autoescape, undefined):
    catalog.jinja_env.autoescape = autoescape
    catalog.jinja_env.undefined = undefined

    (folder / "Layout.jinja").write_text("""
<html>
{{ catalog.render_assets() }}
{{ content }}
</html>
""")

    (folder / "Page.jinja").write_text("""
{#css app.css, http://example.com/super.css #}
{#js app.js #}
<Layout>Hi</Layout>
""")

    (folder / "app.css").write_text("...")

    catalog.fingerprint = True
    html = catalog.render("Page", message="Hello")
    print(html)

    assert 'src="/static/components/app.js"' in html
    assert 'href="/static/components/app-' in html
    assert 'href="http://example.com/super.css' in html


@pytest.mark.parametrize("undefined", [jinja2.Undefined, jinja2.StrictUndefined])
@pytest.mark.parametrize("autoescape", [True, False])
def test_auto_load_assets_with_same_name(catalog, folder, autoescape, undefined):
    catalog.jinja_env.autoescape = autoescape
    catalog.jinja_env.undefined = undefined

    (folder / "Layout.jinja").write_text(
        """{{ catalog.render_assets() }}\n{{ content }}"""
    )

    (folder / "FooBar.css").touch()

    (folder / "common").mkdir()
    (folder / "common" / "Form.jinja").write_text(
        """
{#js "shared.js" #}
<form></form>"""
    )

    (folder / "common" / "Form.css").touch()
    (folder / "common" / "Form.js").touch()

    (folder / "Page.jinja").write_text(
        """
{#css "Page.css" #}
<Layout><common.Form></common.Form></Layout>"""
    )

    (folder / "Page.css").touch()
    (folder / "Page.js").touch()

    html = catalog.render("Page")
    print(html)

    expected = """
<link rel="stylesheet" href="/static/components/Page.css">
<link rel="stylesheet" href="/static/components/common/Form.css">
<script type="module" src="/static/components/Page.js"></script>
<script type="module" src="/static/components/common/Form.js"></script>
<script type="module" src="/static/components/shared.js"></script>
<form></form>
""".strip()

    assert html == Markup(expected)


@pytest.mark.parametrize("undefined", [jinja2.Undefined, jinja2.StrictUndefined])
@pytest.mark.parametrize("autoescape", [True, False])
def test_auto_load_assets_for_kebab_cased_names(catalog, folder, autoescape, undefined):
    catalog.jinja_env.autoescape = autoescape
    catalog.jinja_env.undefined = undefined

    (folder / "Layout.jinja").write_text(
        """{{ catalog.render_assets() }}\n{{ content }}"""
    )

    (folder / "my-component.jinja").write_text("")
    (folder / "my-component.css").touch()
    (folder / "my-component.js").touch()
    (folder / "page.jinja").write_text("<Layout><MyComponent /></Layout>")

    html = catalog.render("Page")
    print(html)

    assert  "/static/components/my-component.css" in html
    assert  "/static/components/my-component.js" in html
