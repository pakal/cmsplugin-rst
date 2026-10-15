"""Generation of CSS stylesheets for the syntax highlighting of docutils "code" directives/roles.

Docutils relies on Pygments (if installed) to highlight code, but its default "long" token
class names (eg. "name function") differ from the short ones (eg. "nf") used by Pygments'
own stylesheets, so we generate matching CSS rules here.

Usage: python -m cmsplugin_rst.highlighting [STYLE_NAME [long|short]] > pygments.css
"""

import sys

# Containers of highlighted tokens: "code" directive blocks, and inline custom "code" roles
CSS_CONTAINERS = ("pre.code", "code")

# Like docutils.utils.code_analyzer.unstyled_tokens
UNSTYLED_TOKENS = ("token", "text", "")


def _get_long_classes(ttype):
    # Same logic as docutils.utils.code_analyzer.Lexer, for the "long" token names
    return [cls for cls in str(ttype).lower().split(".") if cls not in UNSTYLED_TOKENS]


def _get_short_classes(ttype):
    # Same logic as docutils.utils.code_analyzer.Lexer, for the "short" token names
    from pygments.formatters.html import _get_ttype_class

    return [cls for cls in [_get_ttype_class(ttype)] if cls not in UNSTYLED_TOKENS]


# Pygments style keys, with their CSS property, and CSS values when enabled/disabled
CSS_PROPERTIES = [
    ("color", "color", "#%s", "inherit"),
    ("bgcolor", "background-color", "#%s", "transparent"),
    ("bold", "font-weight", "bold", "normal"),
    ("italic", "font-style", "italic", "normal"),
    ("underline", "text-decoration", "underline", "none"),
    ("border", "border", "1px solid #%s", "none"),
]


def _get_css_declarations(ndef, parent_ndef, forced_keys=()):
    """Return CSS declarations for the properties of a token which differ from its parent token,
    or whose key is in `forced_keys`.

    Since an element with long class names also matches the CSS rules of its parent tokens
    (eg. "keyword pseudo" matches ".keyword"), properties disabled by a child token (eg. via
    Pygments "nobold") must be explicitly reset.
    """
    declarations = []
    for key, css_property, on_value, off_value in CSS_PROPERTIES:
        value = ndef[key] or None  # normalize False/None/""
        if value == (parent_ndef.get(key) or None) and key not in forced_keys:
            continue
        if value:
            declarations.append("%s: %s" % (css_property, on_value % value if "%" in on_value else on_value))
        else:
            declarations.append("%s: %s" % (css_property, off_value))
    return declarations


def _get_selector(suffix):
    return ", ".join("%s%s" % (container, suffix) for container in CSS_CONTAINERS)


def get_pygments_css(style_name="default", tokennames="long"):
    """Return a CSS stylesheet for the given Pygments style.

    `tokennames` must match the "syntax_highlight" docutils setting ("long" by default,
    or "short", which can be set via CMSPLUGIN_RST_SETTINGS_OVERRIDES).
    """
    from pygments.styles import get_style_by_name
    from pygments.token import STANDARD_TYPES

    if tokennames not in ("long", "short"):
        raise ValueError("Unsupported tokennames value %r (must be 'long' or 'short')" % tokennames)
    # Pygments' HtmlFormatter.get_style_defs() is not used for short names, since it also emits rules
    # for all <pre> elements and for line numbers tables, which would restyle the whole site.

    style = get_style_by_name(style_name)
    container_declarations = {}  # CSS property -> declaration, so that later tokens override earlier ones
    if style.background_color:
        container_declarations["background-color"] = "background-color: %s" % style.background_color
    token_rules = []

    tokens = list(style)
    if tokennames == "long":
        # Styles may define non-standard tokens (eg. "Comment.PreProc" in gruvbox), which lexers don't emit,
        # but whose long class names are the same as those of a standard token (eg. "Comment.Preproc")
        standard_classes = {frozenset(_get_long_classes(ttype)) for ttype in STANDARD_TYPES}
        tokens = [(ttype, ndef) for ttype, ndef in tokens
                  if ttype in STANDARD_TYPES or frozenset(_get_long_classes(ttype)) not in standard_classes]
        # Keys of the properties set by the rule of each token, to detect rules matching unrelated tokens
        rule_keys = {}
        for ttype, ndef in tokens:
            parent_ndef = style.style_for_token(ttype.parent) if ttype.parent is not None else {}
            if _get_long_classes(ttype):
                rule_keys[ttype] = {key for key, _, _, _ in CSS_PROPERTIES
                                    if (ndef[key] or None) != (parent_ndef.get(key) or None)}

    for ttype, ndef in tokens:
        forced_keys = set()
        if tokennames == "long":
            # an element with long class names also matches the rules of its parent tokens
            parent_ndef = style.style_for_token(ttype.parent) if ttype.parent is not None else {}
            classes = _get_long_classes(ttype)
            # ... and the rules of unrelated tokens whose classes are a subset of its own (eg. "name variable
            # class" matches ".name.class"), so it must explicitly set the properties of these rules; its own
            # rule has more classes, so it wins over them in the CSS cascade
            for other_ttype, other_keys in rule_keys.items():
                if (classes and other_ttype not in ttype.split()
                        and set(_get_long_classes(other_ttype)) < set(classes)):
                    forced_keys.update(other_keys)
        else:
            # an element with a short class name only matches its own rule, so it needs all its properties
            parent_ndef = {}
            classes = _get_short_classes(ttype)
        declarations = _get_css_declarations(ndef, parent_ndef, forced_keys)
        if not declarations:
            continue
        if classes:
            token_rules.append("%s { %s; }" % (_get_selector(" ." + ".".join(classes)), "; ".join(declarations)))
        else:
            # Unstyled tokens (eg. Token.Text) are styled via their container
            container_declarations.update((declaration.split(":")[0], declaration) for declaration in declarations)

    rules = ["/* Pygments style %r, for docutils %s token names */" % (style_name, tokennames)]
    if container_declarations:
        container_declarations = "; ".join(container_declarations.values())
        rules.append("pre.code { %s; }" % container_declarations)
        # Only highlighted inline code (not all <code> elements) gets the style's background and base
        # color, in a separate rule since browsers without :has() support would ignore the whole rule
        rules.append("code:has(> span) { %s; }" % container_declarations)
    rules.append("%s { color: #999999; user-select: none; }" % _get_selector(" .ln"))  # line numbers
    rules.extend(token_rules)
    return "\n".join(rules) + "\n"


if __name__ == "__main__":
    sys.stdout.reconfigure(newline="\n")  # no CRLF on windows
    sys.stdout.write(get_pygments_css(*sys.argv[1:]))
