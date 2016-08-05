
import re
from importlib import import_module

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    BeautifulSoup = None
from django.conf import settings
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
            return unicode(soup)  # NO prettify(), breaks spacing of tags
    return html
    

# BORROWED FROM https://github.com/Chimrod/typogrify
def french_insecable(text):
    """Replace the space between each double sign punctuation by a thin
    non-breaking space.

    This conform with the french typographic rules.

    >>> french_insecable('Foo !')
    u'Foo<span style="white-space:nowrap">&thinsp;</span>!'

    >>> french_insecable('Foo ?')
    u'Foo<span style="white-space:nowrap">&thinsp;</span>?'

    >>> french_insecable('Foo : bar')
    u'Foo<span style="white-space:nowrap">&thinsp;</span>: bar'

    >>> french_insecable('Foo ; bar')
    u'Foo<span style="white-space:nowrap">&thinsp;</span>; bar'

    >>> french_insecable(u'\xab bar \xbb')
    u'\\xab<span style="white-space:nowrap">&thinsp;</span>bar<span style="white-space:nowrap">&thinsp;</span>\\xbb'

    >>> french_insecable('123 456')
    u'123<span style="white-space:nowrap">&thinsp;</span>456'

    >>> french_insecable('123 %')
    u'123<span style="white-space:nowrap">&thinsp;</span>%'

    Space inside attributes should be preserved :

    >>> french_insecable('<a title="foo !">')
    '<a title="foo !">'
    """

    tag_pattern = '</?\w+((\s+\w+(\s*=\s*(?:".*?"|\'.*?\'|[^\'">\s]+))?)+\s*|\s*)/?>'
    intra_tag_finder = re.compile(r'(?P<prefix>(%s)?)(?P<text>([^<]*))(?P<suffix>(%s)?)' % (tag_pattern, tag_pattern))

    nnbsp = u'<span style="white-space:nowrap">&thinsp;</span>'
    space_finder = re.compile(r"""(?:
                            (\w\s[:;!\?\xbb])|       # Group 1, space before punctuation
                            ([\xab]\s\w)|
                            ([0-9]\s[0-9])|
                            ([0-9]\s\%)
                            )""", re.VERBOSE)

    def _insecable_wrapper(groups):
        """This is necessary to keep dotted cap strings to pick up extra spaces"""
        def substitute(matchobj):
            return matchobj.group(0).replace(" ", nnbsp)

        prefix = groups.group('prefix') or ''
        text = space_finder.sub(substitute, groups.group('text'))
        suffix = groups.group('suffix') or ''
        return prefix + text + suffix

    output = intra_tag_finder.sub(_insecable_wrapper, text)
    return output