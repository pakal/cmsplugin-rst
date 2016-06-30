#############
cmsplugin_rst
#############

*Forked from https://github.com/ojii/cmsplugin-rst*

A plugin for `Django CMS`_ which renders restructured text.
By default, it uses 

************
Installation
************

Install ``cmsplugin_rst`` using pip or your favorite method, using a virtualenv or not.

    $ pip install cmsplugin_rst

Add ``'cmsplugin_rst'`` to your ``INSTALLED_APPS`` in your Django settings.

To speed up the rendering of cmsplugin_rst plugins, consider using the cache framework of django.


***************
Configuration
***************

CMSPLUGIN_RST_WRITER_NAME
    Name of the docutils writer to be used for rendering HTML (default: "html4css1")

CMSPLUGIN_RST_CONTENT_PREFIX
    A restructuredtext string wich will be prepended to all your RST plugin contents, before rendering.
    Useful to define replacement blocks, custom roles, etc.
    
CMSPLUGIN_RST_CONTENT_SUFFIX
    A restructuredtext string wich will be appended to all your RST plugin contents, before rendering.

CMSPLUGIN_RST_SETTINGS_OVERRIDES
    A dict of settings which will be merged over plugin defaults, and passed to the docutils renderer. 
    See docutils ``publish_parts()`` and its ``settings_overrides`` parameter : 
    http://docutils.sourceforge.net/docs/user/config.html#html4css1-writer

CMSPLUGIN_RST_POSTPROCESSORS
    If and only if ``BeautifulSoup`` is installed, these postprocessors are applied 
    to the rendered HTML before displaying it.
    It must be a list of qualified function names, eg. ["mymodule.mysubmodule.myfunction"].
    Each of these functions must expect a beautifulsoup tree as unique argument, 
    and modify it in-place.
    
    
DjangoCMS: http://docs.django-cms.org/