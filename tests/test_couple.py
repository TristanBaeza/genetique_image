import random

from classes.contender import Contender
from classes.couple import Couple
from CONSTANTS import N_POLYGONS_TO_MUTATE

WIDTH, HEIGHT = 134, 200


def make_couple(score_1: int, score_2: int) -> Couple:
    first = Contender(x_max=WIDTH, y_max=HEIGHT, n_polygons=10)
    second = Contender(x_max=WIDTH, y_max=HEIGHT, n_polygons=10)
    first.score, second.score = score_1, score_2
    return Couple(first, second)


def test_choose_best_parent():
    couple = make_couple(10, 20)
    assert couple.choose_best_parent() is couple.contender_1  # lowest score wins
    couple = make_couple(20, 10)
    assert couple.choose_best_parent() is couple.contender_2
    couple = make_couple(10, 10)
    assert couple.choose_best_parent() is couple.contender_1  # tie: the first one


def test_new_child():
    couple = make_couple(10, 20)
    parent = couple.contender_1
    child = couple.new_child(parent)

    assert child is not parent
    assert child.polygons_list is not parent.polygons_list
    assert child.polygons_list == parent.polygons_list  # polygons are shared

    before = list(parent.polygons_list)
    couple.mutate_child(child)
    assert parent.polygons_list == before  # sharing them is safe
    assert child.score == 0  # not evaluated yet
    assert parent.score == 10


def test_mutate_child():
    random.seed(0)
    couple = make_couple(10, 20)
    child = couple.contender_1
    before = list(child.polygons_list)

    returned = couple.mutate_child(child)

    assert returned is child  # mutated in place
    changed = [
        index
        for index, polygon in enumerate(child.polygons_list)
        if polygon is not before[index]
    ]
    assert len(changed) == N_POLYGONS_TO_MUTATE  # distinct indices, never twice
    for index, polygon in enumerate(child.polygons_list):
        if index not in changed:
            assert polygon is before[index]
