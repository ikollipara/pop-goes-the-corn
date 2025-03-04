"""
make_cards.py
Aaron Cumming
2025-03-01
"""

[
  {
    "model": "game.card",
    "pk": 1,
    "fields": {
      "name": "Pass the Kernel",
      "description": "Ends your turn without you having to press the kernel.",
      "rarity": 40,
      "effect": "skip",
      "image": "skip.jpg",
    }
  },
  {
    "model": "game.card",
    "pk": 2,
    "fields": {
      "name": "Pinch of lucky salt",
      "description": "Applies salt that increases your chance to draw a card with every click.",
      "rarity": 70,
      "effect": "lucky_turn",
      "image": "salt.jpg",
    }
  },
    {
    "model": "game.card",
    "pk": 3,
    "fields": {
      "name": "Lucky Butter Waterfall",
      "description": "Applies butter that guarantees that you can draw a card with every click.",
      "rarity": 20,
      "effect": "super_lucky_turn",
      "image": "butter.jpg",
    }
  },
    {
    "model": "game.card",
    "pk": 4,
    "fields": {
      "name": "Burnt Rough Estimator",
      "description": "Roughly estimates till when the next burnt popcorn is.",
      "rarity": 70,
      "effect": "burnt_rough_estimator",
      "image": "estimator rough.jpg",
    }
  },
    {
    "model": "game.card",
    "pk": 5,
    "fields": {
      "name": "Burnt Good Estimator",
      "description": "Estimates till when the next burnt popcorn is.",
      "rarity": 30,
      "effect": "burnt_good_estimator",
      "image": "estimator good.jpg",
    }
  },
    {
    "model": "game.card",
    "pk": 6,
    "fields": {
      "name": "Burnt Tracker",
      "description": "Gives you exactly how many clicks till the next burnt popcorn.",
      "rarity": 5,
      "effect": "burnt_tracker",
      "image": "tracker.jpg",
    }
  },
    {
    "model": "game.card",
    "pk": 7,
    "fields": {
      "name": "Shake the Kernels",
      "description": "Shakes and shuffles up the burnt popcorn",
      "rarity": 80,
      "effect": "shuffle",
      "image": "shaking popcorn.jpg",
    }
  },
    {
    "model": "game.card",
    "pk": 8,
    "fields": {
      "name": "Open the Door for a Little",
      "description": "If possible, opens the mircowave door and delays the burn by 5 clicks",
      "rarity": 20,
      "effect": "delay_the_burnt",
      "image": "mircowave door open a little.jpg",
    }
  },
    {
    "model": "game.card",
    "pk": 9,
    "fields": {
      "name": "Open the Door for a Long While",
      "description": "If possible, opens the mircowave door and delays the burn for up to 20 clicks",
      "rarity": 10,
      "effect": "extended_delay_the_burnt",
      "image": "mircowave door open a long while.jpg",
    }
  },
]

"""
tailwind

make a card snippet and incluce this
    {% static card.image %}
    """