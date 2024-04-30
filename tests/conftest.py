import pytest

import jinjax


@pytest.fixture()
def folder(tmp_path):
    d = tmp_path / "components"
    d.mkdir()
    return d


@pytest.fixture()
def folder_t(tmp_path):
    d = tmp_path / "templates"
    d.mkdir()
    return d


@pytest.fixture()
def catalog(folder):
    catalog = jinjax.Catalog(auto_reload=False)
    catalog.add_folder(folder)
    return catalog
