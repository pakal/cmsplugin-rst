
import functools
import re
from docutils import nodes, utils
from docutils.parsers.rst.roles import register_local_role
from docutils.transforms import Transform

from .utils import get_cfg


DEFAULT_ALLOWED_URL_SCHEMES = ("http", "https", "ftp", "ftps", "mailto", "tel")

# Browsers ignore ASCII control characters and spaces in URL schemes (eg. "java\tscript:")
_IGNORED_URL_CHARS = re.compile(r"[\x00-\x20\x7f]+")
_URL_SCHEME = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.\-]*):")


def is_safe_url(url, allowed_schemes=None):
    """Return True if `url` is relative, or uses one of the allowed schemes (case-insensitive)."""
    if allowed_schemes is None:
        allowed_schemes = get_cfg("ALLOWED_URL_SCHEMES", DEFAULT_ALLOWED_URL_SCHEMES)
    match = _URL_SCHEME.match(_IGNORED_URL_CHARS.sub("", url))
    if match is None:
        return True  # relative URL
    return match.group(1).lower() in {scheme.lower() for scheme in allowed_schemes}


class UnsafeURLsRemover(Transform):
    """Neutralize links and images whose URL scheme is not allowed (eg. "javascript:").

    Disabling the "raw" directive isn't sufficient to prevent script injection, since
    standard hyperlinks accept any URL. Unsafe links are replaced by their text,
    and unsafe images by their alternate text, with a warning.
    """

    default_priority = 845  # after all references are resolved, before system messages are gathered

    def apply(self):
        for node in list(self.document.findall(nodes.reference)):
            uri = node.get("refuri")
            if uri is not None and not is_safe_url(uri):
                self.document.reporter.warning("Unsafe link URL removed: %r" % uri, base_node=node)
                node.replace_self(nodes.inline(node.rawsource, "", *node.children))
        for node in list(self.document.findall(nodes.image)):
            uri = node.get("uri", "")
            if not is_safe_url(uri):
                self.document.reporter.warning("Unsafe image URL removed: %r" % uri, base_node=node)
                node.replace_self(nodes.inline("", node.get("alt", "")))


@functools.lru_cache(maxsize=None)
def get_safe_writer_class(writer_class):
    """Return a subclass of the docutils `writer_class`, which applies UnsafeURLsRemover."""

    class SafeWriter(writer_class):
        def get_transforms(self):
            return super().get_transforms() + [UnsafeURLsRemover]

    return SafeWriter


def djangocms_link_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """Role to link to a djangocms page, using its reverse-ID.
    Allows the syntax "Name <ref>" like for standard RST links.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.  Both are allowed to be
    empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    from cms.models import Page  # LAZY loading, else troubles on setup
    from django.core.exceptions import FieldDoesNotExist

    result = re.match(r"^(.+) \<(.+)\>$", text)
    #print (">> djangocms_link_role regex result is", result, result.groups() if result else None)
    if result:
        name, reverse_id = result.groups()
    else:
        name = None
        reverse_id = text

    try:
        # beware: on django-cms<4, draft and published versions of a page share the same
        # reverse-ID, so publisher_is_draft must disambiguate them. django-cms>=4 dropped
        # that field entirely (draft/publish is now versioned PageContent, not separate
        # Page rows), so only add it to the lookup when the installed cms still has it.
        page_lookup = {'reverse_id': reverse_id}
        try:
            Page._meta.get_field('publisher_is_draft')
        except FieldDoesNotExist:
            pass
        else:
            page_lookup['publisher_is_draft'] = False
        # reverse-IDs are only unique per site
        page = Page.objects.on_site().get(**page_lookup)
    except Page.DoesNotExist:
        msg = inliner.reporter.error("Targeted reverse ID of published page doesn't exist: %r" % reverse_id, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    except Page.MultipleObjectsReturned:
        msg = inliner.reporter.error("Targeted reverse ID of published page is not unique: %r" % reverse_id, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    else:
        if name is None:
            name = page.get_menu_title()
        ref = page.get_absolute_url()
        options = dict(options or {})
        if 'class' in options:  # like docutils' set_classes(), deprecated since 0.22
            options['classes'] = options.pop('class')
        node = nodes.reference(rawtext, name, refuri=ref,
                               **options)
        return [node], []
    assert False, "djangocms_link_role buggi implementation"

register_local_role("cmspage", djangocms_link_role)
