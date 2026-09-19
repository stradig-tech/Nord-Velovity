import os
import sys

# 1. Add Backend directory to sys.path so Python can find nordvelocity package
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 2. Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')

# 3. Expose WSGI application for Phusion Passenger on cPanel
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
