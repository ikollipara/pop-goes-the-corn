"""
views.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Views
"""

import random

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView

from game.forms import GameForm, UserLoginForm
from game.models import Game, User, UserGame


def authed(view):
    """Make the given view only available to authed users."""

    def inner(request, *args, **kwargs):
        if not request.COOKIES.get("email"):
            return redirect("home")

        request.game_user = User.objects.get_by_email(request.COOKIES["email"])
        return view(request, *args, **kwargs)

    return inner


def guest(view):
    """Make the given view only available to guest users (not authed)."""

    def inner(request, *args, **kwargs):
        if request.COOKIES.get("email"):
            request.game_user = User.objects.get_by_email(request.COOKIES["email"])
            return redirect("lobby")

        return view(request, *args, **kwargs)

    return inner


class HomeView(FormView):
    """
    # Homepage view.

    The homepage includes form for either logging in or creating an account.
    """

    form_class = UserLoginForm
    template_name = "game/login.html"

    def form_valid(self, form):
        user = form.save()

        response = redirect("lobby")
        response.set_cookie("email", user.email)
        return response


class GameLobbyListView(ListView):
    """
    # GameLobbyListView

    The list of active game lobbies.
    The only ones shown are the games that are not started.
    """

    model = Game
    template_name = "game/game_list.html"
    context_object_name = "games"
    queryset = Game.objects.not_started().with_player_count()


class GameCreateView(CreateView):
    """
    # GameCreateView.

    The view for creating a game.
    This view is quite short, and uses a custom
    form with an overriden save method.
    """

    model = Game
    form_class = GameForm
    template_name = "game/game_create.html"
    success_url = reverse_lazy("lobby")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class GameDetailView(DetailView):
    """
    # GameDetailView.

    The main view of the application, this view is
    short since most of the data is passed through
    the websocket connection.
    """

    model = Game
    template_name = "game/game_detail.html"
    context_object_name = "game"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["alive_users"] = self.object.players.alive()

        # This is the collection of initial data
        # used to setup the websocket connection.
        context["data"] = {
            "ws": f"/ws/game/{self.get_object().pk}",
            "creator": UserGame.objects.is_active_for_game(self.get_object())
            .get()
            .user.email,
            "player": self.request.game_user.email,
        }

        return context
