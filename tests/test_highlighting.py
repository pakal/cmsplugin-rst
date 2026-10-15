import re
import subprocess
import sys

import pytest
from django.contrib.staticfiles import finders

from cmsplugin_rst.cms_plugins import restructuredtext
from cmsplugin_rst.highlighting import CSS_PROPERTIES, _get_long_classes, get_pygments_css

pytest.importorskip("pygments")

from pygments.styles import get_all_styles, get_style_by_name  # noqa: E402
from pygments.token import STANDARD_TYPES  # noqa: E402

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
def test_syntax_highlight_setting(settings, syntax_highlight, expected):
    settings.CMSPLUGIN_RST_SETTINGS_OVERRIDES = {"syntax_highlight": syntax_highlight}
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
    assert "code:has(> span) { background-color: #f8f8f8; }" in css
    assert "pre.code .keyword, code .keyword { color: #008000; font-weight: bold; }" in css
    # child tokens must reset the properties they don't inherit from parent tokens (eg. "nobold")
    assert "pre.code .keyword.pseudo, code .keyword.pseudo { font-weight: normal; }" in css
    assert "pre.code .name.function, code .name.function { color: #0000FF; }" in css
    # pygments-specific short class names are not used
    assert ".k " not in css


def test_long_css_with_container_styles():
    css = get_pygments_css("monokai")
    # Token.Text is unstyled in docutils, so its color goes to containers, along with the background
    assert "pre.code { background-color: #272822; color: #f8f8f2; }" in css
    assert "code:has(> span) { background-color: #272822; color: #f8f8f2; }" in css
    # plain inline code (without highlighted tokens) must not be styled
    assert_only_scoped_selectors(css)


def assert_only_scoped_selectors(css):
    for line in css.splitlines()[1:]:  # skip header comment
        for selector in line.split("{")[0].split(","):
            selector = selector.strip()
            assert selector.startswith(("pre.code", "code:has(> span)", "code .")), selector


def test_short_css():
    css = get_pygments_css(tokennames="short")
    assert css.startswith("/* Pygments style 'default', for docutils short token names */\n")
    assert "pre.code { background-color: #f8f8f8; }" in css
    assert "pre.code .k, code .k { color: #008000; font-weight: bold; }" in css
    # each element has a single short class, so its rule has all its (inherited) properties
    assert "pre.code .kp, code .kp { color: #008000; }" in css
    assert "pre.code .nf, code .nf { color: #0000FF; }" in css
    # no global rules for all <pre> elements, nor for line numbers tables, like in Pygments' stylesheets
    assert_only_scoped_selectors(css)
    assert "linenos" not in css


def test_short_css_with_container_styles():
    css = get_pygments_css("monokai", tokennames="short")
    assert "pre.code { background-color: #272822; color: #f8f8f2; }" in css
    assert "code:has(> span) { background-color: #272822; color: #f8f8f2; }" in css
    assert_only_scoped_selectors(css)


def test_short_css_matches_rendered_classes(settings):
    settings.CMSPLUGIN_RST_SETTINGS_OVERRIDES = {"syntax_highlight": "short"}
    html = restructuredtext(CODE_BLOCK)
    css = get_pygments_css(tokennames="short")
    for cls in ["k", "nf", "s2"]:
        assert '<span class="%s">' % cls in html
        assert "pre.code .%s, code .%s {" % (cls, cls) in css


@pytest.mark.parametrize("tokennames", ["long", "short"])
def test_css_style_without_background(monkeypatch, tokennames):
    import pygments.styles
    from pygments.style import Style
    from pygments.token import Keyword

    class MinimalStyle(Style):
        background_color = None
        styles = {Keyword: "bold"}

    monkeypatch.setattr(pygments.styles, "get_style_by_name", lambda name: MinimalStyle)
    css = get_pygments_css("minimal", tokennames=tokennames)
    lines = css.splitlines()
    assert lines[:3] == [
        "/* Pygments style 'minimal', for docutils %s token names */" % tokennames,
        "pre.code .ln, code .ln { color: #999999; user-select: none; }",
        "pre.code .keyword, code .keyword { font-weight: bold; }"
        if tokennames == "long"
        else "pre.code .k, code .k { font-weight: bold; }",
    ]
    if tokennames == "long":
        assert len(lines) == 3  # sub-tokens inherit via the CSS cascade
    else:
        assert "pre.code .kp, code .kp { font-weight: bold; }" in lines  # sub-tokens need all properties
    assert "pre.code {" not in css
    assert "code:has(> span) {" not in css


def test_css_wrong_tokennames():
    with pytest.raises(ValueError):
        get_pygments_css(tokennames="none")


def test_css_command_line():
    output = subprocess.check_output(
        [sys.executable, "-m", "cmsplugin_rst.highlighting", "monokai"], text=True
    )
    assert output == get_pygments_css("monokai")


def test_css_main(monkeypatch, capsys):
    import runpy

    monkeypatch.setattr(sys, "argv", ["highlighting", "monokai", "short"])
    runpy.run_module("cmsplugin_rst.highlighting", run_name="__main__")
    assert capsys.readouterr().out == get_pygments_css("monokai", "short")


def test_bundled_stylesheet():
    path = finders.find("cmsplugin_rst/pygments.css")
    assert path
    with open(path, encoding="utf8") as f:
        css = f.read()
    assert css.startswith("/* Pygments style 'default', for docutils long token names */\n")
    assert "pre.code .keyword, code .keyword {" in css
    assert css == get_pygments_css()  # up to date


def _get_long_css_cascade_styles(css, classes):
    """Return the CSS properties of an element with the given classes (among highlighted
    tokens), by applying the matching token rules of `css` in the order of the CSS cascade."""
    matching_rules = []
    for index, line in enumerate(css.splitlines()):
        match = re.match(r"pre\.code ((?:\.[\w-]+)+), code \1 \{ (.*); \}$", line)
        if match and match.group(1) != ".ln":
            rule_classes = set(match.group(1).strip(".").split("."))
            if rule_classes <= set(classes):
                matching_rules.append((len(rule_classes), index, match.group(2)))  # specificity, then order
    properties = {}
    for _, _, declarations in sorted(matching_rules):
        properties.update(declaration.split(": ", 1) for declaration in declarations.split("; "))
    return properties


@pytest.mark.parametrize("style_name", sorted(get_all_styles()))
def test_long_css_cascade(style_name):
    # each token must get exactly its own properties, even though its element also matches the rules
    # of its parent tokens, and of unrelated tokens with a subset of its classes (eg. "name variable class"
    # matches ".name.class")
    css = get_pygments_css(style_name)
    style = get_style_by_name(style_name)
    # the color of unstyled tokens is set on the container, and inherited by other tokens
    match = re.search(r"^pre\.code \{ (?:.*; )?color: (#\w+)", css, re.MULTILINE)
    container_color = match.group(1) if match else "inherit"
    standard_classes = {frozenset(_get_long_classes(ttype)) for ttype in STANDARD_TYPES}
    for ttype, ndef in style:
        classes = _get_long_classes(ttype)
        if not classes:
            continue  # unstyled tokens are styled via their container
        if ttype not in STANDARD_TYPES and frozenset(classes) in standard_classes:
            continue  # eg. "Comment.PreProc" of gruvbox, which is not emitted by lexers, unlike "Comment.Preproc"
        properties = _get_long_css_cascade_styles(css, classes)
        for key, css_property, on_value, off_value in CSS_PROPERTIES:
            value = ndef[key]
            expected = (on_value % value if "%" in on_value else on_value) if value else off_value
            actual = properties.get(css_property, off_value)
            if css_property == "color":
                expected, actual = [container_color if v == "inherit" else v for v in (expected, actual)]
            assert actual == expected, (ttype, css_property)
