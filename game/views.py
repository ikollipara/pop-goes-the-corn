from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User
from .forms import LoginForm


def home(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            display_name = form.cleaned_data["display_name"]

            user = User.objects.filter(email=email).first()
            if user:
                login(request, user)
            else:
                user = User.objects.create(email=email, display_name=display_name)
                login(request, user)
            return redirect("home")
    else:
        form = LoginForm()

    return render(request, "home.html", {"form": form})
