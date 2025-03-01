"""
effects.py
Ian Kollipara <ian.kollipara@cune.edu>
2025-03-01

Effects
"""

from __future__ import annotations

from game.models import Deck, Game, UserGame
import random




def skip(game: Game) -> str:
    # ~50 rarity, medium rarity
    # Pass the kernel

    player = game.players.filter(is_active=True, killed_at__isnull=True).get()
    player.is_active = False
    next_player = (
        game.players.filter(is_active=True, killed_at__isnull=True).get().next_player
    )
    next_player.is_active = True

    player.save()
    next_player.save()

    return "You passed the Kernel!"


def lucky_turn(game: Game) -> str:
    # ~50 rarity, medium rarity
    # Pinch of lucky salt

    # Increases rarity of all cards 
    # i.e. higher chances of drawing a card in general, and rarier cards become even more common
    game.chance_to_draw = game.chance_to_draw + 5

    return "You applied a pinch of salt and now have a Lucky Turn!"



def super_lucky_turn(game: Game) -> str:
    # ~20, higher rarity
    # Lucky Butter Waterfall
    
    # Like a lucky_turn but increases more
    game.chance_to_draw = 100


    return "You applied an extraordinary amount of butter and now have a Super Lucky Turn!"


def burnt_rough_estimator(game:Game) -> str:
    # ~ 80 
    # 


    if game.chance_to_draw <= 10:
        return "Less than 10 clicks till the next burnt popcorn!"
    else:
        return "More than 10 clicks till the next burnt popcorn!"

    


def burnt_good_estimator(game:Game) -> str:
    # ~ 30

    if game.chance_to_draw <= 5:
        return "Less than 5 clicks till the next burnt popcorn!"
    elif game.chance_to_draw <= 10:
        return "Less than 10 clicks till the next burnt popcorn!"
    elif game.chance_to_draw <= 15:
        return "Less than 15 clicks till the next burnt popcorn!"
    elif game.chance_to_draw <= 20:
        return "Less than 20 clicks till the next burnt popcorn!"
    else:
        return "More than 20 clicks till the next burnt popcorn!"



def burnt_tracker(game: Game) -> str:
    # ~5~10 very high rarity
    
    # Tells you how many cards till the next pop
    # Could maybe add it to persist till a shuffle or till that pop

    return f"There are {game.until_next_pop} clicks till the next burnt popcorn!"


def shuffle(game: Game) -> str:
    # ~20
    # shake the kernels
    
    # set the numbers of pops from the number of active players - 1 till the amount of cards left in the deck
    game.until_next_pop = random.randint(
        1,
        Deck.objects.cards_left_for_game(game))

    game.save(update_fields=["until_next_pop"])

    return "You have shaked up the burnt popcorn!"


def delay_the_burnt(game: Game) -> str:
    # ~20 high rarity
    # open the door for a little 
    
    if Deck.objects.cards_left_for_game(game) > 5:
        game.until_next_pop += 5 
        game.save(update_fields=["until_next_pop"])
        return "You have opened the mircowave door and delayed the burn by 5 clicks!"
    
    else:
        return "Unable to open the mircowave door and unable delay the burn!!!"
    


def extended_delay_the_burnt(game: Game) -> str:
    # ~10 super high rarity
    # open the door for a long while 
    
    if Deck.objects.cards_left_for_game(game) > 20:
        game.until_next_pop += 20 
        game.save(update_fields=["until_next_pop"])
        return "You have opened the mircowave door and delayed the burn by 20 clicks!"
    
    elif Deck.objects.cards_left_for_game(game) > 15:
        game.until_next_pop += 15
        game.save(update_fields=["until_next_pop"])
        return "You have opened the mircowave door and delayed the burn by 15 clicks!"
    
    elif Deck.objects.cards_left_for_game(game) > 10:
        game.until_next_pop += 10
        game.save(update_fields=["until_next_pop"])
        return "You have opened the mircowave door and delayed the burn by 10 clicks!"

    elif Deck.objects.cards_left_for_game(game) > 5:
        game.until_next_pop += 5
        game.save(update_fields=["until_next_pop"])
        return "You have opened the mircowave door and delayed the burn by 5 clicks!"
    
    else:
        return "Unable to open the mircowave door and unable delay the burn!!!"





"""

def time_travel(game: Game) -> str:
    # ~5-10 very high rarity
    
    # Essentially a defuse, could call pop_evansion

    return "You have avoided a Pop!"

    
targeted unlucky turn


def crystal_ball(game: Game) -> str:
    # ~50 medium rarity
    
    # See the next 5 cards

    return "Here are the next 5 clicks!"


def super_crystal_ball(game: Game) -> str:
    # ~20 high rarity
    
    # See the next 20 cards

    return "Here are the next 20 clicks!"

"""