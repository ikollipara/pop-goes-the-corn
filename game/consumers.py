"""
consumers.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

WebSocketConsumer
"""

import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.template.loader import render_to_string

from game.models import Card, Deck, Game, Hand, UserGame

# Possible Responses


def join_payload(msg: str, alive_html: str):
    return {"type": "join", "msg": msg, "alive_html": alive_html}


def start_payload(msg: str, game: Game):
    return {
        "type": "start",
        "msg": msg,
        "game": game.to_json(),
    }


def click_payload():
    return {"type": "click"}


def sync_payload(game: Game, active_player_html: str):
    return {
        "type": "sync",
        "game": game.to_json(),
        "active_player_html": active_player_html,
    }


def end_turn_payload(msg: str, game: Game):
    return {
        "type": "end_turn",
        "msg": msg,
        "game": game.to_json(),
    }


def kill_payload(msg: str, game: Game, alive_html: str):
    return {
        "type": "kill",
        "msg": msg,
        "game": game.to_json(),
        "alive_html": alive_html,
    }


def play_card_payload(msg: str, game: Game, hand_html: str):
    return {
        "type": "play_card",
        "msg": msg,
        "game": game.to_json(),
        "hand_html": hand_html,
    }


def win_payload(msg: str):
    return {"type": "win", "msg": msg}


class GameWebsocketConsumer(JsonWebsocketConsumer):
    """
    # GameWebsocketCosumer.

    This pertains to most of the gameplay functionality.
    The game runs on this websocket consumer and its interactions
    with the frontend.
    """

    def connect(self):
        self.game_pk: int = self.scope["url_route"]["kwargs"]["pk"]

        async_to_sync(self.channel_layer.group_add)(self.game_pk, self.channel_name)
        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(self.game_pk, self.channel_name)

    def receive_json(self, content: dict, **kwargs):
        print(content)
        type_ = content["type"]
        game = Game.objects.get(pk=self.game_pk)

        match type_:
            case "join":
                # content = email
                alive_html = render_to_string(
                    "alive.html", {"alive_users": game.players.all()}
                )

                if not game.players.filter(user__email=content["email"]).exists():
                    game.join(content["email"])

                    async_to_sync(self.channel_layer.group_send)(
                        self.game_pk,
                        join_payload(
                            f"{content['email']} Successfully joined!", alive_html
                        ),
                    )

            case "start":
                # content = []
                game.start()

                async_to_sync(self.channel_layer.group_send)(
                    self.game_pk, start_payload("Game Started!", game)
                )

            case "click":
                # content = []
                has_popped = game.click()
                if not has_popped:
                    async_to_sync(self.channel_layer.group_send)(
                        self.game_pk, click_payload()
                    )
                else:
                    game.until_next_pop = random.randint(1, 100)
                    game.save()
                    alive_html = render_to_string(
                        "alive.html", {"alive_users": game.players.all()}
                    )
                    async_to_sync(self.channel_layer.group_send)(
                        self.game_pk,
                        kill_payload(
                            f"{game.to_json()['active_player']} has lost!",
                            game,
                            alive_html,
                        ),
                    )
                    if game.pops_left == 0:
                        async_to_sync(self.channel_layer.group_send)(
                            self.game_pk, win_payload("You have won!")
                        )

            case "end_turn":
                # content = game, currentPlayer
                game.advance_turn(content["currentPlayer"])
                game.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.game_pk,
                    end_turn_payload(
                        f"{game.to_json()['active_player']}'s turn!", game
                    ),
                )

    def join(self, msg):
        self.send_json(msg)

    def start(self, msg):
        self.send_json(msg)

    def click(self, msg):
        self.send_json(msg)

    def kill(self, msg):
        self.send_json(msg)

    def win(self, msg):
        self.send_json(msg)

    def end_turn(self, msg):
        self.send_json(msg)


# class GameWebsocketConsumer(JsonWebsocketConsumer):
#     def connect(self):
#         self.game_pk = self.scope["url_route"]["kwargs"]["pk"]
#         async_to_sync(self.channel_layer.group_add)(self.game_pk, self.channel_name)
#         self.accept()

#     def disconnect(self, code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(self.game_pk, self.channel_name)

#     def receive_json(self, content, **kwargs):
#         type_ = content["type"]
#         game = Game.objects.get(pk=self.game_pk)

#         match type_:
#             case "status":
#                 user_email = (
#                     UserGame.objects.is_active_for_game(game)
#                     .with_user_email()
#                     .get()
#                     .user__email
#                 )
#                 self.send_json(
#                     Status(
#                         game=game.to_json(),
#                         active_email=user_email,
#                     ).to_dict()
#                 )

#             case "join":
#                 print(content["email"])
#                 game.join(content["email"])
#                 self.send_json(Ok(msg="Successfully joined").to_dict())

#             case "start_game":
#                 game.start()
#                 self.send_json(
#                     Start(
#                         game=game.to_json(),
#                         active_email=UserGame.objects.with_user_email()
#                         .is_active_for_game(game)
#                         .get()
#                         .user__email,
#                     ).to_dict()
#                 )

#             case "click":
#                 game.click()
#                 if card := Deck.objects.get_drawn_card_for_game(game):
#                     Hand.objects.add_drawn_card(
#                         card=card, email=content["email"], game=game
#                     )
#                 self.send_json(Ok().to_dict())

#             case "play_card":
#                 Hand.objects.for_game(game).for_card(content["card"]).for_user_email(
#                     content["email"]
#                 ).delete()
#                 card = Card.objects.filter(pk=content["card"]).get()
#                 msg = card.do_effect(game)

#                 self.send_json(
#                     CardResolved(
#                         game=game.to_json(),
#                         active_email=UserGame.objects.with_user_email()
#                         .is_active_for_game(game)
#                         .get()
#                         .user__email,
#                         msg=msg,
#                     ).to_dict()
#                 )

#             case "end_turn":
#                 game.advance_turn()
#                 self.send_json(
#                     Start(
#                         game=game.to_json(),
#                         active_email=UserGame.objects.with_user_email()
#                         .is_active_for_game(game)
#                         .get()
#                         .user__email,
#                     ).to_dict()
#                 )

#             case "kick":
#                 UserGame.objects.for_game(game).for_user(content["email"]).get().kill()
#                 self.send_json(Kick(msg="You Lose!").to_dict())
