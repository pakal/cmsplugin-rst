try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    BeautifulSoup = None
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.safestring import mark_safe

def get_cfg(key):
    return getattr(settings, 'CMSPLUGIN_RST_%s' % key, [])

def get_postprocessors():
    for postprocessor in get_cfg("POSTPROCESSORS"):
        module_name, callable_name = postprocessor.rsplit('.', 1)
        module = import_module(module_name)
        func = getattr(module, callable_name)
        yield func


def postprocess(html):
    if get_cfg("POSTPROCESSORS") and BeautifulSoup:
        soup = BeautifulSoup(html)
        for postprocessor in get_postprocessors():
            postprocessor(soup)
        return mark_safe(soup.prettify())
    return html