"""
consumers.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

WebSocketConsumer
"""

from dataclasses import dataclass
from typing import Literal

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from game.models import Card, Deck, Game, Hand, UserGame


@dataclass(frozen=True)
class Status:
    game: dict[str, str]
    active_email: str
    type: Literal["status"] = "status"

    def to_dict(self):
        return {"type": self.type, "game": self.game, "active_email": self.active_email}


@dataclass(frozen=True)
class Start:
    game: dict[str, str]
    active_email: str
    type: Literal["start"] = "start"

    def to_dict(self):
        return {"type": self.type, "game": self.game, "active_email": self.active_email}


@dataclass(frozen=True)
class CardResolved:
    game: dict[str, str]
    active_email: str
    msg: str = ""
    type: Literal["card_resolved"] = "card_resolved"

    def to_dict(self):
        return {
            "type": self.type,
            "game": self.game,
            "active_email": self.active_email,
            "msg": self.msg,
        }


@dataclass(frozen=True)
class Ok:
    msg: str = ""
    type: Literal["ok"] = "ok"

    def to_dict(self):
        return {"type": self.type, "msg": self.msg}


@dataclass(frozen=True)
class Kick:
    msg: str = ""
    type: Literal["kick"] = "kick"

    def to_dict(self):
        return {"type": self.type, "msg": self.msg}


class GameWebsocketConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.game_pk = self.scope["url_route"]["kwargs"]["pk"]
        async_to_sync(self.channel_layer.group_add)(self.game_pk, self.channel_name)
        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(self.game_pk, self.channel_name)

    def receive_json(self, content, **kwargs):
        type_ = content["type"]
        game = Game.objects.get(pk=self.game_pk)

        match type_:
            case "status":
                user_email = (
                    UserGame.objects.is_active_for_game(game)
                    .with_user_email()
                    .get()
                    .user__email
                )
                self.send_json(
                    Status(
                        game=game.to_json(),
                        active_email=user_email,
                    ).to_dict()
                )

            case "join":
                game.join(content["email"])
                self.send_json(Ok(msg="Successfully joined").to_dict())

            case "start_game":
                game.start()
                self.send_json(
                    Start(
                        game=game.to_json(),
                        active_email=UserGame.objects.with_user_email()
                        .is_active_for_game(game)
                        .get()
                        .user__email,
                    ).to_dict()
                )

            case "click":
                game.click()
                if card := Deck.objects.get_drawn_card_for_game(game):
                    Hand.objects.add_drawn_card(
                        card=card, email=content["email"], game=game
                    )
                self.send_json(Ok().to_dict())

            case "play_card":
                Hand.objects.for_game(game).for_card(content["card"]).for_user_email(
                    content["email"]
                ).delete()
                card = Card.objects.filter(pk=content["card"]).get()
                msg = card.do_effect(game)

                self.send_json(
                    CardResolved(
                        game=game.to_json(),
                        active_email=UserGame.objects.with_user_email()
                        .is_active_for_game(game)
                        .get()
                        .user__email,
                        msg=msg,
                    ).to_dict()
                )

            case "end_turn":
                game.advance_turn()
                self.send_json(
                    Start(
                        game=game.to_json(),
                        active_email=UserGame.objects.with_user_email()
                        .is_active_for_game(game)
                        .get()
                        .user__email,
                    ).to_dict()
                )

            case "kick":
                UserGame.objects.for_game(game).for_user(content["email"]).get().kill()
                self.send_json(Kick(msg="You Lose!").to_dict())
