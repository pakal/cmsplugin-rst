#!/usr/bin/env python
"""Manage the demo django-cms project (git submodule "test_project"), with cmsplugin_rst installed, to test it live.

Without arguments, or with the "runserver" command (eg. "runserver 8765" for another port), migrates the
database, creates an "admin" superuser (password "admin") and demo pages if they don't exist yet, then runs the
development server: "python tests/manage.py", then open http://127.0.0.1:8000/ in a browser. Other commands are
run as usual.

Data is stored in a temporary sqlite file (path displayed at startup, and customizable with the
DJANGO_TEST_DB_PATH environment variable): delete it to start from scratch.
"""

import os
import sys
import tempfile

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(THIS_DIR)

DEMO_BODY_EN = """\
This is a top title
===================

This is a subtitle
------------------

This is a first heading
~~~~~~~~~~~~~~~~~~~~~~~

No invisible space added before exclamation point in EN lang !

This is a **bold** word, with a `link <https://www.python.org>`_ and a (unicode-backed) \
non\\ |nbsp|\\ breaking\\ |nbsp|\\ word, as well as an invisible html entity here:{{ NBSP }}.
This sentence is on the same line.
{{ BR }}
This sentence is separated by a newline.

Here is a cms page link (see :cmspage:`My-Reverse-Id`); and here another with \
:cmspage:`custom text <My-Reverse-Id>`. Note that case sensitivity matters, else an ERROR is triggered \
as below: (:cmspage:`my-reverse-id`).

This `unsafe link <javascript:alert(1)>`_ is neutralized, with a warning.

This is a second heading
~~~~~~~~~~~~~~~~~~~~~~~~

   This is a block quote.

::

  Your MEDIA_URL is '{{ MEDIA_URL }}' and STATIC_URL is '{{ STATIC_URL }}'.

Syntax highlighting
~~~~~~~~~~~~~~~~~~~

.. code:: python

   def greet(name: str) -> str:
       \"\"\"Return a greeting.\"\"\"
       return f"Hello {name}!"  # with a comment

.. role:: py(code)
   :language: python

And some inline code: :py:`print("hi")`.
"""

DEMO_BODY_FR = """\
Exemple de RST FR
=================

Ceci est une phrase !

Admirez la typographie de ponctuation ; n'est-ce pas joli ? Elle coûte 12345 € « environ », soit 10 % de plus.

::

  Le code n'est pas modifié : voyez !
"""


def setup_demo():
    """Migrate the database, and create a superuser and demo pages if they don't exist yet."""
    from cms.models import Page
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.core.management import call_command
    from django.db import transaction

    print("Using the sqlite database %s (delete it to start from scratch)" % settings.DATABASES["default"]["NAME"])
    call_command("migrate", interactive=False, verbosity=0)

    User = get_user_model()
    user = User.objects.filter(username="admin").first()
    if user is None:
        user = User.objects.create_superuser("admin", "admin@example.com", "admin")
        print('Created the superuser "admin" (password "admin")')

    if not Page.objects.exists():
        with transaction.atomic():  # required by django-cms to modify the page tree
            create_demo_pages(user)
        print("Created demo pages")


def create_demo_pages(user):
    import cms
    from cms.api import add_plugin, create_page
    from django.conf import settings

    legacy_cms = tuple(int(x) for x in cms.__version__.split(".")[:2]) < (4, 0)
    use_versioning = "djangocms_versioning" in settings.INSTALLED_APPS

    def get_content(page, language):
        # not page.get_admin_content(), whose cache misses the contents of translations added afterwards
        from cms.models import PageContent

        return PageContent.admin_manager.current_content().get(page=page, language=language)

    def get_placeholder(page, language):
        if legacy_cms:
            page.rescan_placeholders()
            return page.placeholders.get(slot="content")
        content = get_content(page, language)
        content.rescan_placeholders()
        return content.get_placeholders().get(slot="content")

    def publish(page, language):
        if legacy_cms:
            page.publish(language)
        elif use_versioning:
            from djangocms_versioning.models import Version

            Version.objects.get_for_content(get_content(page, language)).publish(user)

    def add_translation(page, language, title):
        if legacy_cms:
            from cms.api import create_title

            create_title(language, title, page)
        else:
            from cms.api import create_page_content

            create_page_content(language, title, page, created_by=user, in_navigation=True)

    page_kwargs = {"created_by": user, "in_navigation": True}
    if legacy_cms:
        page_kwargs["published"] = True

    home = create_page("cmsplugin-rst demo", "demo_page.html", "en", **page_kwargs)
    home.set_as_homepage(user)
    add_plugin(get_placeholder(home, "en"), "RstPlugin", "en", name="Demo RST EN", body=DEMO_BODY_EN)
    add_translation(home, "fr", "Démo cmsplugin-rst")
    add_plugin(get_placeholder(home, "fr"), "RstPlugin", "fr", name="Démo RST FR", body=DEMO_BODY_FR)

    linked = create_page("Linked page", "demo_page.html", "en", reverse_id="My-Reverse-Id", **page_kwargs)
    add_plugin(get_placeholder(linked, "en"), "RstPlugin", "en", name="Linked",
               body="This page is the target of the **cmspage** links of the home page.")

    for page, languages in [(home, ["en", "fr"]), (linked, ["en"])]:
        for language in languages:
            publish(page, language)


if __name__ == "__main__":
    sys.path[:0] = [REPO_ROOT, THIS_DIR, os.path.join(THIS_DIR, "test_project")]

    os.environ.setdefault("DJANGO_TEST_DB_PATH", os.path.join(tempfile.gettempdir(), "cmsplugin_rst_demo.sqlite3"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")

    import django
    from django.core.management import execute_from_command_line

    argv = sys.argv if len(sys.argv) > 1 else sys.argv + ["runserver"]
    if argv[1] == "runserver" and not os.environ.get("RUN_MAIN"):  # not in the autoreloader child process
        django.setup()
        setup_demo()

    execute_from_command_line(argv)
