import os
import sys

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forexml.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()