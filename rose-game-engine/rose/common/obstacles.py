""" Game obstacles """

import random

NONE = ""  # NOQA
HOTDOG = "hotdog"  # NOQA
TOMATO = "tomato"  # NOQA
BURGER = "burger"  # NOQA
SALAD = "salad"  # NOQA
PIZZA = "pizza"  # NOQA
BROCOLI = "brocoli"  # NOQA

ALL = (NONE, HOTDOG, TOMATO, BURGER, SALAD, PIZZA, BROCOLI)


def get_random_obstacle():
    return random.choice(ALL)
