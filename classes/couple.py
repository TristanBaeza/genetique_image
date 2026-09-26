from dataclasses import dataclass
from copy import deepcopy
from random import sample

from CONSTANTS import N_POLYGONS_TO_MUTATE
from classes.contender import Contender


@dataclass
class Couple:
    contender_1: Contender
    contender_2: Contender

    def choose_best_parent(self) -> Contender:
        if self.contender_1.score <= self.contender_2.score:
            return self.contender_1
        return self.contender_2

    def new_child(self, contender: Contender) -> Contender:
        new_child = deepcopy(contender)  # polygons are shared, see __deepcopy__
        new_child.score = 0
        return new_child

    def mutate_child(self, child: Contender, sigma_scale: float = 1.0) -> Contender:
        number_of_polygons = len(child.polygons_list)
        for index in sample(range(number_of_polygons), N_POLYGONS_TO_MUTATE):
            child.polygons_list[index] = child.polygons_list[index].mutate_polygon(
                child.x_max, child.y_max, sigma_scale
            )
        return child
