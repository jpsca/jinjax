import jinja2
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


@pytest.fixture()
def autoescaped_catalog(folder):
    jinja_env = jinja2.Environment(autoescape=True)
    catalog = jinjax.Catalog(auto_reload=False, jinja_env=jinja_env)
    catalog.add_folder(folder)
    return catalog
