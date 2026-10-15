import pytest
from cms.api import create_page
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


@pytest.mark.django_db
def test_cmspage_role_unknown_reverse_id():
    html = restructuredtext(":cmspage:`unknown`")
    assert "doesn&#x27;t exist" in html or "doesn't exist" in html
