#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from base_project import startup


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if sys.argv[1] == 'runserver':
        import subprocess
        from django.conf import settings

        startup.run()
        subprocess.run(['uvicorn', f'{settings.PROJECT_NAME}.asgi:application', '--reload', '--host', '0.0.0.0'], check=False)
        return

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
