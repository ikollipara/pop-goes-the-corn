"""
models.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Game Models
"""

import random
from typing import TYPE_CHECKING

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.transaction import atomic
from django.utils import timezone

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class CardQuerySet(models.QuerySet["Card"]):
    """Custom queryset for the Card."""

    def get_random_card(self):
        max_id = self.aggregate(max_id=models.Max("id"))["max_id"]
        if max_id:
            random_id = random.randint(1, max_id)
            while not (card_qs := self.filter(pk=random_id)).exists():
                random_id = random.randint(1, max_id)

            return card_qs.get()


class Card(models.Model):
    """
    # Card.

    A card represets a potential playing card in the game.
    Cards have a vareity of effects, detailed in `game/effects.py`.
    The effect is noted in the effect column, which stores the effect's function name.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()
    rarity = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    effect = models.TextField()
    image = models.TextField()

    objects: CardQuerySet = CardQuerySet.as_manager()

    def __str__(self):
        return self.name

    def do_effect(self, game: "Game") -> str:
        """Execute the given effect."""

        from game import effects

        return effects.__dict__[self.effect](game)


class GameQuerySet(models.QuerySet["Game"]):
    """Custom Queryset for the Game."""

    def not_started(self):
        """Filter the games to include only those that have not yet finished."""

        return self.filter(started_at__isnull=True)

    def with_player_count(self):
        """Annotate the game to include the player count."""

        return self.annotate(player_count=models.Count("players"))

    def create_with_player(self, user: "User"):
        """Create a game with the given user as the first player."""

        game = self.create()
        game.players.create(user=user, is_active=False, next_player=None)

        return game


class Game(models.Model):
    """
    # Game.

    The game is the central model to the application.
    It includes a vareity of data for the game state,
    which is synced across a web socket to the frontend.

    There are a vareity of methods, since each game must do certain
    actions.
    """

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    pops_left = models.IntegerField(default=0)
    until_next_pop = models.IntegerField(default=0)
    last_card_played = models.IntegerField(default=None, null=True)
    chance_to_draw = models.SmallIntegerField(
        default=75, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    objects: GameQuerySet = GameQuerySet.as_manager()

    deck_cards: "RelatedManager[Deck]"
    players: "RelatedManager[UserGame]"

    def to_json(self):
        """Serialize to json."""
        return {
            "pops_left": self.pops_left,
            "until_next_pop": self.until_next_pop,
            "last_card_played": self.last_card_played,
            "chance_to_draw": self.chance_to_draw,
        }

    @atomic
    def join(self, email: str):
        """Have a player with the given email join the game."""
        last_player = UserGame.objects.get_last_player_for_game(self)
        player = self.players.create(user=User.objects.get_by_email(email))
        last_player.next_player = player
        last_player.save()

    @atomic
    def start(self):
        """Start a nnew game."""

        # This will close the loop for the players so we have an actual circle
        last_player = UserGame.objects.get_last_player_for_game(self).get()
        first_player = UserGame.objects.is_active_for_game(self).get()
        last_player.next_player = first_player
        last_player.save()

    @atomic
    def click(self) -> bool:
        """Apply a click to the corn kernel."""

        popped = False
        self.until_next_pop -= 1
        if self.until_next_pop == 0:
            self.pops_left -= 1
            popped = True

        self.save()
        return popped

    @atomic
    def advance_turn(self):
        """Advance the game to the start of the next player's turn."""

        UserGame.objects.is_active_for_game(self).update(
            next_player__is_active=True, is_active=False
        )


class UserQuerySet(models.QuerySet["User"]):
    """Custom queryset for the User Model."""

    def get_by_email(self, email: str):
        """Retrieve a user by the given email. Throw if not found."""
        return self.filter(email=email).get()


class User(models.Model):
    """
    # User.

    This user is different from Django's user model.
    The game does not require a more complex user, so a simple
    email and display name can be used.
    """

    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=255)

    objects: UserQuerySet = UserQuerySet.as_manager()

    def __str__(self):
        return self.display_name


class UserGameQuerySet(models.QuerySet["UserGame"]):
    """Custom Queryset for the UserGame."""

    def for_user(self, user: User | str):
        """Filter to only include those with the given user (or user email)."""

        if isinstance(user, str):
            return self.filter(user__email=user)

        else:
            return self.filter(user=user)

    def for_game(self, game: Game):
        """Filter to only include those with the given game."""
        return self.filter(game=game)

    def is_active_for_game(self, game: Game):
        """Filter to only include the active player for the given game."""
        return self.filter(is_active=True, game=game)

    def with_user_email(self):
        """Annotate to include the user's email."""

        return self.annotate(user__email=models.F("user__email"))

    def get_last_player_for_game(self, game: Game):
        """Get the last palyer for the given game.

        We define last to mean no next player.
        The last is the last joined, since one the game
        starts this will always be null.
        """

        return self.filter(game=game, next_player__isnull=True)

    def alive(self):
        return self.filter(killed_at__isnull=True)


class UserGame(models.Model):
    """
    # UserGame.

    The UserGame is the join table connecting users to the game.
    The table includes important information on that particular player's state
    during the game, such as if they're active or if they have been killed.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="players")
    killed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField()
    next_player: "models.OneToOneField[UserGame]" = models.OneToOneField(
        "game.UserGame",
        on_delete=models.DO_NOTHING,
        related_name="prev_player",
        null=True,
    )

    objects: UserGameQuerySet = UserGameQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "game"], name="usergame_user_game_unique"
            )
        ]

    @atomic
    def kill(self):
        """Kill the given player."""
        self.killed_at = timezone.now()
        self.prev_player = self.next_player
        self.save()


class DeckQuerySet(models.QuerySet["Deck"]):
    """Custom Queryset for the Deck."""

    def create_for_game(self, game: Game, size: int):
        """Create a deck for the given game with the given size."""

        if Card.objects.count() > 1:
            for i in range(1, size + 1):
                card = Card.objects.get_random_card()
                self.create(game=game, card=card, placement=i)

    def for_game(self, game: Game):
        """Filter to only include those with the given game."""
        return self.filter(game=game)

    def cards_left_for_game(self, game: Game):
        """Determine the number of cards left in a deck for a given game."""
        return self.filter(is_played=False, game=game).count()

    def current_card(self, game: Game):
        """Determine the current card for the given game."""
        return self.filter(
            is_played=False,
            placement=models.Subquery(
                Game.objects.filter(game=game).get().last_card_played
            ),
        ).get()

    def order_by_placement(self):
        return self.order_by("-placement")

    def get_drawn_card_for_game(self, game: Game):
        """Potentially draw a card, given the game's random chance."""

        chance = game.chance_to_draw
        if random.randint(1, 100) < chance:
            deck_card = self.for_game(game).order_by_placement().earliest("-placement")
            deck_card.is_played = True
            deck_card.save(update_fields=["is_played"])

        return deck_card.card


class Deck(models.Model):
    """
    # Deck.

    The deck is a collection of the cards available in a particular game.
    If a card is drawn, we mark it as played. In a sense, the card has
    been put into play.

    Placement is used strictly for ordering.
    """

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="deck_cards")
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    # is_drawn == is_played
    is_played = models.BooleanField(default=False)
    placement = models.PositiveSmallIntegerField()

    objects: DeckQuerySet = DeckQuerySet.as_manager()

    class Meta:
        indexes = [models.Index(fields=["card", "game"])]


class HandQuerySet(models.QuerySet["Hand"]):
    """Custom Queryset for Hand."""

    def for_game(self, game: Game):
        """Filter to include those with the given game."""

        return self.filter(game=game)

    def for_user_email(self, email: str):
        """Filter to include those who have a user with the given email."""

        return self.filter(user__email=email)

    def for_card(self, card: Card):
        """Filter to include those with the given card."""

        return self.filter(card=card)

    def add_drawn_card(self, card: Card, email: str, game: Game):
        """Add the given card to the user's hand for the given game."""

        return self.create(
            card=card,
            user=models.Subquery(User.objects.filter(email=email))[0],
            game=game,
        )


class Hand(models.Model):
    """
    # Hand.

    The hand model represets a particular player's hand.
    This is used to display their cards, among other things.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hand")
    card = models.ForeignKey(Card, on_delete=models.DO_NOTHING)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    objects: HandQuerySet = HandQuerySet.as_manager()

    class Meta:
        indexes = [models.Index(fields=["user", "game"])]
