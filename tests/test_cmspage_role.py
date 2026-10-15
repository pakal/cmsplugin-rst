import datetime
import html as html_lib

import pytest
from cms.api import create_page
from cms.models import Page
from django.conf import settings
from django.utils import timezone

from cmsplugin_rst.cms_plugins import restructuredtext

LEGACY_CMS = settings.CMS_VERSION < (4, 0)

legacy_cms_only = pytest.mark.skipif(not LEGACY_CMS, reason="django-cms<4 publication workflow")
versioning_only = pytest.mark.skipif(not settings.USE_VERSIONING, reason="djangocms-versioning not installed")


@pytest.fixture
def make_page(db, admin_user):
    """Create a page, published unless told otherwise, whatever the django-cms publication workflow."""

    def _make_page(title, reverse_id=None, published=True, **kwargs):
        if LEGACY_CMS:
            kwargs["published"] = published
        page = create_page(title, "page.html", "en", reverse_id=reverse_id, created_by=admin_user, **kwargs)
        if settings.USE_VERSIONING and published:
            publish_version(page, admin_user)
        return page

    return _make_page


def get_version(page):
    from cms.models import PageContent
    from djangocms_versioning.models import Version

    content = PageContent.admin_manager.get(page=page, language="en")
    return Version.objects.get_for_content(content)


def publish_version(page, user):
    get_version(page).publish(user)


@pytest.fixture
def page(make_page):
    return make_page("My Page", reverse_id="my-page")


def assert_link_error(html, message):
    assert "<a class=\"reference" not in html
    assert message + ": 'my-page'" in html_lib.unescape(html)


def test_cmspage_role_with_menu_title(page):
    html = restructuredtext(":cmspage:`my-page`")
    assert '<a class="reference external" href="/en/my-page/">My Page</a>' in html


def test_cmspage_role_with_explicit_name(page):
    html = restructuredtext(":cmspage:`Custom name <my-page>`")
    assert '<a class="reference external" href="/en/my-page/">Custom name</a>' in html


def test_cmspage_role_with_class_option(page):
    html = restructuredtext(".. role:: fancypage(cmspage)\n   :class: fancy\n\n:fancypage:`my-page`")
    assert '<a class="reference external fancy" href="/en/my-page/">My Page</a>' in html


def test_cmspage_role_duplicate_reverse_id(page, make_page, capsys):
    make_page("Other Page")
    # create_page() refuses duplicate reverse IDs, but nothing prevents them in DB
    Page.objects.exclude(reverse_id="my-page").update(reverse_id="my-page")
    html = restructuredtext(":cmspage:`my-page`")
    assert_link_error(html, "Targeted reverse ID of published page is not unique")
    assert capsys.readouterr().out == ""


def test_cmspage_role_multisite(page, make_page, settings):
    from django.contrib.sites.models import Site

    other_site = Site.objects.create(domain="other.example.com", name="other")
    make_page("Other Site Page", reverse_id="my-page", site=other_site)

    html = restructuredtext(":cmspage:`my-page`")
    assert '<a class="reference external" href="/en/my-page/">My Page</a>' in html

    settings.SITE_ID = other_site.pk
    html = restructuredtext(":cmspage:`my-page`")
    assert '<a class="reference external" href="/en/other-site-page/">Other Site Page</a>' in html


@pytest.mark.django_db
def test_cmspage_role_unknown_reverse_id():
    html = restructuredtext(":cmspage:`my-page`")
    assert_link_error(html, "Targeted reverse ID of published page doesn't exist")


@legacy_cms_only
def test_cmspage_role_unpublished_page_legacy(page):
    page.unpublish("en")
    html = restructuredtext(":cmspage:`my-page`")
    assert_link_error(html, "Targeted reverse ID of published page doesn't exist")


@legacy_cms_only
def test_cmspage_role_never_published_page_legacy(make_page):
    make_page("My Page", reverse_id="my-page", published=False)
    html = restructuredtext(":cmspage:`my-page`")
    assert_link_error(html, "Targeted reverse ID of published page doesn't exist")


@legacy_cms_only
def test_cmspage_role_expired_page_legacy(make_page):
    make_page("My Page", reverse_id="my-page", publication_end_date=timezone.now() - datetime.timedelta(days=1))
    html = restructuredtext(":cmspage:`my-page`")
    assert_link_error(html, "Targeted reverse ID of published page doesn't exist")


@versioning_only
def test_cmspage_role_draft_page_versioning(make_page, admin_user):
    page = make_page("My Page", reverse_id="my-page", published=False)
    html = restructuredtext(":cmspage:`my-page`")
    assert_link_error(html, "Targeted reverse ID of published page doesn't exist")

    publish_version(page, admin_user)
    html = restructuredtext(":cmspage:`my-page`")
    assert '<a class="reference external" href="/en/my-page/">My Page</a>' in html

    get_version(page).unpublish(admin_user)
    html = restructuredtext(":cmspage:`my-page`")
    assert_link_error(html, "Targeted reverse ID of published page doesn't exist")
