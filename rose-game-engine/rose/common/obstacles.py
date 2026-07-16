""" Game obstacles """

import random

NONE = ""  # NOQA
HOTDOG = "hotdog"  # NOQA
TOMATO = "tomato"  # NOQA
BURGER = "burger"  # NOQA
SALAD = "salad"  # NOQA
PIZZA = "pizza"  # NOQA
BROCOLI = "brocoli"  # NOQA
SAUCE = "sauce"  # NOQA

FOOD = (NONE, HOTDOG, TOMATO, BURGER, SALAD, PIZZA, BROCOLI)
ALL = FOOD + (SAUCE,)

SAUCE_CHANCE = 0.2


def get_random_obstacle():
    if random.random() < SAUCE_CHANCE:
        return SAUCE
    return random.choice(FOOD)
