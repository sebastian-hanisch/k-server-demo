"""Einsatzfolgen auf der Geraden 0 bis GRID: Startaufstellung und die Anfragemuster (der Gegner entsteht erst im Lauf, siehe kse_algorithm)."""

import numpy as np

import kse_constants as C


def starts(k: int) -> list[int]:
    """Fahrzeuge gleichmäßig über die Strecke verteilt, an beiden Enden beginnend; ein einzelnes Fahrzeug steht in der Mitte."""
    if k == 1:
        return [C.GRID // 2]
    return [int(round(i * C.GRID / (k - 1))) for i in range(k)]


def gebiet_orte(h: int) -> list[int]:
    """h Orte im Abstand 2, um die Mitte der Strecke zentriert."""
    mitte = C.GRID // 2
    return [mitte + 2 * j - (h - 1) for j in range(h)]


def draw_requests(muster: str, k: int, t: int, seed: int) -> list[int]:
    """t Einsatzorte für ein festes Muster (nicht für den Gegner)."""
    assert muster in C.MUSTER and muster != "Gegner", muster
    rng = np.random.default_rng([seed, t, C.MUSTER.index(muster)])
    if muster == "gleichverteilt":
        return [int(x) for x in rng.integers(0, C.GRID + 1, size=t)]
    if muster == "gebündelt":
        zentren = rng.choice(C.BRENNPUNKTE, size=t)
        x = np.rint(rng.normal(zentren, C.STREUUNG))
        return [int(v) for v in np.clip(x, 0, C.GRID)]
    if muster == "wandernd":
        pos = C.GRID // 2
        out = []
        for step in rng.integers(-C.SCHRITT_MAX, C.SCHRITT_MAX + 1, size=t):
            pos = int(min(C.GRID, max(0, pos + int(step))))
            out.append(pos)
        return out
    orte = gebiet_orte(C.GEBIET_ORTE[muster])
    return [int(orte[i]) for i in rng.integers(0, len(orte), size=t)]


def draw_gebiet(h: int, t: int, seed: int) -> list[int]:
    """t Einsätze auf h Orten (für die Experimente, h kann auch 6 sein)."""
    rng = np.random.default_rng([seed, t, 1000 + h])
    orte = gebiet_orte(h)
    return [int(orte[i]) for i in rng.integers(0, h, size=t)]
