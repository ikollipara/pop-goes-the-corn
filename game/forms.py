"""
forms.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Forms Baby :)
"""

from django import forms

from game.models import User


class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "display_name"]

    def save(self, *args, **kwargs):
        email = self.cleaned_data["email"]
        user = User.objects.get_or_create(
            {"display_name": self.cleaned_data["display_name"]}, email=email
        )
        return user
