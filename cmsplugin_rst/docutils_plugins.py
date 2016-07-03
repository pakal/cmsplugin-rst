
import re
from docutils import nodes, utils
from docutils.parsers.rst.roles import set_classes, register_local_role


def djangocms_link_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
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

    result = re.match(r"^(.+) \<(.+)\>$", text)
    #print (">> djangocms_link_role regex result is", result, result.groups() if result else None)
    if result:
        name, reverse_id = result.groups()
    else:
        name = None
        reverse_id = text

    try:
        # beware: draft and published versions of a page may have the same reverse-ID...
        page_lookup = {'reverse_id': reverse_id,
                       'publisher_is_draft': False}  
        page = Page.objects.all().get(**page_lookup)
    except Page.DoesNotExist:
        msg = inliner.reporter.error("Targeted reverse page ID doesn't exist: %r" % reverse_id, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    except Page.MultipleObjectsReturned:
        print("MultipleObjectsReturned", reverse_id)
        msg = inliner.reporter.error("Targeted reverse page ID is not unique: %r" % reverse_id, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    else:
        if name is None:
            name = page.get_menu_title()
        ref = page.get_absolute_url()
        set_classes(options)
        node = nodes.reference(rawtext, name, refuri=ref,
                               **options)
        return [node], []
    assert False, "djangocms_link_role buggi implementation"

register_local_role("cmspage", djangocms_link_role)
