from classes.polygon import Polygon
from dataclasses import dataclass, field
from CONSTANTS import MAX_RADIUS, MIN_RADIUS, POLYGONS_AMOUNT
from random import randint
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import numpy.typing as npt


@dataclass
class Contender:
    x_max: int
    y_max: int
    n_polygons: int = POLYGONS_AMOUNT
    polygons_list: list[Polygon] = field(init=False, repr=False)
    score: int = 0

    def __post_init__(self) -> None:
        polygons_list = []
        for _ in range(self.n_polygons):
            polygons_list.append(self.randomise_polygon())
        self.polygons_list = polygons_list

    def randomise_polygon(self) -> Polygon:
        return Polygon(
            x=randint(0, self.x_max - 1),
            y=randint(0, self.y_max - 1),
            rgb=(randint(0, 255), randint(0, 255), randint(0, 255)),
            angle=randint(0, 359),
            radius=randint(MIN_RADIUS, MAX_RADIUS),
        )

    def scoring(self, img: npt.NDArray[np.uint8]) -> None:
        height, width, _ = img.shape
        created_grid = np.zeros((height, width, 3), dtype=np.uint8)
        for polygon in self.polygons_list:
            boolean_mask, (y_slice, x_slice) = polygon.boolean_mask_maker(width, height)
            region = created_grid[y_slice, x_slice]
            region[boolean_mask] = polygon.rgb
        difference = img.astype(np.int64) - created_grid.astype(np.int64)
        self.score = int(np.sum(difference**2))

    def plot(self) -> Figure:
        fig, ax = plt.subplots()
        ax.set_xlim(-0.5, self.x_max - 0.5)
        ax.set_ylim(self.y_max - 0.5, -0.5)
        ax.set_aspect("equal")
        for polygon in self.polygons_list:
            polygon.draw_on(ax)
        return fig
