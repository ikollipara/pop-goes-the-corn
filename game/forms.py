"""
forms.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Forms Baby :)
"""

from django import forms

from game.models import Game, User, UserGame


class UserLoginForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            {
                "class": "border border-gray-800 w-full rounded px-2",
                "placeholder": "Email...",
            }
        )
    )

    class Meta:
        model = User
        fields = ["display_name"]
        widgets = {
            "display_name": forms.TextInput(
                {
                    "class": "border border-gray-800 w-full rounded px-2",
                    "placeholder": "Display Name...",
                }
            ),
        }

    def save(self, *args, **kwargs):
        email = self.cleaned_data["email"]
        print(email)
        if not (user := User.objects.filter(email=email).first()):
            user, _ = User.objects.create(
                email=email,
                display_name=self.cleaned_data["display_name"],
            )
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    display_name = forms.CharField(max_length=255)


class GameForm(forms.ModelForm):
    deck_size = forms.IntegerField(
        max_value=1_000,
        min_value=100,
        required=True,
        widget=forms.NumberInput(
            {
                "class": "border border-gray-800 w-full rounded px-2",
                "value": 500,
            }
        ),
    )

    class Meta:
        model = Game
        fields = []

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def save(self, *args, **kwargs):
        game = Game.objects.create()

        # Creating the deck

        game.players.create(
            user=self.request.game_user, is_active=False, next_player=None
        )

        return game
