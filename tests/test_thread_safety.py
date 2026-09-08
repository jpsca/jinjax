"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
from threading import Barrier, Event, Thread

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

    def join(self, *args, **kwargs):
        Thread.join(self, *args, **kwargs)
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

    print("Catalog1 key:", catalog._key)
    print("Catalog2 key:", catalog2._key)

    # Check if the context variables exist before the test
    print("Before any rendering:")
    print("Catalog1 in collected_css:", catalog._key in jinjax.catalog.collected_css)
    print("Catalog2 in collected_css:", catalog2._key in jinjax.catalog.collected_css)
    print("collected_css keys:", list(jinjax.catalog.collected_css.keys()))
    print("collected_js keys:", list(jinjax.catalog.collected_js.keys()))

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

    # Render first component with first catalog
    html1 = catalog.render("Comp1")

    # Check context variables after first render
    print("\nAfter first render:")
    print("Catalog1 collected_css:", catalog.collected_css)
    print("Catalog2 collected_css:", catalog2.collected_css)
    print("Catalog1 in collected_css:", catalog._key in jinjax.catalog.collected_css)
    print("Catalog2 in collected_css:", catalog2._key in jinjax.catalog.collected_css)
    print("collected_css keys:", list(jinjax.catalog.collected_css.keys()))

    # Render second component with second catalog
    html2 = catalog2.render("Comp2")

    # Check context variables after second render
    print("\nAfter second render:")
    print("Catalog1 collected_css:", catalog.collected_css)
    print("Catalog2 collected_css:", catalog2.collected_css)
    print("Catalog1 in collected_css:", catalog._key in jinjax.catalog.collected_css)
    print("Catalog2 in collected_css:", catalog2._key in jinjax.catalog.collected_css)
    print("collected_css keys:", list(jinjax.catalog.collected_css.keys()))

    print("\nHTML outputs:")
    print("HTML1:", html1)
    print("HTML2:", html2)

    assert html1 == Markup(expected_1)
    assert html2 == Markup(expected_2)


def test_thread_safety_of_template_globals(catalog, folder):
    """Every thread must render its own globals, even when they all hold the
    same cached component at the same time.

    The globals are set and the component looked up *before* the barrier, so
    all the threads sit between the lookup and the render simultaneously. That
    is the window in which a shared template would end up with the globals of
    whichever thread happened to be the last one.
    """
    NUM_THREADS = 5
    (folder / "Page.jinja").write_text("{{ globalvar }}")

    # Warm the cache, so all the threads get the same compiled template
    assert catalog.render("Page", _globals={"globalvar": "warmup"}) == Markup("warmup")

    barrier = Barrier(NUM_THREADS, timeout=5)

    def render(i):
        catalog.tmpl_globals = {"globalvar": i}
        component = catalog._get_component("Page")
        barrier.wait()
        return component.render()

    threads = []

    for i in range(NUM_THREADS):
        thread = ThreadWithReturnValue(target=render, args=(i,))
        threads.append(thread)
        thread.start()

    results = [thread.join() for thread in threads]

    for i, result in enumerate(results):
        assert result == Markup(str(i))


def test_cached_template_globals_are_not_shared_between_threads(catalog, folder):
    """A render must not emit the globals of another request that used the
    same cached component in the meantime."""
    (folder / "Page.jinja").write_text("<p>{{ user }}</p>")

    # Warm the cache, so both threads get the same compiled template
    assert catalog.render("Page", _globals={"user": "warmup"}) == Markup("<p>warmup</p>")

    got_component = Event()
    other_finished = Event()
    results = {}

    def first():
        catalog.tmpl_globals = {"user": "first"}
        component = catalog._get_component("Page")
        # Let another request render the same component before this one does
        got_component.set()
        other_finished.wait(timeout=5)
        results["first"] = component.render()

    def second():
        got_component.wait(timeout=5)
        results["second"] = catalog.render("Page", _globals={"user": "second"})
        other_finished.set()

    threads = [Thread(target=first), Thread(target=second)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results["first"] == Markup("<p>first</p>")
    assert results["second"] == Markup("<p>second</p>")


def test_render_globals_are_not_stored_in_the_shared_cache(catalog, folder):
    (folder / "Page.jinja").write_text("<p>{{ user }}</p>")
    assert catalog.render("Page", _globals={"user": "secret"}) == Markup("<p>secret</p>")

    assert catalog._cache
    for cache in catalog._cache.values():
        assert "tmpl_globals" not in cache
        assert "user" not in cache["tmpl"].globals
