import pytest
from cms.api import create_page
from cms.models import Page
from django.conf import settings

from cmsplugin_rst.cms_plugins import restructuredtext


@pytest.fixture
def page(db):
    kwargs = {}
    if settings.CMS_VERSION < (4, 0):
        kwargs["published"] = True
    return create_page("My Page", "page.html", "en", reverse_id="my-page", **kwargs)


def test_cmspage_role_with_menu_title(page):
    html = restructuredtext(":cmspage:`my-page`")
    assert 'href="/en/my-page/"' in html
    assert ">My Page</a>" in html


def test_cmspage_role_with_explicit_name(page):
    html = restructuredtext(":cmspage:`Custom name <my-page>`")
    assert 'href="/en/my-page/"' in html
    assert ">Custom name</a>" in html


def test_cmspage_role_duplicate_reverse_id(page, capsys):
    kwargs = {"published": True} if settings.CMS_VERSION < (4, 0) else {}
    create_page("Other Page", "page.html", "en", **kwargs)
    # create_page() refuses duplicate reverse IDs, but nothing prevents them in DB
    Page.objects.exclude(reverse_id="my-page").update(reverse_id="my-page")
    html = restructuredtext(":cmspage:`my-page`")
    assert "Targeted reverse ID of published page is not unique: &#x27;my-page&#x27;" in html or (
        "Targeted reverse ID of published page is not unique: 'my-page'" in html
    )
    assert "href=\"/en/" not in html
    assert capsys.readouterr().out == ""


@pytest.mark.django_db
def test_cmspage_role_unknown_reverse_id():
    html = restructuredtext(":cmspage:`unknown`")
    assert "doesn&#x27;t exist" in html or "doesn't exist" in html
