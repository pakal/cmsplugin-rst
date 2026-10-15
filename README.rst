#############
cmsplugin_rst
#############

A plugin for `Django CMS`_, which renders restructured text into html, using docutils.

Supports python 3.10+, django-cms 3.11 to 5.x, and django 4.2 to 6.x.


************
Installation
************

Install ``cmsplugin_rst`` using pip or your favorite method, using a virtualenv or not.

    $ pip install cmsplugin_rst

To use postprocessors (see below), install the optional ``beautifulsoup4`` dependency too:

    $ pip install cmsplugin_rst[postprocessors]

To get syntax highlighting of code blocks (see below), install the optional ``pygments`` dependency:

    $ pip install cmsplugin_rst[highlighting]

Add ``'cmsplugin_rst'`` to your ``INSTALLED_APPS``, in your django settings.

And then migrate the DB:

    $ python manage.py migrate
    
Beware, if you upgrade from **cmsplugin_rst v0.1.1**, 
which didn't use django migrations but South, 
you may have to skip the initial migration (eg. if you get the 
"OperationalError: table "cmsplugin_rst_rstpluginmodel" already exists" error):

    $ python manage.py migrate --fake-initial cmsplugin_rst

To speed up the (potentially heavy) rendering of cmsplugin_rst plugins, 
consider using the cache framework of django.


***************
Configuration
***************

The behaviour of cmsplugin_rst can be tweaked with these Django settings (all are optional).

**The plugin disallows, by default, insecure features like *file insertions* 
and *raw* directive, in the restructured text renderer. Links and images
with unsafe URLs (eg. "javascript:...") are also neutralized, with a warning.**


CMSPLUGIN_RST_WRITER_NAME
    Name of the docutils writer to be used for rendering HTML (default: "html4css1")

CMSPLUGIN_RST_CONTENT_PREFIX
    A restructuredtext string wich will be prepended to all your RST plugin contents, before rendering.
    Useful to define replacement blocks, custom roles, etc.
    
CMSPLUGIN_RST_CONTENT_SUFFIX
    A restructuredtext string wich will be appended to all your RST plugin contents, before rendering.

CMSPLUGIN_RST_SETTINGS_OVERRIDES
    A dict of settings which will be merged over plugin defaults, and passed to the docutils renderer. 
    See docutils ``publish_parts()`` and its ``settings_overrides`` parameter (http://docutils.sourceforge.net/docs/user/config.html#html4css1-writer).
    Amongst interesting settings are "initial_header_level" and "report_level".

CMSPLUGIN_RST_ALLOWED_URL_SCHEMES
    The URL schemes allowed in links and images, case-insensitively; relative URLs are always allowed
    (default: ``("http", "https", "ftp", "ftps", "mailto", "tel")``).
    Links with other schemes are replaced by their text, and images by their alternate text.

CMSPLUGIN_RST_POSTPROCESSORS
    If and only if ``beautifulsoup4`` is installed, these postprocessors are applied 
    to the rendered HTML before displaying it.
    It must be a list of qualified function names, eg. ["mymodule.mysubmodule.myfunction"].
    Each of these functions must expect a beautifulsoup tree as unique argument, 
    and modify it in-place.

    
***********************************
Specific Roles and Replacements
***********************************

The restructured text is not evaluated by the django template engine, 
so you can't use django/djangocms tags and filters.

But some specific replacements take place:

- {{ MEDIA_URL }} and {{ STATIC_URL }} tags are replaced, *before* html rendering, 
  by corresponding django settings.
- {{ BR }} and {{ NBSP }} are replaced, *after* html rendering, by corresponding html
  tags/entities.

Additionally, you can create links to other CMS pages with 
the custom "cmspage" role provided, using the "reverse IDs" 
that you'll have set previously in advanced page parameters:

::

   :cmspage:`My-Reverse-Id`   // the menu title will be use as the link name
   
   :cmspage:`My Link Name <My-Reverse-Id>`   // here the link name is embedded in role

Targeted pages must be published (with djangocms-versioning, if installed, on django-cms>=4),
and their reverse IDs must exist and be unique on the current site, else the rendering of the link fails.

   
*******************
Syntax Highlighting
*******************

The standard docutils ``code`` directive (and its aliases ``code-block`` and ``sourcecode``)
highlights source code, provided that Pygments is installed:

::

   .. code:: python
      :number-lines:

      def hello(name):
          return "Hello %s" % name

Inline code can be highlighted too, by defining a custom role based on the ``code`` role:

::

   .. role:: py(code)
      :language: python

   Use :py:`import os` to import the module.

Beware, without Pygments, code blocks with a language argument are replaced by a
"Pygments package not found" warning message, unless "report_level" is set above 2
or "syntax_highlight" is set to "none" (see below), in which case they are rendered
as plain literal blocks. Code blocks without a language argument are never highlighted.

Highlighted tokens are wrapped in ``<span>`` elements with CSS classes, but no styling is applied
by default: include the stylesheet bundled with this app (Pygments' "default" style) in your
page templates:

::

   {% load static %}
   <link rel="stylesheet" href="{% static 'cmsplugin_rst/pygments.css' %}">

Beware, docutils uses *long* token class names by default (eg. ``class="name function"``),
so the stylesheets of Pygments itself, which use short class names (eg. ``class="nf"``), don't
work as is. To get a stylesheet for any other Pygments style (see ``pygmentize -L styles``), run:

::

   $ python -m cmsplugin_rst.highlighting monokai > myproject/static/css/pygments-monokai.css

Alternatively, you can switch docutils to short class names, with
``CMSPLUGIN_RST_SETTINGS_OVERRIDES = {"syntax_highlight": "short"}``, and then generate a
matching stylesheet with ``python -m cmsplugin_rst.highlighting monokai short``.
Generated stylesheets only target highlighted code, unlike the stylesheets of Pygments itself
(eg. from ``pygmentize -S monokai -f html``), which also restyle all ``<pre>`` elements of the site.
Setting ``"syntax_highlight": "none"`` disables highlighting altogether.


*************
Tests
*************

The test suite uses pytest and pytest-django; run it against your current environment with:

    $ pip install -e .[test]
    $ pytest
    $ pytest --cov    # with a coverage report

Or against all supported python/django-cms/django combinations, with tox:

    $ pip install tox tox-uv
    $ tox p                         # all environments, in parallel
    $ tox -e py313-cms50-dj52       # a single environment

Some code paths are only exercised with specific django-cms versions, or with djangocms-versioning
(see the ``-versioning`` tox environments).

To test the plugin live, a demo django-cms project is included in the repository, as a git submodule
(fetch it with ``git submodule update --init``). Run it with:

    $ python tests/manage.py                    # or "python tests/manage.py runserver 8765" for another port

This migrates a temporary sqlite database (its path is displayed, and can be set with the
``DJANGO_TEST_DB_PATH`` environment variable; delete it to start from scratch), creates demo pages
and a superuser with credentials admin/admin, then runs the development server on http://127.0.0.1:8000/.
Its settings are in ``tests/test_settings.py``. Other django commands work as usual, eg.
``python tests/manage.py createsuperuser``.


.. _Django CMS: https://www.django-cms.org