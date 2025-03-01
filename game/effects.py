"""
effects.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Effects
"""

from __future__ import annotations

from game.models import Deck, Game


def skip(game: Game) -> str:
    player = game.players.filter(is_active=True, killed_at__isnull=True).get()
    player.is_active = False
    next_player = (
        game.players.filter(is_active=True, killed_at__isnull=True).get().next_player
    )
    next_player.is_active = True

    player.save()
    next_player.save()

    return "Skipped Turn!"
