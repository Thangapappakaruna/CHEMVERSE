import os

import sys

path = "/home/<username>/chemverse"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "chemverse.settings"
os.environ["SECRET_KEY"] = "put-a-long-random-string-here"
os.environ["DEBUG"] = "False"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()