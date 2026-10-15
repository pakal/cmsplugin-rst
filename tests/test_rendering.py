import pytest

from cmsplugin_rst.cms_plugins import render_rich_text, restructuredtext


def test_basic_rendering():
    html = restructuredtext("Hello *world*")
    assert "<p>Hello <em>world</em></p>" in html


def test_lone_title_is_kept_and_header_level():
    html = restructuredtext("My Title\n========\n\nSome text")
    assert "<h1>My Title</h1>" in html
    html = restructuredtext("My Title\n========\n\nSome text", header_level=3)
    assert "<h3>My Title</h3>" in html


@pytest.mark.parametrize("header_level", [0, -1])
def test_header_level_below_1_is_ignored(header_level):
    html = restructuredtext("My Title\n========\n\nSome text", header_level=header_level)
    assert "<h1>My Title</h1>" in html


def test_header_level_above_6_is_capped():
    html = restructuredtext("My Title\n========\n\nSome text", header_level=7)
    assert '<h6 class="h7">My Title</h6>' in html


@pytest.mark.parametrize(
    "source",
    [
        ".. raw:: html\n\n   <script>alert(1)</script>\n",
        ".. include:: /etc/passwd\n",
    ],
)
def test_insecure_directives_are_disabled(source):
    html = restructuredtext(source, report_level=5)
    assert "<script>" not in html
    assert "root:" not in html


def test_html_in_source_is_escaped():
    html = restructuredtext("<script>alert(1)</script> & co")
    assert "<script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt; &amp; co" in html


def test_settings_overrides(settings):
    source = 'Title\n=====\n\n"quoted"'
    html = restructuredtext(source)
    assert "<h1>Title</h1>" in html
    assert "&quot;quoted&quot;" in html
    settings.CMSPLUGIN_RST_SETTINGS_OVERRIDES = {"initial_header_level": 2, "smart_quotes": True}
    html = restructuredtext(source)
    assert "<h2>Title</h2>" in html
    assert "“quoted”" in html
    # explicit arguments have priority over global settings
    assert "<h4>Title</h4>" in restructuredtext(source, header_level=4)
    # overrides must not leak into the defaults
    settings.CMSPLUGIN_RST_SETTINGS_OVERRIDES = {}
    assert "<h1>Title</h1>" in restructuredtext(source)


def test_report_level():
    source = "`unclosed"
    assert "system-message" in restructuredtext(source)
    assert "system-message" not in restructuredtext(source, report_level=5)


def test_render_rich_text_replacements():
    html = render_rich_text("Image at {{ STATIC_URL }}img.png{{ BR }}x{{ NBSP }}y")
    assert "/static/img.png<br/>x&nbsp;y" in html


def test_render_rich_text_prefix_suffix(settings):
    settings.CMSPLUGIN_RST_CONTENT_PREFIX = "*PREFIX*"
    settings.CMSPLUGIN_RST_CONTENT_SUFFIX = "*SUFFIX*"
    html = render_rich_text("body")
    assert html.index("<em>PREFIX</em>") < html.index("body") < html.index("<em>SUFFIX</em>")
    # prefix and suffix are separate paragraphs, not merged with the content
    assert "<p><em>PREFIX</em></p>\n<p>body</p>\n<p><em>SUFFIX</em></p>" in html


def test_render_rich_text_prefix_with_explicit_markup(settings):
    settings.CMSPLUGIN_RST_CONTENT_PREFIX = ".. |hello| replace:: Hello"
    settings.CMSPLUGIN_RST_CONTENT_SUFFIX = ".. _target: https://example.com"
    html = render_rich_text("|hello| world, see target_")
    assert "<p>Hello world, see <a" in html
    assert 'href="https://example.com"' in html
    assert "system-message" not in html


def test_render_rich_text_french_typography():
    assert "&thinsp;" not in render_rich_text("Bonjour !", language_code="en")
    assert "Bonjour<span style=\"white-space:nowrap\">&thinsp;</span>!" in render_rich_text(
        "Bonjour !", language_code="fr-FR"
    )


def add_stuffs_to_soup(soup):
    soup.append("[postprocessed]")


def test_postprocessors(settings):
    pytest.importorskip("bs4")
    assert not render_rich_text("text").endswith("[postprocessed]")
    settings.CMSPLUGIN_RST_POSTPROCESSORS = ["tests.test_rendering.add_stuffs_to_soup"]
    assert render_rich_text("text").endswith("[postprocessed]")
