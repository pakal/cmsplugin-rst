# -*- coding: utf-8 -*-
from cms.models.pluginmodel import CMSPlugin
from django.db import models


class RstPluginModel(CMSPlugin):
    name = models.CharField(max_length=255, blank=True)
    body = models.TextField()

    def __unicode__(self):
        return self.name