from django.contrib import admin
from .models import Games, About, GameInfo , Subscriber

admin.site.register(Games)
admin.site.register(About)
admin.site.register(GameInfo)
admin.site.register(Subscriber)