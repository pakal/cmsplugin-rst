
from test_app.settings import *

INSTALLED_APPS += ("cmsplugin_rst",)


## DJANGO CMSPLUGIN RST CONF ##

CMSPLUGIN_RST_CONTENT_PREFIX = """

.. |nbsp| unicode:: 0xA0 
   :trim:
    
*Global Prefix: Start of Content*

"""

CMSPLUGIN_RST_CONTENT_SUFFIX =  \
"""*Global Suffix: End of Content*"""


CMSPLUGIN_RST_SETTINGS_OVERRIDES = {"initial_header_level": 2, # minimum "h2" when rendered to html
                                    "doctitle_xform": False, # important, to have even lone titles stay in the html fragment
                                    "sectsubtitle_xform": False, # we disable the promotion of the title of a lone subsection to a subtitle
                                    'file_insertion_enabled': False,  # SECURITY MEASURE (file hacking)
                                    'raw_enabled': False, # SECURITY MEASURE (script tag)
                                    'smart_quotes': "alt"}
                                    #"'language_code': "fr" ## SEEMS BROKEN!

                                    
def add_stuffs_to_soup(soup):
    soup.div.append("""String Appended Via Beautifulsoup Postprocessor""")

CMSPLUGIN_RST_POSTPROCESSORS = [
    "test_settings.add_stuffs_to_soup"
]


