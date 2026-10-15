import importlib
import sys

import pytest

from cmsplugin_rst import utils


def uppercase_paragraphs(soup):
    for p in soup.find_all("p"):
        p.string = p.get_text().upper()


def add_class(soup):
    soup.p["class"] = "processed"


def test_get_cfg(settings):
    assert utils.get_cfg("UNKNOWN_SETTING", "default") == "default"
    settings.CMSPLUGIN_RST_UNKNOWN_SETTING = "value"
    assert utils.get_cfg("UNKNOWN_SETTING", "default") == "value"


def test_get_postprocessors(settings):
    assert utils.get_postprocessors() == []
    settings.CMSPLUGIN_RST_POSTPROCESSORS = ["tests.test_utils.uppercase_paragraphs", "tests.test_utils.add_class"]
    assert utils.get_postprocessors() == [uppercase_paragraphs, add_class]


def test_get_postprocessors_wrong_path(settings):
    settings.CMSPLUGIN_RST_POSTPROCESSORS = ["tests.test_utils.unknown_function"]
    with pytest.raises(AttributeError):
        utils.get_postprocessors()


def test_postprocess_chains_postprocessors(settings):
    pytest.importorskip("bs4")
    html = "<p>hello &amp; <b>bye</b></p>"
    assert utils.postprocess(html) == html  # no postprocessors
    settings.CMSPLUGIN_RST_POSTPROCESSORS = ["tests.test_utils.uppercase_paragraphs", "tests.test_utils.add_class"]
    assert utils.postprocess(html) == '<p class="processed">HELLO &amp; BYE</p>'


def test_postprocess_without_beautifulsoup(settings, monkeypatch):
    monkeypatch.setattr(utils, "BeautifulSoup", None)
    settings.CMSPLUGIN_RST_POSTPROCESSORS = ["tests.test_utils.add_class"]
    html = "<p>hello</p>"
    assert utils.postprocess(html) == html


def test_beautifulsoup_is_optional(monkeypatch):
    monkeypatch.setitem(sys.modules, "bs4", None)  # makes "import bs4" fail
    try:
        importlib.reload(utils)
        assert utils.BeautifulSoup is None
    finally:
        monkeypatch.undo()
        importlib.reload(utils)
    assert utils.BeautifulSoup is not None
