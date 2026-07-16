from rose.common.obstacles import (
    NONE,
    HOTDOG,
    TOMATO,
    BURGER,
    SALAD,
    PIZZA,
    BROCOLI,
    ALL,
    get_random_obstacle,
)


def test_constants():
    assert NONE == ""
    assert HOTDOG == "hotdog"
    assert TOMATO == "tomato"
    assert BURGER == "burger"
    assert SALAD == "salad"
    assert PIZZA == "pizza"
    assert BROCOLI == "brocoli"


def test_all_constant():
    assert ALL == (NONE, HOTDOG, TOMATO, BURGER, SALAD, PIZZA, BROCOLI)


def test_get_random_obstacle():
    # This test checks if the function returns a valid obstacle
    obstacle = get_random_obstacle()
    assert obstacle in ALL
