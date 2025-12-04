from django.urls import path
from data import views
# from core.urls import urlpatterns
from django.contrib.auth import views as auth_views

urlpatterns = [

    # ---------------- OLD URLS ----------------
    path("games/", views.GameView.as_view()),
    path("games/<int:pk>/", views.GameView.as_view()),

    path("about_game/", views.AboutView.as_view()),
    path("about_game/<int:pk>/", views.AboutView.as_view()),

    # ---------------- NEW CLEAN ROOT URLS ----------------
    path("", views.games_list_view, name="new_home"),
    path("about/", views.about_list_view, name="new_about_list"),
    path("game_list/", views.gameinfo_list_view, name="new_gameinfo_list"),

    path("privacy/", views.privacy_page, name="new_privacy"),
    path("terms/", views.terms_page, name="new_terms"),
    path("faq/", views.faq_page, name="new_faq"),
]
