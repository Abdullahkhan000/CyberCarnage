# from django.contrib import admin
# from django.urls import path, include
#
# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("", include("data.urls")),
# ]

from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("data.urls")),

    # Discord HTTPS verification
    path('.well-known/discord', serve, {
        'path': 'discord',
        'document_root': os.path.join(BASE_DIR, '.well-known')
    }),
]
