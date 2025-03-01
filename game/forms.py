"""
forms.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Forms Baby :)
"""

from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField()
    display_name = forms.CharField(max_length=255)
