# genetique_image

Approximation d'une image par un empilement de polygones réguliers opaques,
optimisé par un algorithme évolutionnaire. Le programme part de polygones
tirés au hasard, les fait muter génération après génération, et garde à chaque
fois celui qui ressemble le plus à l'image cible.

## Qui a écrit quoi

**L'algorithme est écrit par l'auteur du dépôt**, sans génération de code :
la géométrie des polygones réguliers, le calcul du masque de pixels par
produit vectoriel, le score, les mutations, la sélection et la boucle
d'évolution. Claude (Anthropic) est intervenu en conseil sur ces parties —
explications, relectures, mesures comparatives de réglages — mais le code est
celui de l'auteur.

**La partie graphique est écrite par Claude** : `classes/viewer.py`, la
méthode `Polygon.draw_on`, la méthode `Contender.plot`, ainsi que les tests du
dossier `tests/`.

## Lancer le projet, pas à pas

### 1. Installer Python

Python 3.13 ou plus récent, depuis [python.org](https://www.python.org/downloads/).
Sur Windows, cocher **« Add python.exe to PATH »** pendant l'installation.

Vérification :

```powershell
python --version
```

### 2. Récupérer le projet

```powershell
git clone <url-du-depot>
cd genetique_image
```

### 3. Créer un environnement virtuel

Un environnement virtuel est un dossier qui contient sa propre copie de
Python et ses propres bibliothèques. Il évite que les versions installées pour
ce projet entrent en conflit avec celles d'un autre.

```powershell
python -m venv .venv
```

Un dossier `.venv` apparaît. Il n'est pas versionné, chacun crée le sien.

### 4. Installer les dépendances

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Cette commande est détaillée dans la section suivante.

### 5. Choisir l'image cible

N'importe quelle image placée à la racine du projet fait l'affaire. Le nom du
fichier se règle dans `CONSTANTS.py` :

```python
IMAGE_PATH = "mona_lisa.jpg"
```

### 6. Lancer

```powershell
.\.venv\Scripts\python.exe main.py
```

Le programme affiche le meilleur score au fil des générations :

```
epoch    0 | best score   169.56M
epoch  500 | best score    70.18M
epoch 1000 | best score    42.10M
```

Le score est une **distance** à l'image cible : plus il est bas, mieux c'est.

À la fin, une fenêtre s'ouvre avec l'image cible à gauche, le meilleur
candidat à droite, et un curseur en bas pour rejouer les instantanés
enregistrés, du premier au dernier.

### 7. Lancer les tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Comment fonctionne requirements.txt

Ce fichier est la liste des bibliothèques dont le projet a besoin, à raison
d'une par ligne :

```
pillow==12.3.0
numpy==2.5.3
pytest==9.1.1
matplotlib==3.11.2
```

- **pillow** ouvre et redimensionne l'image cible.
- **numpy** calcule les masques de pixels et les scores.
- **matplotlib** dessine les polygones et le curseur.
- **pytest** lance les tests.

Le `==` fixe une version **exacte**. N'importe qui installant le projet
obtiendra donc les mêmes versions que celles avec lesquelles il a été
développé, et un changement de comportement dans une nouvelle version d'une
bibliothèque ne cassera pas le projet sans prévenir. Il existe des contraintes
plus souples : `>=12.0` accepte toute version à partir de 12.0, et un nom seul
accepte n'importe quelle version.

L'installation se fait avec l'option `-r`, qui veut dire « lis la liste dans
ce fichier » :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Passer par `.\.venv\Scripts\python.exe -m pip` plutôt que par `pip` tout court
garantit que l'installation atterrit dans l'environnement virtuel du projet,
et non dans le Python global de la machine. C'est la source d'erreur la plus
fréquente : `pip` seul s'adresse au premier Python trouvé dans le `PATH`, qui
n'est pas forcément celui du projet.

Pour vérifier ce qui est réellement installé dans l'environnement :

```powershell
.\.venv\Scripts\python.exe -m pip list
```

Après avoir ajouté une bibliothèque, il faut penser à l'ajouter au fichier,
avec sa version exacte. `pip freeze` affiche la liste complète de
l'environnement au bon format.

## Réglages

Tout se règle dans `CONSTANTS.py`. Les valeurs actuelles correspondent au
preset B ci-dessous.

Les meilleurs réglages dépendent du budget de calcul, donc chaque preset est
réglé pour son propre `N_EPOCHS`, avec `CONTENDERS_AMOUNT = 2` dans les trois
cas.

| réglage | A | B (actif) | C |
|---|---|---|---|
| `N_EPOCHS` | 5 000 | 50 000 | 500 000 |
| `SNAPSHOT_EVERY` | 50 | 500 | 5 000 |
| `N_POLYGONS_TO_MUTATE` | 4 | 1 | 1 |
| `SIGMA_X`, `SIGMA_Y` | 6.5 | 5 | 5 |
| `SIGMA_RGB` | 60 | 40 | 40 |
| `SIGMA_ANGLE` | 15 | 30 | 30 |
| `SIGMA_RADIUS` | 0.27 | 0.3 | 0.3 |
| `SIGMA_FINAL_SCALE` | 0.045 | 0.05 | 0.05 |
| score final | ~48 M | ~20,5 M | ~14 M |
| durée | ~18 s | ~3 min | ~30 min |

Pour comparaison, les réglages précédents (1000 candidats, 1000 générations,
501 000 images évaluées) atteignaient 51,8 M en une trentaine de minutes.

## Organisation du code

| fichier | rôle |
|---|---|
| `main.py` | point d'entrée : lance l'évolution puis le visualiseur |
| `CONSTANTS.py` | tous les réglages |
| `classes/polygon.py` | un polygone régulier : géométrie, masque, mutation |
| `classes/contender.py` | un candidat : une liste de polygones et son score |
| `classes/couple.py` | sélection du meilleur parent et création d'un enfant muté |
| `classes/mapping.py` | l'image cible, la population et la boucle d'évolution |
| `classes/viewer.py` | la fenêtre de résultat et son curseur |
| `tests/` | un fichier de tests par classe |
