from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View

from .forms import UserLoginForm
from .models import User


class HomeView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, "game/login.html", {"form": form})

    def post(self, request):
        form = UserLoginForm(request.POST, self.request.FILES)
        if form.is_valid():
            user, _ = form.save()

            response = redirect("home")
            response.set_cookie("email", user.email)
            return response
