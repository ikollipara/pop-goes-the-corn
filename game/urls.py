"""
urls.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Urls
"""

from django.urls import path

from game import views

urlpatterns = [path("", views.HomeView.as_view(), name="home")]
