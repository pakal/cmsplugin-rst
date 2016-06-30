#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    REPO_ROOT = os.path.dirname(THIS_DIR)
    sys.path.extend([REPO_ROOT, 
                     os.path.join(THIS_DIR, "test_project")])

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
