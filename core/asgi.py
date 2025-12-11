import os
from django.core.asgi import get_asgi_application

# Set default settings module for Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Vercel requires this variable name
app = get_asgi_application()
