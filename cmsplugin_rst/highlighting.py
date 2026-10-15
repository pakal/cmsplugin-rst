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


def _get_css_declarations(ndef, parent_ndef):
    """Return CSS declarations for the properties of a token which differ from its parent token.

    Since an element with long class names also matches the CSS rules of its parent tokens
    (eg. "keyword pseudo" matches ".keyword"), properties disabled by a child token (eg. via
    Pygments "nobold") must be explicitly reset.
    """
    declarations = []
    for key, css_property, on_value, off_value in [
        ("color", "color", "#%s", "inherit"),
        ("bgcolor", "background-color", "#%s", "transparent"),
        ("bold", "font-weight", "bold", "normal"),
        ("italic", "font-style", "italic", "normal"),
        ("underline", "text-decoration", "underline", "none"),
        ("border", "border", "1px solid #%s", "none"),
    ]:
        value = ndef[key] or None  # normalize False/None/""
        if value == (parent_ndef.get(key) or None):
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
    from pygments.formatters import HtmlFormatter
    from pygments.styles import get_style_by_name

    if tokennames == "short":
        return HtmlFormatter(style=style_name).get_style_defs(CSS_CONTAINERS) + "\n"
    if tokennames != "long":
        raise ValueError("Unsupported tokennames value %r (must be 'long' or 'short')" % tokennames)

    style = get_style_by_name(style_name)
    container_declarations = []
    if style.background_color:
        container_declarations.append("background-color: %s" % style.background_color)
    token_rules = []

    for ttype, ndef in style:
        parent_ndef = style.style_for_token(ttype.parent) if ttype.parent is not None else {}
        declarations = _get_css_declarations(ndef, parent_ndef)
        if not declarations:
            continue
        classes = _get_long_classes(ttype)
        if classes:
            token_rules.append("%s { %s; }" % (_get_selector(" ." + ".".join(classes)), "; ".join(declarations)))
        else:
            # Unstyled tokens (eg. Token.Text) are styled via their container
            container_declarations.extend(declarations)

    rules = ["/* Pygments style %r, for docutils long token names */" % style_name]
    if container_declarations:
        container_declarations = "; ".join(container_declarations)
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
