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

from .utils import get_cfg, french_insecable


DOCUTILS_RENDERER_SETTINGS = {
    "initial_header_level": 1,
    # important, to have even lone titles stay in the html fragment:
    "doctitle_xform": False, 
    # we also disable the promotion of lone subsection title to a subtitle:
    "sectsubtitle_xform": False, 
    'file_insertion_enabled': False,  # SECURITY MEASURE (file hacking)
    'raw_enabled': False, # SECURITY MEASURE (script tag)
    'report_level': 2,  # report warnings and above, by default
}
DOCUTILS_RENDERER_SETTINGS.update(get_cfg("SETTINGS_OVERRIDES", {}))


def restructuredtext(value, header_level=None, report_level=None):
    try:
        from docutils.core import publish_parts
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError("Error in 'restructuredtext' filter: The Python docutils library isn't installed.")
        return force_text(value)
    else:
        settings_overrides = DOCUTILS_RENDERER_SETTINGS.copy()
        if header_level is not None:  # starts from 1
            settings_overrides["initial_header_level"] = header_level
        if report_level is not None:  # starts from 1 too
            settings_overrides["report_level"] = report_level
        parts = publish_parts(source=force_bytes(value), 
                              writer_name=get_cfg("WRITER_NAME", "html4css1"), 
                              settings_overrides=settings_overrides)
        return force_text(parts["html_body"])


def render_rich_text(rst_string, language_code="", header_level=None, report_level=None):
    rst = get_cfg("CONTENT_PREFIX", "") + "\n"
    rst += rst_string
    rst += "\n" + get_cfg("CONTENT_SUFFIX", "") 
    rst = rst.replace("{{ MEDIA_URL }}", settings.MEDIA_URL)
    rst = rst.replace("{{ STATIC_URL }}", settings.STATIC_URL)
    content = restructuredtext(rst, header_level=header_level, report_level=report_level)
    content = content.replace("{{ BR }}", "<br/>")
    content = content.replace("{{ NBSP }}", "&nbsp;")
    if language_code.lower().startswith("fr"):  # ONLY french codes should start like that
        content = french_insecable(content)
    content = postprocess(content)
    return content


class RstPlugin(CMSPluginBase):
    name = _('Restructured Text Plugin')
    render_template = 'cms/content.html'
    model = RstPluginModel
    form = RstPluginForm

    def render(self, context, instance, placeholder):
        # we lookup cms page language, else i18n language
        language_code = context.get("lang", "") or context.get("LANGUAGE_CODE", "")
        content = render_rich_text(instance.body, 
                                   language_code=language_code, 
                                   header_level=instance.header_level,
                                   report_level=None)  # not set ATM
        context.update({'content': mark_safe(content)})
        return context

plugin_pool.register_plugin(RstPlugin)
