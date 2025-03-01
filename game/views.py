from django.contrib.auth import login
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from .forms import GameForm, UserLoginForm
from .models import Game, User


def authed(view):
    def inner(request, *args, **kwargs):
        if not request.COOKIES.get("email"):
            return redirect("home")

        request.game_user = User.objects.filter(email=request.COOKIES["email"]).get()
        print(request, view.__name__)
        return view(request, *args, **kwargs)

    return inner


def guest(view):
    def inner(request, *args, **kwargs):
        if request.COOKIES.get("email"):
            request.game_user = User.objects.filter(
                email=request.COOKIES["email"]
            ).get()
            return redirect("lobby")

        return view(request, *args, **kwargs)

    return inner


class HomeView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, "game/login.html", {"form": form})

    def post(self, request):
        form = UserLoginForm(request.POST, self.request.FILES)
        print(form)
        if form.is_valid():
            user = form.save()

            response = redirect("lobby")
            response.set_cookie("email", user.email)
            return response

        return render(request, "game/login.html", {"form": form})


class GameLobbyListView(ListView):
    model = Game
    template_name = "game/game_list.html"
    context_object_name = "games"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(started_at__isnull=True)


class GameCreateView(CreateView):
    model = Game
    form_class = GameForm
    template_name = "game/game_create.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("lobby")


class GameDetailView(DetailView):
    model = Game
    template_name = "game/game_detail.html"
    context_object_name = "game"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
