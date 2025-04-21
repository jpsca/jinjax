"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
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
