import pytest

from cmsplugin_rst.cms_plugins import render_rich_text, restructuredtext
from cmsplugin_rst.docutils_plugins import is_safe_url


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "HTTPS://example.com/a:b",
        "mailto:someone@example.com",
        "tel:+33123456789",
        "ftp://example.com/file",
        "/en/some/page/",
        "page.html",
        "page.html#anchor:with:colons",
        "#anchor",
        "?query=a:b",
        "//example.com/protocol-relative",
        "",
    ],
)
def test_is_safe_url_ok(url):
    assert is_safe_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "JaVaScRiPt:alert(1)",
        " javascript:alert(1)",
        "\x01javascript:alert(1)",
        "java\tscript:alert(1)",
        "java\nscript:alert(1)",
        "vbscript:msgbox(1)",
        "data:text/html,<script>alert(1)</script>",
        "file:///etc/passwd",
        "unknown-scheme:foo",
    ],
)
def test_is_safe_url_ko(url):
    assert not is_safe_url(url)


def test_is_safe_url_custom_schemes(settings):
    assert is_safe_url("http://example.com", allowed_schemes=["HTTP"])
    assert not is_safe_url("https://example.com", allowed_schemes=["http"])
    settings.CMSPLUGIN_RST_ALLOWED_URL_SCHEMES = ["https"]
    assert not is_safe_url("http://example.com")
    assert is_safe_url("https://example.com")


@pytest.mark.parametrize(
    "source",
    [
        "`click <javascript:alert(1)>`_",
        "`click <JAVASCRIPT:alert(1)>`__",
        "click_\n\n.. _click: javascript:alert(1)",
        # docutils joins the lines of a target URL
        "click_\n\n.. _click: java\n   script:alert(1)",
        "click__\n\n__ javascript:alert(1)",
        "click_\n\n.. _click: other_\n.. _other: javascript:alert(1)",
        "`click <data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==>`_",
    ],
)
def test_unsafe_links_are_removed(source):
    html = restructuredtext(source)
    assert "click" in html
    assert "<a " not in html
    assert "href" not in html
    assert "Unsafe link URL removed" in html
    # the link is removed even if warnings are not displayed
    html = restructuredtext(source, report_level=5)
    assert "click" in html
    assert "href" not in html
    assert "system-message" not in html


@pytest.mark.parametrize(
    "source",
    [
        ".. image:: javascript:alert(1)\n   :alt: my picture",
        ".. image:: javascript:alert(1).svg\n   :alt: my picture",  # svg images use <object data=...>
        ".. figure:: javascript:alert(1)\n   :alt: my picture\n\n   Caption",
        ".. |pic| image:: javascript:alert(1)\n   :alt: my picture\n\nText |pic|",
    ],
)
def test_unsafe_images_are_removed(source):
    html = restructuredtext(source)
    assert "my picture" in html
    assert "<img" not in html
    assert "<object" not in html
    assert "javascript:alert(1)\"" not in html
    assert "Unsafe image URL removed" in html


def test_unsafe_image_target_is_removed():
    html = restructuredtext(".. image:: /static/pic.png\n   :alt: my picture\n   :target: javascript:alert(1)")
    assert '<img alt="my picture" src="/static/pic.png" />' in html
    assert "href" not in html
    assert "Unsafe link URL removed" in html


def test_safe_links_and_images_are_kept():
    html = restructuredtext(
        "`a <https://example.com/>`_, `b <mailto:x@example.com>`_, `c </en/page/>`_, d_, e__\n\n"
        ".. _d: http://example.com/d\n"
        "__ #local\n\n"
        ".. image:: /static/pic.png\n   :target: https://example.com/target\n\n"
        "Section\n=======\n\nSee Section_ and https://example.com/standalone."
    )
    for href in [
        "https://example.com/",
        "mailto:x&#64;example.com",  # docutils obfuscates email addresses
        "/en/page/",
        "http://example.com/d",
        "#local",
        "https://example.com/target",
        "#section",
        "https://example.com/standalone",
    ]:
        assert 'href="%s"' % href in html
    assert 'src="/static/pic.png"' in html
    assert "Unsafe" not in html


def test_allowed_url_schemes_setting(settings):
    settings.CMSPLUGIN_RST_ALLOWED_URL_SCHEMES = ["https"]
    html = render_rich_text("`a <https://example.com/>`_ and `b <http://example.com/>`_")
    assert 'href="https://example.com/"' in html
    assert 'href="http://example.com/"' not in html
    assert "Unsafe link URL removed: &#x27;http://example.com/&#x27;" in html or (
        "Unsafe link URL removed: 'http://example.com/'" in html
    )
