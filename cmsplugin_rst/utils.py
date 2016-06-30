try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    BeautifulSoup = None
from django.conf import settings
from importlib import import_module
from django.utils.safestring import mark_safe


def get_cfg(key, default):
    return getattr(settings, 'CMSPLUGIN_RST_%s' % key, default)

    
def get_postprocessors():
    funcs = []
    for postprocessor in get_cfg("POSTPROCESSORS", []):
        module_name, callable_name = postprocessor.rsplit('.', 1)
        module = import_module(module_name)
        func = getattr(module, callable_name)
        funcs.append(func)
    return funcs


def postprocess(html):
    if BeautifulSoup:
        postprocessors = get_postprocessors()
        if postprocessors:
            soup = BeautifulSoup(html)
            for postprocessor in postprocessors:
                postprocessor(soup)
            return soup.prettify()
    return html