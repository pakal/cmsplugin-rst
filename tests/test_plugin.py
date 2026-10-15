import pytest
from cms.api import add_plugin
from cms.models import Placeholder
from django.core.management import call_command

from cmsplugin_rst.cms_plugins import RstPlugin
from cmsplugin_rst.forms import RstPluginForm
from cmsplugin_rst.models import RstPluginModel


def test_plugin_render():
    instance = RstPluginModel(name="test", body="Title\n=====\n\n**bold**", header_level=2)
    context = RstPlugin().render({"LANGUAGE_CODE": "en"}, instance, None)
    assert "<h2>Title</h2>" in context["content"]
    assert "<strong>bold</strong>" in context["content"]
    assert str(instance) == "test"


def test_plugin_render_with_header_level_0():
    instance = RstPluginModel(name="test", body="Title\n=====", header_level=0)
    context = RstPlugin().render({"LANGUAGE_CODE": "en"}, instance, None)
    assert "<h1>Title</h1>" in context["content"]


@pytest.mark.parametrize("plugin_language, context, is_french", [
    ("fr", {"lang": "en", "LANGUAGE_CODE": "en"}, True),
    ("en", {"lang": "fr", "LANGUAGE_CODE": "fr"}, False),
    ("", {"lang": "fr-ca", "LANGUAGE_CODE": "en"}, True),
    ("", {"LANGUAGE_CODE": "fr"}, True),
    ("", {"LANGUAGE_CODE": "en"}, False),
])
def test_plugin_render_french_typography(plugin_language, context, is_french):
    # the plugin's own language prevails, since django-cms may display fallback-language content
    instance = RstPluginModel(name="test", body="Bonjour !", language=plugin_language)
    content = RstPlugin().render(context, instance, None)["content"]
    assert ("&thinsp;" in content) == is_french


def test_plugin_form():
    form = RstPluginForm(data={"name": "x", "header_level": "", "body": "hello"})
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_plugin_saved_in_placeholder():
    placeholder = Placeholder.objects.create(slot="content")
    plugin = add_plugin(placeholder, RstPlugin, "en", name="saved", body="*hi*")
    plugin = RstPluginModel.objects.get(pk=plugin.pk)
    assert plugin.body == "*hi*"
    assert plugin.header_level is None


@pytest.mark.django_db
def test_no_missing_migrations():
    call_command("makemigrations", "cmsplugin_rst", "--check", "--dry-run", verbosity=0)
