"""
models.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01
"""

from typing import TYPE_CHECKING

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


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
    chance_to_draw = models.SmallIntegerField(
        default=75,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    deck_cards: "RelatedManager[Deck]"
    players: "RelatedManager[UserGame]"


class User(models.Model):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=255)


class UserGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="players")
    killed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField()
    next_player: "models.OneToOneField[UserGame]" = models.OneToOneField(
        "game.UserGame", on_delete=models.DO_NOTHING, related_name="prev_player"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "game"], name="usergame_user_game_unique"
            )
        ]

    def kill(self):
        self.killed_at = timezone.now()
        self.save()


class DeckQuerySet(models.QuerySet["Deck"]):
    def for_game(self, game: Game):
        return self.filter(game=game)

    def cards_left_for_game(self, game: Game):
        return self.filter(is_played=False, game=game).count()

    def current_card(self, game: Game):
        return self.filter(
            is_played=False,
            placement=models.Subquery(
                Game.objects.filter(game=game).get().last_card_played
            ),
        ).get()


class Deck(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="deck_cards")
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    # is_drawn == is_played
    is_played = models.BooleanField(default=False)
    placement = models.PositiveSmallIntegerField()

    objects: DeckQuerySet = DeckQuerySet.as_manager()

    class Meta:
        indexes = [models.Index(fields=["card", "game"])]



class Hand(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hand")
    card = models.ForeignKey(Card, on_delete=models.DO_NOTHING)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        indexes = [models.Index(fields=["user", "game"])]
