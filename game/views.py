from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View

from .forms import UserLoginForm
from .models import User


class HomeView(View):
    def get(self):
        form = UserLoginForm()
        return render(self.request, "game/login.html", {"form": form})

    def post(self):
        form = UserLoginForm(self.request.POST, self.request.FILES)
        user, _ = form.save()

        login(self.request, user)
        return redirect("home")
