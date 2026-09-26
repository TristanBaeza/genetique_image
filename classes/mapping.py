from copy import deepcopy
from dataclasses import dataclass, field
from random import shuffle
from CONSTANTS import (
    CONTENDERS_AMOUNT,
    IMAGE_PATH,
    N_EPOCHS,
    SIGMA_DECAY,
    SIGMA_FINAL_SCALE,
    SNAPSHOT_EVERY,
    TARGET_HEIGHT,
)
from PIL import Image
import numpy as np
import numpy.typing as npt

from classes.contender import Contender
from classes.couple import Couple


@dataclass
class Mapping:
    height: int = TARGET_HEIGHT
    n_contenders: int = CONTENDERS_AMOUNT
    img: npt.NDArray[np.uint8] = field(init=False, repr=False, compare=False)
    width: int = field(init=False)
    contenders_list: list[Contender] = field(init=False, repr=False)
    history: list[tuple[int, Contender]] = field(  # snapshots for the Viewer
        init=False, repr=False, default_factory=list
    )

    def __post_init__(self) -> None:
        img, width = self.loading_image()
        self.img = img
        self.width = width
        self.contenders_list = self.contenders_initialization()

    def loading_image(self) -> tuple[npt.NDArray[np.uint8], int]:
        img = Image.open(IMAGE_PATH).convert("RGB")
        width = round(img.width * self.height / img.height)
        img = img.resize((width, self.height), Image.Resampling.LANCZOS)
        img = np.asarray(img)
        return img, width

    def contenders_initialization(self) -> list[Contender]:
        contenders_list = []
        for _ in range(self.n_contenders):
            contenders_list.append(Contender(self.width, self.height))
        return contenders_list

    def best_contender(self) -> Contender:
        for contender in self.contenders_list:
            if contender.score == 0:
                contender.scoring(self.img)
        return min(self.contenders_list, key=lambda contender: contender.score)

    def sigma_scale(self, epoch: int) -> float:
        if not SIGMA_DECAY:
            return 1.0
        return SIGMA_FINAL_SCALE ** (epoch / max(N_EPOCHS - 1, 1))  # 1.0 -> final

    def one_round_tournament(self, sigma_scale: float = 1.0) -> None:
        for contender in self.contenders_list:
            if contender.score == 0:
                contender.scoring(self.img)
        self.contenders_list.sort(key=lambda contender: contender.score)
        contenders_list_length = self.n_contenders // 2
        self.contenders_list = self.contenders_list[:contenders_list_length]
        shuffle(self.contenders_list)
        for index in range(contenders_list_length):
            couple = Couple(
                self.contenders_list[index],
                self.contenders_list[(index + 1) % contenders_list_length],
            )
            self.contenders_list.append(
                couple.mutate_child(
                    couple.new_child(couple.choose_best_parent()), sigma_scale
                )
            )

    def tournament(self) -> None:
        for epoch in range(N_EPOCHS):
            self.one_round_tournament(self.sigma_scale(epoch))
            if epoch % SNAPSHOT_EVERY == 0 or epoch == N_EPOCHS - 1:
                best = self.best_contender()
                self.history.append((epoch, deepcopy(best)))
                print(f"epoch {epoch:4d} | best score {best.score / 1e6:8.2f}M")
