"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""

import os
from pathlib import Path

import pytest

import jinjax


def test_add_folder_with_default_prefix():
    catalog = jinjax.Catalog()
    catalog.add_folder("file_path")

    assert "file_path" in catalog.prefixes[""].searchpath


def test_add_folder_with_custom_prefix():
    catalog = jinjax.Catalog()
    catalog.add_folder("file_path", prefix="custom")

    assert "file_path" in catalog.prefixes["custom"].searchpath


def test_add_folder_with_dirty_prefix():
    catalog = jinjax.Catalog()
    catalog.add_folder("file_path", prefix="/custom.")

    assert "/custom." not in catalog.prefixes
    assert "file_path" in catalog.prefixes["custom"].searchpath


def test_add_folders_with_same_prefix():
    catalog = jinjax.Catalog()
    catalog.add_folder("file_path1", prefix="custom")
    catalog.add_folder("file_path2", prefix="custom")

    assert "file_path1" in catalog.prefixes["custom"].searchpath
    assert "file_path2" in catalog.prefixes["custom"].searchpath


def test_add_same_folder_in_same_prefix_does_nothing():
    catalog = jinjax.Catalog()
    catalog.add_folder("file_path", prefix="custom")
    catalog.add_folder("file_path", prefix="custom")

    assert catalog.prefixes["custom"].searchpath.count("file_path") == 1


def test_add_module_legacy():
    class Module:
        components_path = "legacy_path"

    catalog = jinjax.Catalog()
    module = Module()
    catalog.add_module(module, prefix="legacy")

    assert "legacy_path" in catalog.prefixes["legacy"].searchpath


def test_add_module_legacy_with_default_prefix():
    class Module:
        components_path = "legacy_path"

    catalog = jinjax.Catalog()
    module = Module()
    catalog.add_module(module)

    assert "legacy_path" in catalog.prefixes[""].searchpath


def test_add_module_fails_with_other_modules():
    class Module:
        pass

    catalog = jinjax.Catalog()
    module = Module()
    with pytest.raises(AttributeError):
        catalog.add_module(module)


@pytest.mark.parametrize(
    (
        "fingerprint",
        "root_path_is_folder",
        "files",
        "collected_assets",
        "component_assets",
        "expected",
    ),
    [
        pytest.param(
            True,
            True,
            {"relative.css": "x"},
            [],
            ["relative.css"],
            ["relative-8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7.css"],
            id="Fingerprints relative path",
        ),
        pytest.param(
            True,
            True,
            {},
            [],
            [
                "/dist/global.css",
                "http://example.com/a.css",
                "https://example.com/a.css",
            ],
            [
                "/dist/global.css",
                "http://example.com/a.css",
                "https://example.com/a.css",
            ],
            id="Skips fingerprint for global URLs",
        ),
        pytest.param(
            False,
            True,
            {},
            ["foo.css"],
            ["foo.css", "bar.css"],
            ["bar.css"],
            id="Skips already collected",
        ),
        pytest.param(
            True,
            False,
            {"app.css": "x"},
            [],
            ["app.css"],
            ["app.css"],
            id="Skips fingerprint without root path",
        ),
    ],
)
def test_fingerprint_and_gather_unique_assets(
    catalog: jinjax.Catalog,
    folder: Path,
    fingerprint: bool,
    root_path_is_folder: bool,
    files: dict[str, str],
    collected_assets: list[str],
    component_assets: list[str],
    expected: list[str],
):
    catalog.fingerprint = fingerprint
    root_path = folder if root_path_is_folder else None

    for name, content in files.items():
        path = folder / name
        path.write_text(content)
        if fingerprint and root_path_is_folder:
            os.utime(path, (0, 0))

    added = catalog._fingerprint_and_gather_unique_assets(
        root_path,
        collected_assets=collected_assets,
        component_assets=component_assets,
    )
    assert added == expected


@pytest.mark.parametrize(
    ("root_url", "collected_urls", "expected_elements", "expected_rendered"),
    [
        pytest.param(
            "https://cdn.example.com/",
            [
                "local.css",
                "/dist/global.css",
                "http://example.com/remote.css",
                "https://example.com/secure.css",
            ],
            [
                '<link rel="stylesheet" href="https://cdn.example.com/local.css">',
                '<link rel="stylesheet" href="/dist/global.css">',
                '<link rel="stylesheet" href="http://example.com/remote.css">',
                '<link rel="stylesheet" href="https://example.com/secure.css">',
            ],
            {
                "https://cdn.example.com/local.css",
                "/dist/global.css",
                "http://example.com/remote.css",
                "https://example.com/secure.css",
            },
            id="Prepends root_url to relative paths only",
        ),
        pytest.param(
            "/dist/components/",
            ["dup.css", "dup.css"],
            ['<link rel="stylesheet" href="/dist/components/dup.css">'],
            {"/dist/components/dup.css"},
            id="Deduplicates collected urls",
        ),
    ],
)
def test_asset_urls_to_html(
    catalog: jinjax.Catalog,
    root_url: str,
    collected_urls: list[str],
    expected_elements: list[str],
    expected_rendered: set[str],
):
    catalog.root_url = root_url

    elements, rendered = catalog._asset_urls_to_html(
        '<link rel="stylesheet" href="{}">',
        collected_urls=collected_urls,
        rendered_urls=None,
    )

    assert elements == expected_elements
    assert rendered == expected_rendered


def test_format_collected_assets_deduplicates_urls_across_css_and_js(
    catalog: jinjax.Catalog,
):
    catalog.collected_css = ["shared.css"]
    catalog.collected_js = ["shared.css"]

    markup = catalog._format_collected_assets()
    assert markup == '<link rel="stylesheet" href="/static/components/shared.css">'
