from django.urls import path
from data import views
# from core.urls import urlpatterns
from django.contrib.auth import views as auth_views
urlpatterns = [
    path("games/",views.GameView.as_view()),
    path("games/<int:pk>/", views.GameView.as_view()),

    path("about_game/",views.AboutView.as_view()),
    path("about_game/<int:pk>/", views.AboutView.as_view()),

    path("cybercarnage/", views.games_list_view, name="home"),
    path("cybercarnage/about/", views.about_list_view, name="about_list"),
    path("cybercarnage/game_list/", views.gameinfo_list_view, name="gameinfo_list"),
    path("about/<int:pk>/", views.about_detail_view, name="about_detail"),

    path("contact/send/", views.send_contact, name="send_contact"),

    path("subscribe/", views.subscribe_newsletter, name="subscribe_newsletter"),

    path("cybercarnage/privacy/", views.privacy_page, name="privacy"),
    path("cybercarnage/terms/", views.terms_page, name="terms"),

    path("cybercarnage/faq/",views.faq_page, name="faq"),
]