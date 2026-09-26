import random
from math import pi, sin

import numpy as np
import pytest
from matplotlib.figure import Figure
from matplotlib.patches import Polygon as PolygonPatch

from classes.polygon import Polygon, clamp
from CONSTANTS import MAX_RADIUS, MIN_RADIUS

WIDTH, HEIGHT = 134, 200


def make_polygon(x=67, y=100, angle=0, radius=20, n_sides=3) -> Polygon:
    return Polygon(x=x, y=y, rgb=(0, 0, 0), angle=angle, radius=radius, n_sides=n_sides)


def full_image_mask(polygon: Polygon) -> np.ndarray:
    """Same edge test, but over the whole image and without any clipping."""
    corners_x = polygon.corners_abscissa_maker()
    corners_y = polygon.corners_ordinate_maker()
    vectors_x = polygon.corners_vectors_maker(corners_x)
    vectors_y = polygon.corners_vectors_maker(corners_y)
    ys, xs = np.ogrid[0:HEIGHT, 0:WIDTH]
    mask = np.ones((HEIGHT, WIDTH), dtype=bool)
    for k in range(polygon.n_sides):
        det = vectors_x[k] * (ys - corners_y[k]) - vectors_y[k] * (xs - corners_x[k])
        mask &= det >= 0
    return mask


def test_clamp():
    assert clamp(5, 0, 10) == 5  # inside: untouched
    assert clamp(-3, 0, 10) == 0
    assert clamp(42, 0, 10) == 10
    assert clamp(0, 0, 10) == 0  # bounds are included
    assert clamp(10, 0, 10) == 10


def test_boolean_mask_maker():
    polygon = make_polygon(x=67, y=100, angle=0, radius=20)
    mask, (y_slice, x_slice) = polygon.boolean_mask_maker(WIDTH, HEIGHT)
    placed = np.zeros((HEIGHT, WIDTH), dtype=bool)
    placed[y_slice, x_slice] = mask

    assert mask.dtype == bool
    assert placed[100, 67], "the center must be inside the polygon"
    assert not placed[100, 55], "a point left of the left edge is outside"

    n = polygon.n_sides  # pixel count vs theoretical area, within one perimeter
    area = n / 2 * polygon.radius**2 * sin(2 * pi / n)
    perimeter = n * 2 * polygon.radius * sin(pi / n)
    assert abs(mask.sum() - area) <= perimeter

    # Clipping only removes pixels outside the image, wherever the polygon is.
    for x, y in [(3, 100), (131, 100), (67, 2), (67, 198), (1, 1), (133, 199),
                 (-40, 100), (200, 100), (67, 300)]:
        polygon = make_polygon(x=x, y=y, angle=30, radius=20)
        mask, (y_slice, x_slice) = polygon.boolean_mask_maker(WIDTH, HEIGHT)
        placed = np.zeros((HEIGHT, WIDTH), dtype=bool)

        assert mask.shape == placed[y_slice, x_slice].shape, f"x={x}, y={y}"
        placed[y_slice, x_slice] = mask
        assert np.array_equal(placed, full_image_mask(polygon)), f"x={x}, y={y}"

    cached, _ = polygon.boolean_mask_maker(WIDTH, HEIGHT)
    assert cached is mask  # same object: computed once, then reused
    other, _ = polygon.boolean_mask_maker(WIDTH + 1, HEIGHT)
    assert other is not mask  # one entry per image size


def test_deepcopy():
    from copy import deepcopy

    polygon = make_polygon()
    assert deepcopy(polygon) is polygon  # shared, never modified in place


@pytest.mark.parametrize(
    "x, y, expected",
    [
        (67, 100, (47, 88, 80, 121)),  # fully inside the image
        (5, 100, (0, 26, 80, 121)),  # overflows on the left
        (130, 100, (110, 134, 80, 121)),  # overflows on the right
        (67, 5, (47, 88, 0, 26)),  # overflows at the top
        (67, 195, (47, 88, 175, 200)),  # overflows at the bottom
        (-40, 100, (0, 0, 80, 121)),  # fully on the left: empty slice
        (200, 100, (134, 134, 80, 121)),  # fully on the right: empty slice
    ],
)
def test_starting_ending_coordinates(x, y, expected):
    polygon = make_polygon(x=x, y=y, radius=20)
    assert polygon.starting_ending_coordinates(WIDTH, HEIGHT) == expected


@pytest.mark.parametrize(
    "n_sides, angle, expected",
    [
        (4, 0, [60, 50, 40, 50]),  # square: right, bottom, left, top
        (4, 90, [50, 40, 50, 60]),  # the same square, quarter turn
        (3, 0, [60, 45, 45]),  # triangle: cos(0°), cos(120°), cos(240°)
    ],
)
def test_corners_abscissa_maker(n_sides, angle, expected):
    polygon = make_polygon(x=50, y=80, angle=angle, radius=10, n_sides=n_sides)
    assert polygon.corners_abscissa_maker() == pytest.approx(expected)


@pytest.mark.parametrize(
    "n_sides, angle, expected",
    [
        (4, 0, [80, 90, 80, 70]),  # y increases downwards in an image
        (4, 90, [90, 80, 70, 80]),
        (3, 0, [80, 80 + 5 * 3**0.5, 80 - 5 * 3**0.5]),
    ],
)
def test_corners_ordinate_maker(n_sides, angle, expected):
    polygon = make_polygon(x=50, y=80, angle=angle, radius=10, n_sides=n_sides)
    assert polygon.corners_ordinate_maker() == pytest.approx(expected)


def test_corners_vectors_maker():
    polygon = make_polygon(n_sides=4)
    vectors = polygon.corners_vectors_maker([0.0, 1.0, 3.0, 6.0])

    assert vectors == [1.0, 2.0, 3.0, -6.0]  # the last one returns to the first
    assert sum(vectors) == 0  # the polygon is closed


def test_mutate_polygon():
    random.seed(0)  # reproducible draws
    parent = Polygon(  # close to every bound, to exercise the clamping
        x=1, y=HEIGHT - 2, rgb=(2, 128, 253), angle=355, radius=MIN_RADIUS, n_sides=6
    )
    children = [parent.mutate_polygon(WIDTH, HEIGHT) for _ in range(2000)]

    for child in children:
        assert 0 <= child.x < WIDTH
        assert 0 <= child.y < HEIGHT
        assert MIN_RADIUS <= child.radius <= MAX_RADIUS
        assert 0 <= child.angle < 360
        assert all(0 <= channel <= 255 for channel in child.rgb)
        assert child.n_sides == parent.n_sides  # untouched fields are kept

    assert (parent.x, parent.y, parent.rgb, parent.angle, parent.radius) == (
        1,
        HEIGHT - 2,
        (2, 128, 253),
        355,
        MIN_RADIUS,
    )  # the parent itself is never modified
    assert any(child.angle < 180 for child in children)  # the angle wraps around
    assert any(child.angle > 180 for child in children)

    random.seed(0)
    wide = [parent.mutate_polygon(WIDTH, HEIGHT, 1.0) for _ in range(500)]
    random.seed(0)
    narrow = [parent.mutate_polygon(WIDTH, HEIGHT, 0.1) for _ in range(500)]
    spread = lambda polygons: max(p.y for p in polygons) - min(p.y for p in polygons)
    assert spread(narrow) < spread(wide)  # sigma_scale shrinks every step


def test_draw_on():
    ax = Figure().add_subplot()  # Figure, not pyplot: no window, nothing to close
    polygon = Polygon(x=50, y=80, rgb=(255, 0, 51), angle=0, radius=10, n_sides=4)
    polygon.draw_on(ax)

    assert len(ax.patches) == 1
    patch = ax.patches[0]
    assert isinstance(patch, PolygonPatch)
    expected = list(
        zip(polygon.corners_abscissa_maker(), polygon.corners_ordinate_maker())
    )
    assert patch.get_xy()[:-1] == pytest.approx(np.array(expected))  # last = first
    assert patch.get_facecolor()[:3] == pytest.approx((1.0, 0.0, 0.2))  # 0-1, not 0-255
