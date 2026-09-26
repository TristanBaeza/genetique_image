from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import classes.mapping as mapping_module
from classes.contender import Contender
from classes.mapping import Mapping
from CONSTANTS import IMAGE_PATH

ROOT = Path(__file__).parent.parent
HEIGHT = 100
N_CONTENDERS = 5


@pytest.fixture(scope="module")
def mapping():
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.chdir(ROOT)  # Mapping opens its image by a relative path
        yield Mapping(height=HEIGHT, n_contenders=N_CONTENDERS)


@pytest.fixture
def small_mapping():
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.chdir(ROOT)
        yield Mapping(height=40, n_contenders=20)  # fresh: these tests mutate it


def test_post_init(mapping):
    assert mapping.img.shape == (mapping.height, mapping.width, 3)
    assert len(mapping.contenders_list) == N_CONTENDERS
    assert mapping.history == []


def test_loading_image(mapping):
    img, width = mapping.loading_image()
    original_width, original_height = Image.open(ROOT / IMAGE_PATH).size

    assert img.dtype == np.uint8
    assert img.shape == (HEIGHT, width, 3)  # RGB, no alpha channel
    assert width == round(original_width * HEIGHT / original_height)  # same ratio


def test_contenders_initialization(mapping):
    contenders = mapping.contenders_initialization()

    assert len(contenders) == N_CONTENDERS
    for contender in contenders:
        assert isinstance(contender, Contender)
        assert contender.x_max == mapping.width
        assert contender.y_max == mapping.height


def test_best_contender(small_mapping):
    population = small_mapping.contenders_list
    best = small_mapping.best_contender()

    assert all(contender.score > 0 for contender in population)  # all scored
    assert best.score == min(contender.score for contender in population)
    assert best in population


def test_sigma_scale(small_mapping, monkeypatch):
    monkeypatch.setattr(mapping_module, "SIGMA_DECAY", True)
    monkeypatch.setattr(mapping_module, "SIGMA_FINAL_SCALE", 0.25)
    monkeypatch.setattr(mapping_module, "N_EPOCHS", 101)

    assert small_mapping.sigma_scale(0) == 1.0
    assert small_mapping.sigma_scale(50) == pytest.approx(0.5)
    assert small_mapping.sigma_scale(100) == pytest.approx(0.25)  # last epoch
    scales = [small_mapping.sigma_scale(epoch) for epoch in range(101)]
    assert scales == sorted(scales, reverse=True)

    monkeypatch.setattr(mapping_module, "SIGMA_DECAY", False)
    assert small_mapping.sigma_scale(500) == 1.0  # the switch turns it off


def test_one_round_tournament(small_mapping):
    best_before = small_mapping.best_contender().score

    small_mapping.one_round_tournament()
    population = small_mapping.contenders_list

    assert len(population) == small_mapping.n_contenders  # size is kept
    assert len({id(contender) for contender in population}) == len(population)
    for contender in population:
        contender.scoring(small_mapping.img)  # a child carries its parent's score
    assert min(contender.score for contender in population) <= best_before  # elitism


def test_tournament(small_mapping, monkeypatch):
    rounds = 0
    scales = []

    def counting_round(self, sigma_scale=1.0):
        nonlocal rounds
        rounds += 1
        scales.append(sigma_scale)

    monkeypatch.setattr(mapping_module, "N_EPOCHS", 3)
    monkeypatch.setattr(mapping_module, "SNAPSHOT_EVERY", 2)
    monkeypatch.setattr(Mapping, "one_round_tournament", counting_round)
    small_mapping.tournament()

    assert rounds == 3
    assert scales == [small_mapping.sigma_scale(epoch) for epoch in range(3)]
    assert [epoch for epoch, _ in small_mapping.history] == [0, 2]  # plus the last
    for _, contender in small_mapping.history:
        assert contender.score > 0
