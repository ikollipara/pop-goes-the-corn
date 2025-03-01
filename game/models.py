"""
models.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Card(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    rarity = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    effect = models.TextField()
    image = models.TextField()

    def __str__(self):
        return self.name


class Game(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    pops_left = models.IntegerField(default=0)
    until_next_pop = models.IntegerField(default=0)
    last_card_played = models.IntegerField(default=None, null=True)


class User(models.Model):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=255)


class UserGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="players")
    killed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "game"], name="usergame_user_game_unique"
            )
        ]

    def kill(self):
        self.killed_at = timezone.now()
        self.save()


class Deck(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="deck_cards")
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    is_played = models.BooleanField(default=False)
    placement = models.PositiveSmallIntegerField()

    class Meta:
        indexes = [models.Index(fields=["card", "game"])]


class Hand(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hand")
    card = models.ForeignKey(Card, on_delete=models.DO_NOTHING)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        indexes = [models.Index(fields=["user", "game"])]
