import subprocess
import sys

import pytest
from django.contrib.staticfiles import finders

from cmsplugin_rst.cms_plugins import restructuredtext
from cmsplugin_rst.highlighting import get_pygments_css

pytest.importorskip("pygments")

CODE_BLOCK = """\
.. code:: python

   def f(x):
       return "<b>"
"""


def test_code_directive_is_highlighted():
    html = restructuredtext(CODE_BLOCK)
    assert '<pre class="code python literal-block">' in html
    assert '<span class="keyword">def</span>' in html
    assert '<span class="name function">f</span>' in html
    assert "&quot;&lt;b&gt;&quot;" in html  # code is properly escaped
    assert "system-message" not in html


def test_code_role_is_highlighted():
    html = restructuredtext(".. role:: py(code)\n   :language: python\n\n:py:`import os`\n")
    assert '<code class="py python"><span class="keyword namespace">import</span>' in html


def test_unknown_language_is_reported():
    html = restructuredtext(".. code:: notalanguage\n\n   foo\n")
    assert "No Pygments lexer found" in html


@pytest.mark.parametrize(
    "syntax_highlight, expected",
    [
        ("short", '<span class="k">def</span>'),
        ("none", '<pre class="code python literal-block">\ndef f(x):'),
    ],
)
def test_syntax_highlight_setting(monkeypatch, syntax_highlight, expected):
    from cmsplugin_rst import cms_plugins

    monkeypatch.setitem(cms_plugins.DOCUTILS_RENDERER_SETTINGS, "syntax_highlight", syntax_highlight)
    assert expected in restructuredtext(CODE_BLOCK)


def test_without_pygments(monkeypatch):
    from docutils.utils import code_analyzer

    monkeypatch.setattr(code_analyzer, "with_pygments", False)
    html = restructuredtext(CODE_BLOCK)
    assert "Pygments package not found" in html
    html = restructuredtext(CODE_BLOCK, report_level=3)
    assert '<pre class="code python literal-block">\ndef f(x):' in html
    assert "<span" not in html


def test_long_css():
    css = get_pygments_css()
    assert css.startswith("/* Pygments style 'default', for docutils long token names */\n")
    assert "pre.code { background-color: #f8f8f8; }" in css
    assert "pre.code .keyword, code .keyword { color: #008000; font-weight: bold; }" in css
    # child tokens must reset the properties they don't inherit from parent tokens (eg. "nobold")
    assert "pre.code .keyword.pseudo, code .keyword.pseudo { font-weight: normal; }" in css
    assert "pre.code .name.function, code .name.function { color: #0000FF; }" in css
    # pygments-specific short class names are not used
    assert ".k " not in css


def test_long_css_with_container_styles():
    css = get_pygments_css("monokai")
    assert "pre.code, code { color: #f8f8f2; }" in css  # Token.Text is unstyled in docutils


def test_short_css():
    css = get_pygments_css(tokennames="short")
    assert "pre.code .k, code .k { color: #008000; font-weight: bold }" in css


def test_css_wrong_tokennames():
    with pytest.raises(ValueError):
        get_pygments_css(tokennames="none")


def test_css_command_line():
    output = subprocess.check_output(
        [sys.executable, "-m", "cmsplugin_rst.highlighting", "monokai"], text=True
    )
    assert output == get_pygments_css("monokai")


def test_bundled_stylesheet():
    path = finders.find("cmsplugin_rst/pygments.css")
    assert path
    with open(path, encoding="utf8") as f:
        css = f.read()
    assert css.startswith("/* Pygments style 'default', for docutils long token names */\n")
    assert "pre.code .keyword, code .keyword {" in css
