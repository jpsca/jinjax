"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
import typing as t
from pathlib import Path

import jinjax


def application(environ, start_response) -> list[bytes]:
    status = "200 OK"
    headers = [("Content-type", "text/plain")]
    start_response(status, headers)
    return [b"NOPE"]


def make_environ(**kw) -> dict[str, t.Any]:
    kw.setdefault("PATH_INFO", "/")
    kw.setdefault("REQUEST_METHOD", "GET")
    return kw


def mock_start_response(status: str, headers: dict[str, t.Any]):
    pass


def get_catalog(folder: "str | Path", **kw) -> jinjax.Catalog:
    catalog = jinjax.Catalog(**kw)
    catalog.add_folder(folder)
    return catalog


TMiddleware = t.Callable[
    [
        dict[str, t.Any],
        t.Callable[[str, dict[str, t.Any]], None],
    ],
    t.Any
]

def run_middleware(middleware: TMiddleware, url: str):
    return middleware(make_environ(PATH_INFO=url), mock_start_response)


# Tests


def test_css_is_returned(folder):
    (folder / "page.css").write_text("/* Page.css */")
    catalog = get_catalog(folder)
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/components/page.css")
    assert resp and not isinstance(resp, list)
    text = resp.filelike.read().strip()
    assert text == b"/* Page.css */"


def test_js_is_returned(folder):
    (folder / "page.js").write_text("/* Page.js */")
    catalog = get_catalog(folder)
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/components/page.js")
    assert resp and not isinstance(resp, list)
    text = resp.filelike.read().strip()
    assert text == b"/* Page.js */"


def test_other_file_extensions_ignored(folder):
    (folder / "Page.jinja").write_text("???")
    catalog = get_catalog(folder)
    middleware = catalog.get_middleware(application)
    resp = run_middleware(middleware, "/static/components/Page.jinja")
    assert resp == [b"NOPE"]


def test_add_custom_extensions(folder):
    (folder / "Page.jinja").write_text("???")
    catalog = get_catalog(folder)
    middleware = catalog.get_middleware(application, allowed_ext=[".jinja"])

    resp = run_middleware(middleware, "/static/components/Page.jinja")
    assert resp and not isinstance(resp, list)
    text = resp.filelike.read().strip()
    assert text == b"???"


def test_custom_root_url(folder):
    (folder / "page.css").write_text("/* Page.css */")
    catalog = get_catalog(folder, root_url="/static/co/")
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/co/page.css")
    assert resp and not isinstance(resp, list)
    text = resp.filelike.read().strip()
    assert text == b"/* Page.css */"


def test_autorefresh_load(folder):
    (folder / "page.css").write_text("/* Page.css */")
    catalog = get_catalog(folder)
    middleware = catalog.get_middleware(application, autorefresh=True)

    resp = run_middleware(middleware, "/static/components/page.css")
    assert resp and not isinstance(resp, list)
    text = resp.filelike.read().strip()
    assert text == b"/* Page.css */"


def test_autorefresh_block(folder):
    (folder / "Page.jinja").write_text("???")
    catalog = get_catalog(folder)
    middleware = catalog.get_middleware(application, autorefresh=True)

    resp = run_middleware(middleware, "/static/components/Page.jinja")
    assert resp == [b"NOPE"]


def test_multiple_folders(tmp_path):
    folder1 = tmp_path / "folder1"
    folder1.mkdir()
    (folder1 / "folder1.css").write_text("folder1")

    folder2 = tmp_path / "folder2"
    folder2.mkdir()
    (folder2 / "folder2.css").write_text("folder2")

    catalog = jinjax.Catalog()
    catalog.add_folder(folder1)
    catalog.add_folder(folder2)
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/components/folder1.css")
    assert resp.filelike.read() == b"folder1"
    resp = run_middleware(middleware, "/static/components/folder2.css")
    assert resp.filelike.read() == b"folder2"


def test_multiple_folders_precedence(tmp_path):
    folder1 = tmp_path / "folder1"
    folder1.mkdir()
    (folder1 / "name.css").write_text("folder1")

    folder2 = tmp_path / "folder2"
    folder2.mkdir()
    (folder2 / "name.css").write_text("folder2")

    catalog = jinjax.Catalog()
    catalog.add_folder(folder1)
    catalog.add_folder(folder2)
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/components/name.css")
    assert resp.filelike.read() == b"folder1"
