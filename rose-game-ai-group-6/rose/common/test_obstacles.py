from rose.common.obstacles import (
    NONE,
    HOTDOG,
    TOMATO,
    BURGER,
    SALAD,
    PIZZA,
    BROCOLI,
    SAUCE,
    FOOD,
    ALL,
    SAUCE_CHANCE,
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
    assert SAUCE == "sauce"


def test_food_constant():
    assert FOOD == (NONE, HOTDOG, TOMATO, BURGER, SALAD, PIZZA, BROCOLI)


def test_all_constant():
    assert ALL == (NONE, HOTDOG, TOMATO, BURGER, SALAD, PIZZA, BROCOLI, SAUCE)


def test_get_random_obstacle():
    # This test checks if the function returns a valid obstacle
    obstacle = get_random_obstacle()
    assert obstacle in ALL


def test_sauce_chance_is_approximately_correct():
    # Statistical sanity check: sauce should show up close to SAUCE_CHANCE
    # of the time over a large enough sample.
    samples = 10000
    sauce_count = sum(1 for _ in range(samples) if get_random_obstacle() == SAUCE)
    ratio = sauce_count / samples
    assert abs(ratio - SAUCE_CHANCE) < 0.03
