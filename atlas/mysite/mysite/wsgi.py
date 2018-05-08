"""
WSGI config for mysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

# import sys
import os


from django.core.wsgi import get_wsgi_application

# path = '/home/path/to/project'
# if path not in sys.path:uws
#     sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

application = get_wsgi_application()
