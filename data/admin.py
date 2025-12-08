from django.contrib import admin
from .models import Games, About, GameInfo , Subscriber , GuestUser , ChatMessage

admin.site.register(Games)
admin.site.register(About)
admin.site.register(GameInfo)
admin.site.register(Subscriber)
admin.site.register(ChatMessage)
admin.site.register(GuestUser)
