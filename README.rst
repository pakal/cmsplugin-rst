#############
cmsplugin_rst
#############

A plugin for `Django CMS`_, which renders restructured text into html, using docutils.


************
Installation
************

Install ``cmsplugin_rst`` using pip or your favorite method, using a virtualenv or not.

    $ pip install cmsplugin_rst

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
and *raw* directive, in the restructured text renderer.**


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

CMSPLUGIN_RST_POSTPROCESSORS
    If and only if ``BeautifulSoup`` is installed, these postprocessors are applied 
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

Reverse IDs must exist and be unique in the djangocms DB, else the rendering of the link fails.

   
*************
Test Project
*************

A demo project with a sqlite DB is included in repository, 
as a git submodule (https://git-scm.com/docs/git-submodule).

Its django admin credentials are test/test.


.. _Django CMS: https://www.django-cms.org