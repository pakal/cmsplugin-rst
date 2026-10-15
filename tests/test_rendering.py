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
