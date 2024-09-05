from pathlib import Path
from threading import Thread

import pytest
from markupsafe import Markup

import jinjax


@pytest.mark.parametrize("autoescape", [True, False])
def test_render_assets(catalog, folder, autoescape):
    catalog.jinja_env.autoescape = autoescape

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
<link rel="stylesheet" href="https://somewhere.com/style.css">
<link rel="stylesheet" href="/static/components/card.css">
<link rel="stylesheet" href="/static/components/greeting.css">
<link rel="stylesheet" href="http://example.com/super.css">
<script type="module" src="https://somewhere.com/blabla.js"></script>
<script type="module" src="/static/components/shared.js"></script>
<script type="module" src="/static/components/card.js"></script>
<script type="module" src="/static/components/greeting.js"></script>
<section class="card">
<div class="greeting [&_a]:flex">Hello</div>
<button type="button">Close</button>
</section>
</html>
""".strip()
        in html
    )


@pytest.mark.parametrize("autoescape", [True, False])
def test_cleanup_assets(catalog, folder, autoescape):
    catalog.jinja_env.autoescape = autoescape

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


@pytest.mark.parametrize("autoescape", [True, False])
def test_fingerprint_assets(catalog, folder: Path, autoescape):
    catalog.jinja_env.autoescape = autoescape

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


@pytest.mark.parametrize("autoescape", [True, False])
def test_auto_load_assets_with_same_name(catalog, folder, autoescape):
    catalog.jinja_env.autoescape = autoescape

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
<script type="module" src="/static/components/shared.js"></script>
<script type="module" src="/static/components/common/Form.js"></script>
<form></form>
""".strip()

    assert html == Markup(expected)


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=None, kwargs=None):
        args = args or ()
        kwargs = kwargs or {}
        Thread.__init__(
            self,
            group=group,
            target=target,
            name=name,
            args=args,
            kwargs=kwargs,
        )
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def test_thread_safety_of_render_assets(catalog, folder):
    NUM_THREADS = 5

    child_tmpl = """
{#css "c{i}.css" #}
{#js "c{i}.js" #}
<p>Child {i}</p>""".strip()

    parent_tmpl = """
{{ catalog.render_assets() }}
{{ content }}""".strip()

    comp_tmpl = """
{#css "a{i}.css", "b{i}.css" #}
{#js "a{i}.js", "b{i}.js" #}
<Parent{i}><Child{i} /></Parent{i}>""".strip()

    expected_tmpl = """
<link rel="stylesheet" href="/static/components/a{i}.css">
<link rel="stylesheet" href="/static/components/b{i}.css">
<link rel="stylesheet" href="/static/components/c{i}.css">
<script type="module" src="/static/components/a{i}.js"></script>
<script type="module" src="/static/components/b{i}.js"></script>
<script type="module" src="/static/components/c{i}.js"></script>
<p>Child {i}</p>""".strip()

    def render(i):
        return catalog.render(f"Page{i}")

    for i in range(NUM_THREADS):
        si = str(i)
        child_name = f"Child{i}.jinja"
        child_src = child_tmpl.replace("{i}", si)

        parent_name = f"Parent{i}.jinja"
        parent_src = parent_tmpl.replace("{i}", si)

        comp_name = f"Page{i}.jinja"
        comp_src = comp_tmpl.replace("{i}", si)

        (folder / child_name).write_text(child_src)
        (folder / comp_name).write_text(comp_src)
        (folder / parent_name).write_text(parent_src)

    threads = []

    for i in range(NUM_THREADS):
        thread = ThreadWithReturnValue(target=render, args=(i,))
        threads.append(thread)
        thread.start()

    results = [thread.join() for thread in threads]

    for i, result in enumerate(results):
        expected = expected_tmpl.replace("{i}", str(i))
        print(f"---- EXPECTED {i}----")
        print(expected)
        print(f"---- RESULT {i}----")
        print(result)
        assert result == Markup(expected)


def test_same_thread_assets_independence(catalog, folder):
    catalog2 = jinjax.Catalog()
    catalog2.add_folder(folder)

    print(catalog._key)
    print(catalog2._key)

    (folder / "Parent.jinja").write_text(
        """
{{ catalog.render_assets() }}
{{ content }}""".strip()
    )

    (folder / "Comp1.jinja").write_text(
        """
{#css "a.css" #}
{#js "a.js" #}
<Parent />""".strip()
    )

    (folder / "Comp2.jinja").write_text(
        """
{#css "b.css" #}
{#js "b.js" #}
<Parent />""".strip()
    )

    expected_1 = """
<link rel="stylesheet" href="/static/components/a.css">
<script type="module" src="/static/components/a.js"></script>""".strip()

    expected_2 = """
<link rel="stylesheet" href="/static/components/b.css">
<script type="module" src="/static/components/b.js"></script>""".strip()

    html1 = catalog.render("Comp1")
    # `irender` instead of `render` so the assets are not cleared
    html2 = catalog2.irender("Comp2")
    print(html1)
    print(html2)
    assert html1 == Markup(expected_1)
    assert html2 == Markup(expected_2)
