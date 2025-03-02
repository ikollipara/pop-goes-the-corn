"""
routing.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Routing
"""

from django.urls import re_path

from game import consumers

websocket_patterns = [
    re_path(r"^ws/game/(?P<pk>[0-9]+)/", consumers.GameWebsocketConsumer.as_asgi())
]
