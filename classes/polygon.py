from dataclasses import dataclass, field, replace
from typing import Any
from math import exp
from typing import Self
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.patches import Polygon as PolygonPatch
from random import gauss

from CONSTANTS import (
    MAX_RADIUS,
    MIN_RADIUS,
    SIDES_POLYGONS,
    SIGMA_ANGLE,
    SIGMA_RADIUS,
    SIGMA_RGB,
    SIGMA_X,
    SIGMA_Y,
)


def clamp(value: int, lowest: int, highest: int) -> int:
    return min(max(value, lowest), highest)


@dataclass
class Polygon:
    x: int
    y: int
    rgb: tuple[int, int, int]
    angle: int
    radius: int
    n_sides: int = SIDES_POLYGONS
    mask_cache: dict[  # one mask per image size, never invalidated
        tuple[int, int], tuple[npt.NDArray[np.bool_], tuple[slice, slice]]
    ] = field(default_factory=dict, init=False, repr=False, compare=False)

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        return self  # never modified in place, so copies can share it

    def boolean_mask_maker(
        self, width: int, height: int
    ) -> tuple[npt.NDArray[np.bool_], tuple[slice, slice]]:
        cached = self.mask_cache.get((width, height))
        if cached is not None:
            return cached
        x_start, x_end, y_start, y_end = self.starting_ending_coordinates(width, height)

        corners_abscissa = self.corners_abscissa_maker()
        corners_ordinate = self.corners_ordinate_maker()
        corners_vectors_x = self.corners_vectors_maker(corners_abscissa)
        corners_vectors_y = self.corners_vectors_maker(corners_ordinate)
        x_points = np.arange(x_start, x_end)[None, :]
        y_points = np.arange(y_start, y_end)[:, None]
        boolean_mask = np.ones((y_points.shape[0], x_points.shape[1]), dtype=bool)
        for index in range(self.n_sides):
            det = corners_vectors_x[index] * (
                y_points - corners_ordinate[index]
            ) - corners_vectors_y[index] * (x_points - corners_abscissa[index])
            boolean_mask = boolean_mask & (det >= 0)
        result = (boolean_mask, (slice(y_start, y_end), slice(x_start, x_end)))
        self.mask_cache[(width, height)] = result
        return result

    def starting_ending_coordinates(
        self, width: int, height: int
    ) -> tuple[int, int, int, int]:
        x_start = min(max(self.x - self.radius, 0), width)
        x_end = min(max(self.x + self.radius + 1, 0), width)
        y_start = min(max(self.y - self.radius, 0), height)
        y_end = min(max(self.y + self.radius + 1, 0), height)
        return x_start, x_end, y_start, y_end

    def corners_abscissa_maker(self) -> list[float]:
        return [
            self.x
            + self.radius
            * np.cos((index * 360 / self.n_sides + self.angle) * np.pi / 180)
            for index in range(self.n_sides)
        ]

    def corners_ordinate_maker(self) -> list[float]:
        return [
            self.y
            + self.radius
            * np.sin((index * 360 / self.n_sides + self.angle) * np.pi / 180)
            for index in range(self.n_sides)
        ]

    def corners_vectors_maker(self, corners_coordinates: list[float]) -> list[float]:
        return [
            corners_coordinates[(index + 1) % self.n_sides] - corners_coordinates[index]
            for index in range(self.n_sides)
        ]

    def mutate_polygon(self, width: int, height: int, sigma_scale: float = 1.0) -> Self:
        x = clamp(round(gauss(self.x, SIGMA_X * sigma_scale)), 0, width - 1)
        y = clamp(round(gauss(self.y, SIGMA_Y * sigma_scale)), 0, height - 1)
        r = clamp(round(gauss(self.rgb[0], SIGMA_RGB * sigma_scale)), 0, 255)
        g = clamp(round(gauss(self.rgb[1], SIGMA_RGB * sigma_scale)), 0, 255)
        b = clamp(round(gauss(self.rgb[2], SIGMA_RGB * sigma_scale)), 0, 255)
        rgb = (r, g, b)
        angle = round(gauss(self.angle, SIGMA_ANGLE * sigma_scale)) % 360  # circular
        radius = round(self.radius * exp(gauss(0, SIGMA_RADIUS * sigma_scale)))
        radius = clamp(radius, MIN_RADIUS, MAX_RADIUS)
        return replace(self, x=x, y=y, rgb=rgb, angle=angle, radius=radius)

    def draw_on(self, ax: Axes) -> None:
        corners = list(
            zip(self.corners_abscissa_maker(), self.corners_ordinate_maker())
        )
        color = tuple(channel / 255 for channel in self.rgb)
        ax.add_patch(PolygonPatch(corners, closed=True, facecolor=color))
