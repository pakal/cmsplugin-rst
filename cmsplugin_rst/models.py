# -*- coding: utf-8 -*-
from cms.models.pluginmodel import CMSPlugin
from django.db import models

from . import docutils_plugins  # we register custom docutils directives/roles/...


rst_help_text = '<a target="_blank" href="http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html">Restructuredtext Reference</a>'


class RstPluginModel(CMSPlugin):
    name = models.CharField(max_length=255, blank=True,
                             help_text="Used to identify your plugin instance in page structure.")
    header_level = models.PositiveIntegerField(null=True, blank=True, 
                             help_text="If >0, specifies at which level the headings start.")
    body = models.TextField(help_text=rst_help_text)

    def __unicode__(self):
        return self.name