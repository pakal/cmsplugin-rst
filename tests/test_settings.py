
from textwrap import dedent
from test_app.settings import *

INSTALLED_APPS += ("cmsplugin_rst",)

 
## DJANGO CMSPLUGIN RST CONF ##

if not os.environ.get("CMSPLUGIN_RST_SKIP_CONF"):  # use this flag to test the zero-conf case

    CMSPLUGIN_RST_WRITER_NAME = "html4css1"

    CMSPLUGIN_RST_CONTENT_PREFIX = dedent("""

    .. |nbsp| unicode:: 0xA0 
       :trim:
    
    *Global Prefix: Start of Content*

    """)

    CMSPLUGIN_RST_CONTENT_SUFFIX =  \
    """*Global Suffix: End of Content*"""


    CMSPLUGIN_RST_SETTINGS_OVERRIDES = {"initial_header_level": 2, # minimum "h2" when rendered to html
                                        "smart_quotes": "alt"}
                                        #"'language_code': "fr"  # weirdly seems BROKEN!

                             
    def add_stuffs_to_soup(soup):
        soup.div.append("""String Appended Via Beautifulsoup Postprocessor""")

    CMSPLUGIN_RST_POSTPROCESSORS = [
        "test_settings.add_stuffs_to_soup"
    ]

