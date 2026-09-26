# genetique_image

<https://github.com/TristanBaeza/genetique_image>

Approximating an image with a stack of opaque regular polygons, optimised by
an evolutionary algorithm. The program starts from randomly drawn polygons,
mutates them generation after generation, and keeps the one that looks most
like the target image.

## Who wrote what

**The algorithm was written by the author of this repository**, without code
generation: the geometry of the regular polygons, the pixel mask computed from
cross products, the score, the mutations, the selection and the evolution
loop. Claude (Anthropic) advised on those parts — explanations, reviews,
comparative measurements of settings — but the code is the author's.

**The graphical part was written by Claude**: `classes/viewer.py`, the
`Polygon.draw_on` method, the `Contender.plot` method, and the tests in the
`tests/` folder.

## Running the project, step by step

### 1. Install Python

Python 3.13 or newer, from [python.org](https://www.python.org/downloads/).
On Windows, tick **"Add python.exe to PATH"** during the installation.

To check:

```powershell
python --version
```

### 2. Get the project

```powershell
git clone https://github.com/TristanBaeza/genetique_image.git
cd genetique_image
```

### 3. Create a virtual environment

A virtual environment is a folder holding its own copy of Python and its own
libraries. It keeps the versions installed for this project from clashing with
those of another one.

```powershell
python -m venv .venv
```

A `.venv` folder appears. It is not versioned: everyone creates their own.

### 4. Install the dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This command is detailed in the next section.

### 5. Choose the target image

Any image placed at the root of the project will do. The file name is set in
`CONSTANTS.py`:

```python
IMAGE_PATH = "mona_lisa.jpg"
```

### 6. Run

```powershell
.\.venv\Scripts\python.exe main.py
```

The program prints the best score as the generations go by:

```
epoch    0 | best score   169.56M
epoch  500 | best score    70.18M
epoch 1000 | best score    42.10M
```

The score is a **distance** to the target image: the lower, the better.

At the end, a window opens with the target image on the left, the best
contender on the right, and a slider at the bottom to replay the recorded
snapshots, from the first one to the last.

### 7. Run the tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## How requirements.txt works

This file lists the libraries the project needs, one per line:

```
pillow==12.3.0
numpy==2.5.3
pytest==9.1.1
matplotlib==3.11.2
```

- **pillow** opens and resizes the target image.
- **numpy** computes the pixel masks and the scores.
- **matplotlib** draws the polygons and the slider.
- **pytest** runs the tests.

The `==` pins an **exact** version. Anyone installing the project therefore
gets the same versions it was developed with, and a change of behaviour in a
new release of a library cannot break the project without warning. Looser
constraints exist: `>=12.0` accepts any version from 12.0 onwards, and a bare
name accepts any version at all.

Installing is done with the `-r` option, which means "read the list in this
file":

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Going through `.\.venv\Scripts\python.exe -m pip` rather than through plain
`pip` makes sure the installation lands in the project's virtual environment,
and not in the machine's global Python. This is the most common mistake: `pip`
on its own talks to the first Python found in the `PATH`, which is not
necessarily the project's one.

To check what is actually installed in the environment:

```powershell
.\.venv\Scripts\python.exe -m pip list
```

After adding a library, remember to add it to the file with its exact version.
`pip freeze` prints the whole environment in the right format.

## Settings

Everything is set in `CONSTANTS.py`. The current values match preset B below.

The best settings depend on the computing budget, so each preset is tuned for
its own `N_EPOCHS`, with `CONTENDERS_AMOUNT = 2` in all three cases.

| setting | A | B (active) | C |
|---|---|---|---|
| `N_EPOCHS` | 5,000 | 50,000 | 500,000 |
| `SNAPSHOT_EVERY` | 50 | 500 | 5,000 |
| `N_POLYGONS_TO_MUTATE` | 4 | 1 | 1 |
| `SIGMA_X`, `SIGMA_Y` | 6.5 | 5 | 5 |
| `SIGMA_RGB` | 60 | 40 | 40 |
| `SIGMA_ANGLE` | 15 | 30 | 30 |
| `SIGMA_RADIUS` | 0.27 | 0.3 | 0.3 |
| `SIGMA_FINAL_SCALE` | 0.045 | 0.05 | 0.05 |
| final score | ~48M | ~20.5M | ~14M |
| time | ~18 s | ~3 min | ~30 min |

For comparison, the previous settings (1,000 contenders, 1,000 generations,
501,000 images evaluated) reached 51.8M in about thirty minutes.

## Code layout

| file | role |
|---|---|
| `main.py` | entry point: runs the evolution, then the viewer |
| `CONSTANTS.py` | every setting |
| `classes/polygon.py` | one regular polygon: geometry, mask, mutation |
| `classes/contender.py` | one candidate: a list of polygons and its score |
| `classes/couple.py` | picking the best parent and building a mutated child |
| `classes/mapping.py` | the target image, the population and the evolution loop |
| `classes/viewer.py` | the result window and its slider |
| `tests/` | one test file per class |
