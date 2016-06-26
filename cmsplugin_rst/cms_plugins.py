# -*- coding: utf-8 -*-
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cmsplugin_rst.forms import RstPluginForm
from cmsplugin_rst.models import RstPluginModel
from cmsplugin_rst.utils import postprocess
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.encoding import force_text, force_bytes
from django.utils.safestring import mark_safe
from django import template


def restructuredtext(value):
    try:
        from docutils.core import publish_parts
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError("Error in 'restructuredtext' filter: The Python docutils library isn't installed.")
        return force_text(value)
    else:
        docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})
        parts = publish_parts(source=force_bytes(value), writer_name="html4css1", settings_overrides=docutils_settings)
        return mark_safe(force_text(parts["fragment"]))


class RstPlugin(CMSPluginBase):
    name = _('Restructured Text Plugin')
    render_template = 'cms/content.html'
    model = RstPluginModel
    form = RstPluginForm

    def render(self, context, instance, placeholder):
        rst = getattr(settings, "RESTRUCTUREDTEXT_INITIALIZER", "") + "\n"
        rst += instance.body
        rst = rst.replace("{{ MEDIA_URL }}", settings.MEDIA_URL)
        rst = rst.replace("{{ STATIC_URL }}", settings.STATIC_URL)
        context.update({'content': postprocess(restructuredtext(rst))})
        return context

plugin_pool.register_plugin(RstPlugin)
