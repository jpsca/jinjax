from threading import Thread

from markupsafe import Markup

import jinjax


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

    (folder / "Parent.jinja").write_text("""
{{ catalog.render_assets() }}
{{ content }}""".strip())

    (folder / "Comp1.jinja").write_text("""
{#css "a.css" #}
{#js "a.js" #}
<Parent />""".strip())

    (folder / "Comp2.jinja").write_text("""
{#css "b.css" #}
{#js "b.js" #}
<Parent />""".strip())

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


def test_thread_safety_of_template_globals(catalog, folder):
    NUM_THREADS = 5
    (folder / "Page.jinja").write_text("{{ globalvar if globalvar is defined else 'not set' }}")

    def render(i):
        return catalog.render("Page", __globals={"globalvar": i})

    threads = []

    for i in range(NUM_THREADS):
        thread = ThreadWithReturnValue(target=render, args=(i,))
        threads.append(thread)
        thread.start()

    results = [thread.join() for thread in threads]

    for i, result in enumerate(results):
        assert result == Markup(str(i))

