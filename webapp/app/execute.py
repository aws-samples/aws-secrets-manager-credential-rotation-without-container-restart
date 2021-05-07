#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codecompose.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    #this is done just for quickstart demo purpose.
    #production should separate out the database migrations and also use a more robust wsgi web server
    execute_from_command_line(['manage.py','makemigrations','encryptioncontext'])
    execute_from_command_line(['manage.py','migrate'])
    execute_from_command_line(['manage.py','runserver','0.0.0.0:80'])
