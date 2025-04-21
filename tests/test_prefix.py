"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
import jinja2
import pytest
from markupsafe import Markup


@pytest.mark.parametrize("undefined", [jinja2.Undefined, jinja2.StrictUndefined])
@pytest.mark.parametrize("autoescape", [True, False])
def test_render_prefixed(catalog, folder, folder_t, autoescape, undefined):
    """Components mounted with a prefix should be able to import other components
    from the same folder without specifying the prefix.
    """
    catalog.jinja_env.autoescape = autoescape
    catalog.jinja_env.undefined = undefined
    catalog.add_folder(folder_t, prefix="ui")

    (folder / "Test.jinja").write_text("<ui:Title />")

    (folder_t / "Title.jinja").write_text("prefix")

    html = catalog.render("Test")
    assert html == Markup("prefix")


@pytest.mark.parametrize("undefined", [jinja2.Undefined, jinja2.StrictUndefined])
@pytest.mark.parametrize("autoescape", [True, False])
def test_prefix_namespace(catalog, folder, folder_t, autoescape, undefined):
    """Components mounted with a prefix should be able to import other components
    from the same folder without specifying the prefix.
    """
    catalog.jinja_env.autoescape = autoescape
    catalog.jinja_env.undefined = undefined
    catalog.add_folder(folder_t, prefix="ui")

    (folder / "Title.jinja").write_text("parent")

    (folder_t / "Title.jinja").write_text("prefix")
    (folder_t / "Alert.jinja").write_text("<Title />")

    html = catalog.render("ui:Alert")
    assert html == Markup("prefix")


@pytest.mark.parametrize("undefined", [jinja2.Undefined, jinja2.StrictUndefined])
@pytest.mark.parametrize("autoescape", [True, False])
def test_prefix_namespace_sub(catalog, folder, folder_t, autoescape, undefined):
    """Components mounted with a prefix should be able to import other components
    from the same folder without specifying the prefix, even if those components
    are in a subfolder.
    """
    catalog.jinja_env.autoescape = autoescape
    catalog.jinja_env.undefined = undefined
    catalog.add_folder(folder_t, prefix="ui")


    (folder / "Title.jinja").write_text("parent")
    (folder / "sub").mkdir()
    (folder / "sub" / "Title.jinja").write_text("sub/parent")

    (folder_t / "Title.jinja").write_text("sub")
    (folder_t / "sub").mkdir()
    (folder_t / "sub" / "Title.jinja").write_text("sub/prefix")
    (folder_t / "Alert.jinja").write_text("<sub.Title />")

    html = catalog.render("ui:Alert")
    assert html == Markup("sub/prefix")


@pytest.mark.parametrize("undefined", [jinja2.Undefined, jinja2.StrictUndefined])
@pytest.mark.parametrize("autoescape", [True, False])
def test_prefix_fallback(catalog, folder, folder_t, autoescape, undefined):
    """If a component is not found in the folder with the prefix, it should
    fallback to the no-prefix folders.
    """
    catalog.jinja_env.autoescape = autoescape
    catalog.jinja_env.undefined = undefined
    catalog.add_folder(folder_t, prefix="ui")

    (folder / "Title.jinja").write_text("parent")
    (folder_t / "Alert.jinja").write_text("<Title />")

    html = catalog.render("ui:Alert")
    assert html == Markup("parent")


@pytest.mark.parametrize("undefined", [jinja2.Undefined, jinja2.StrictUndefined])
@pytest.mark.parametrize("autoescape", [True, False])
def test_prefix_namespace_assets(catalog, folder, folder_t, autoescape, undefined):
    """Components import without specifying the prefix should also be
    able to auto-import their assets.
    """
    catalog.jinja_env.autoescape = autoescape
    catalog.jinja_env.undefined = undefined
    catalog.add_folder(folder_t, prefix="ui")

    (folder_t / "Title.jinja").write_text("prefix")
    (folder_t / "Title.css").touch()
    (folder_t / "Layout.jinja").write_text("""
{{ catalog.render_assets() }}
{{ content }}
""")
    (folder_t / "Alert.jinja").write_text("<Layout><Title /></Layout>")

    html = catalog.render("ui:Alert")
    assert html == Markup("""
<link rel="stylesheet" href="/static/components/ui/Title.css">
prefix
""".strip())
