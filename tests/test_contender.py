import random

import matplotlib.pyplot as plt
import numpy as np
import pytest

from classes.contender import Contender
from classes.polygon import Polygon
from CONSTANTS import MAX_RADIUS, MIN_RADIUS

WIDTH, HEIGHT = 134, 200


def test_post_init():
    contender = Contender(x_max=WIDTH, y_max=HEIGHT, n_polygons=10)
    assert len(contender.polygons_list) == 10
    assert all(isinstance(polygon, Polygon) for polygon in contender.polygons_list)


def test_randomise_polygon():
    random.seed(0)  # reproducible draws
    contender = Contender(x_max=WIDTH, y_max=HEIGHT, n_polygons=0)
    polygons = [contender.randomise_polygon() for _ in range(2000)]

    for polygon in polygons:
        assert 0 <= polygon.x < WIDTH  # the center is always an image pixel
        assert 0 <= polygon.y < HEIGHT
        assert MIN_RADIUS <= polygon.radius <= MAX_RADIUS
        assert 0 <= polygon.angle < 360
        assert len(polygon.rgb) == 3
        assert all(0 <= channel <= 255 for channel in polygon.rgb)

    assert min(polygon.x for polygon in polygons) == 0  # bounds are reached
    assert max(polygon.x for polygon in polygons) == WIDTH - 1
    assert max(polygon.y for polygon in polygons) == HEIGHT - 1


def test_scoring():
    def covering(rgb: tuple[int, int, int]) -> Polygon:
        return Polygon(x=WIDTH // 2, y=HEIGHT // 2, rgb=rgb, angle=0, radius=1000)

    grey = np.full((HEIGHT, WIDTH, 3), 100, dtype=np.uint8)
    contender = Contender(x_max=WIDTH, y_max=HEIGHT, n_polygons=0)

    contender.scoring(grey)
    assert contender.score == 100**2 * 3 * HEIGHT * WIDTH  # black canvas

    contender.polygons_list = [covering((100, 100, 100))]
    contender.scoring(grey)
    assert contender.score == 0  # exactly the right color

    contender.polygons_list = [covering((100, 100, 100)), covering((110, 90, 100))]
    contender.scoring(grey)
    assert contender.score == (10**2 + 10**2) * HEIGHT * WIDTH  # the last one wins

    white = np.full((HEIGHT, WIDTH, 3), 255, dtype=np.uint8)
    contender.polygons_list = []
    contender.scoring(white)
    assert contender.score == 255**2 * 3 * HEIGHT * WIDTH  # 5.2e9, beyond int32


def test_plot():
    contender = Contender(x_max=WIDTH, y_max=HEIGHT, n_polygons=10)
    fig = contender.plot()
    ax = fig.axes[0]

    assert len(ax.patches) == 10
    for patch, polygon in zip(ax.patches, contender.polygons_list):
        expected = tuple(channel / 255 for channel in polygon.rgb)
        assert patch.get_facecolor()[:3] == pytest.approx(expected)  # list order
    assert ax.get_xlim() == (-0.5, WIDTH - 0.5)
    assert ax.get_ylim() == (HEIGHT - 0.5, -0.5)  # y points down, as with imshow

    plt.close(fig)
