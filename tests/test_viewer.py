import matplotlib.pyplot as plt
import numpy as np
import pytest

from classes.contender import Contender
from classes.viewer import Viewer

WIDTH, HEIGHT = 30, 40


@pytest.fixture
def viewer():
    img = np.full((HEIGHT, WIDTH, 3), 100, dtype=np.uint8)
    history = []
    for epoch in (0, 10, 20):
        contender = Contender(x_max=WIDTH, y_max=HEIGHT, n_polygons=5)
        contender.score = 1_000_000 * (30 - epoch)
        history.append((epoch, contender))
    return Viewer(img, history)


def test_draw_contender(viewer):
    ax = plt.figure().add_subplot()
    viewer.draw_contender(ax, 1)

    assert len(ax.patches) == 5  # one patch per polygon
    assert "epoch 10" in ax.get_title()
    assert ax.get_xlim() == (-0.5, WIDTH - 0.5)
    assert ax.get_ylim() == (HEIGHT - 0.5, -0.5)  # y points down, as with imshow

    viewer.draw_contender(ax, 2)
    assert len(ax.patches) == 5  # replaced, not stacked
    assert "epoch 20" in ax.get_title()

    plt.close("all")


def test_figure_maker(viewer):
    fig = viewer.figure_maker()
    target_ax, best_ax = fig.axes[0], fig.axes[1]

    assert len(target_ax.images) == 1  # the target image
    assert viewer.slider.val == len(viewer.history) - 1  # starts on the last one
    assert "epoch 20" in best_ax.get_title()

    viewer.slider.set_val(0)
    assert "epoch 0" in best_ax.get_title()  # moving it redraws

    plt.close(fig)


def test_show(viewer, monkeypatch):
    shown = []
    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: shown.append(True))
    viewer.show()

    assert shown == [True]
    assert plt.get_fignums()  # the figure was built before showing it
    plt.close("all")
