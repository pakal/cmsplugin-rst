from setuptools import setup, find_packages

version = __import__('cmsplugin_rst').__version__

setup(
    name = 'cmsplugin-rst',
    version = version,
    description = 'Restructured Text plugin for the django CMS.',
    author = 'Jonas Obrist',
    author_email = 'jonas.obrist@divio.ch',
    url = 'http://github.com/ojii/cmsplugin-rst',
    packages = find_packages(),
    zip_safe=False,
    install_requires=[
        'docutils',
        'django-cms>=2.1',
        'django>=1.2',
    ],
    extras_require = {
        'Postprocessors': ["BeautifulSoup==3.2.0"],
    }
)