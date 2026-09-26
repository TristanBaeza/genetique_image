from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.widgets import Slider

from classes.contender import Contender


@dataclass
class Viewer:
    img: npt.NDArray[np.uint8]
    history: list[tuple[int, Contender]]
    slider: Slider = field(init=False, repr=False)  # kept, or it stops responding

    def draw_contender(self, ax: Axes, index: int) -> None:
        epoch, contender = self.history[index]
        ax.clear()
        ax.set_xlim(-0.5, contender.x_max - 0.5)
        ax.set_ylim(contender.y_max - 0.5, -0.5)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"epoch {epoch} - score {contender.score / 1e6:.2f}M")
        for polygon in contender.polygons_list:
            polygon.draw_on(ax)

    def figure_maker(self) -> Figure:
        fig, (target_ax, best_ax) = plt.subplots(1, 2, figsize=(9, 5))
        target_ax.imshow(self.img)
        target_ax.set_title("target")
        target_ax.set_xticks([])
        target_ax.set_yticks([])
        fig.subplots_adjust(bottom=0.2)  # room for the slider

        last = len(self.history) - 1
        self.slider = Slider(
            ax=fig.add_axes((0.2, 0.08, 0.6, 0.04)),
            label="snapshot",
            valmin=0,
            valmax=max(last, 1),  # a slider needs valmin < valmax
            valinit=last,
            valstep=1,
        )
        self.slider.on_changed(
            lambda value: (
                self.draw_contender(best_ax, int(value)),
                fig.canvas.draw_idle(),
            )
        )
        self.draw_contender(best_ax, last)
        return fig

    def show(self) -> None:
        self.figure_maker()
        plt.show()
