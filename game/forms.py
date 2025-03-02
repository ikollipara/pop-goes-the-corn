"""
forms.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Forms Baby :)
"""

from django import forms

from game.models import Deck, Game, User


class UserLoginForm(forms.ModelForm):
    '''Form for logging in a user'''
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
        '''Save the user to the database and return the user''' 
        user, _ = User.objects.get_or_create(**self.cleaned_data)
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    display_name = forms.CharField(max_length=255)


class GameForm(forms.ModelForm):
    '''Form for creating a game'''
    deck_size = forms.IntegerField(
        label="Deck Size",
        max_value=1_000,
        min_value=100,
        required=True,
        widget=forms.NumberInput(
            {
                "class": "border border-gray-800 w-full rounded px-2 py-1 bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-red-500",
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
        '''Create a game with the current user and a deck of the given size'''
        game = Game.objects.create_with_player(self.request.game_user)
        Deck.objects.create_for_game(game, self.cleaned_data["deck_size"])

        return game
