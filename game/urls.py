"""
urls.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Urls
"""

from django.urls import path

from game import views

urlpatterns = [
    path("", views.guest(views.HomeView.as_view()), name="home"),
    path(
        "games/",
        views.authed(views.GameLobbyListView.as_view()),
        name="lobby",
    ),
    path("games/create/", views.authed(views.GameCreateView.as_view()), name="create"),
    path("game/<int:pk>/", views.authed(views.GameDetailView.as_view()), name="detail"),
]
