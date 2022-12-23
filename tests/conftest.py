import pytest
import jinjax


@pytest.fixture()
def folder(tmp_path):
    d = tmp_path / "components"
    d.mkdir()
    return d


@pytest.fixture()
def catalog(folder):
    catalog = jinjax.Catalog()
    catalog.add_folder(folder)
    return catalog
