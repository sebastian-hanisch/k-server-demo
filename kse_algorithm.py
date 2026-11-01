"""Kern: k Fahrzeuge auf der ganzzahligen Geraden 0 bis GRID. Ein Einsatz an einem Ort verlangt, dass dort ein Fahrzeug steht; Kosten = gefahrene Strecke.

Verfahren: Greedy, Double Coverage, Arbeitsfunktionsalgorithmus. Das Offline-Optimum kommt aus der Arbeitsfunktion (Minimum über alle Aufstellungen);
unabhängig davon prüfen die Tests es mit Zuordnung (scipy) und dynamischer Programmierung."""

import itertools
import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

import kse_constants as C


# ---------------------------------------------------------------------------------------------------------------------------------
# Arbeitsfunktion über alle Aufstellungen (sortierte k-Tupel mit Wiederholung)


@lru_cache(maxsize=None)
def tables(k: int):
    """Aufstellungen, Nachbartabelle und Kosten: neigh[X, j, r] ist die Aufstellung, in der das j-te Fahrzeug von X an den Ort r gefahren ist."""
    configs = [c for c in itertools.combinations_with_replacement(range(C.GRID + 1), k)]
    index = {c: i for i, c in enumerate(configs)}
    S, P = len(configs), C.GRID + 1
    neigh = np.zeros((S, k, P), dtype=np.int32)
    cost = np.zeros((S, k, P), dtype=np.int32)
    for i, X in enumerate(configs):
        for j in range(k):
            rest = X[:j] + X[j + 1:]
            for r in range(P):
                neigh[i, j, r] = index[tuple(sorted(rest + (r,)))]
                cost[i, j, r] = abs(X[j] - r)
    return np.array(configs, dtype=np.int32), index, neigh, cost


class WorkFunction:
    """w_t(X) = geringste Kosten, die Einsätze bis t zu bedienen und in der Aufstellung X zu enden (Start: die Aufstellung der Fahrzeuge)."""

    def __init__(self, k: int, start):
        self.k = k
        self.configs, self.index, self.neigh, self.cost = tables(k)
        s = np.sort(np.array(start, dtype=np.int32))
        self.w = np.abs(self.configs - s[None, :]).sum(axis=1).astype(np.int64)

    def step(self, r: int):
        w = self.w
        cand = w[self.neigh[:, :, r]] + self.cost[:, :, r]
        self.w = cand.min(axis=1)

    @property
    def opt(self) -> int:
        return int(self.w.min())


def opt_prefix(k: int, start, requests) -> list[int]:
    """Optimale Gesamtkosten für jede Anfangsstrecke der Folge: Eintrag t gilt für die ersten t + 1 Einsätze."""
    wf = WorkFunction(k, start)
    out = []
    for r in requests:
        wf.step(r)
        out.append(wf.opt)
    return out


# ---------------------------------------------------------------------------------------------------------------------------------
# Verfahren: je ein Objekt mit step(r) -> Kosten und der Aufstellung pos (sortiert)


class Greedy:
    name = "Greedy"

    def __init__(self, k, start):
        self.pos = sorted(start)

    def step(self, r: int) -> int:
        i = min(range(len(self.pos)), key=lambda j: (abs(self.pos[j] - r), j))
        c = abs(self.pos[i] - r)
        self.pos[i] = r
        self.pos.sort()
        return c


class DoubleCoverage:
    name = "Double Coverage"

    def __init__(self, k, start):
        self.pos = sorted(start)

    def step(self, r: int) -> int:
        p = self.pos
        if r <= p[0]:
            c = p[0] - r
            p[0] = r
            return c
        if r >= p[-1]:
            c = r - p[-1]
            p[-1] = r
            return c
        left = max(i for i, x in enumerate(p) if x <= r)
        right = min(i for i, x in enumerate(p) if x >= r)
        if p[left] == r or p[right] == r:
            return 0
        d = min(r - p[left], p[right] - r)
        p[left] += d
        p[right] -= d
        return 2 * d


class Arbeitsfunktion:
    name = "Arbeitsfunktion"

    def __init__(self, k, start):
        self.wf = WorkFunction(k, start)
        self.pos = sorted(start)

    def step(self, r: int) -> int:
        self.wf.step(r)
        if r in self.pos:
            return 0
        best, choice = math.inf, None
        for j in range(len(self.pos)):
            c2 = int(self.wf.neigh[self.wf.index[tuple(self.pos)], j, r])
            v = int(self.wf.w[c2]) + abs(self.pos[j] - r)
            if v < best:
                best, choice = v, (j, c2)
        j, c2 = choice
        c = abs(self.pos[j] - r)
        self.pos = [int(x) for x in self.wf.configs[c2]]
        return c


ALGS = {"Greedy": Greedy, "Double Coverage": DoubleCoverage, "Arbeitsfunktion": Arbeitsfunktion}


@dataclass(frozen=True)
class Run:
    name: str
    requests: tuple
    cum: tuple            # kumulierte Kosten nach jedem Einsatz
    positions: tuple      # Aufstellung (sortiert) vor dem ersten und nach jedem Einsatz
    opt: tuple            # optimale Kosten der Anfangsstrecken (opt_prefix)

    @property
    def cost(self) -> int:
        return self.cum[-1] if self.cum else 0

    @property
    def optimum(self) -> int:
        return self.opt[-1] if self.opt else 0


def simulate(name: str, k: int, start, requests) -> Run:
    alg = ALGS[name](k, start)
    cum, pos, total = [], [tuple(alg.pos)], 0
    for r in requests:
        total += alg.step(r)
        cum.append(total)
        pos.append(tuple(alg.pos))
    return Run(name, tuple(requests), tuple(cum), tuple(pos), tuple(opt_prefix(k, start, requests)))


def free_point(pos) -> int:
    """Erster Ort unter 0 bis k, an dem kein Fahrzeug steht (der Gegner fragt ihn an)."""
    k = len(pos)
    return next(p for p in range(k + 1) if p not in pos)


def simulate_adversary(name: str, k: int, t: int) -> Run:
    """Der Gegner fragt jedes Mal den unbesetzten von k + 1 Orten an (Fahrzeuge starten auf 0 bis k − 1)."""
    start = list(range(k))
    alg = ALGS[name](k, start)
    reqs, cum, pos, total = [], [], [tuple(alg.pos)], 0
    for _ in range(t):
        r = free_point(alg.pos)
        reqs.append(r)
        total += alg.step(r)
        cum.append(total)
        pos.append(tuple(alg.pos))
    return Run(name, tuple(reqs), tuple(cum), tuple(pos), tuple(opt_prefix(k, start, reqs)))


def quotient(cost: float, opt: float) -> float:
    """Kosten geteilt durch das Optimum; ohne Optimumskosten ist 1 der neutrale Wert, wenn auch das Verfahren nichts zahlt, sonst unendlich."""
    if opt <= 0:
        return 1.0 if cost <= 0 else math.inf
    return cost / opt


def guarantee(name: str, k: int):
    """Garantie des Verfahrens (bis auf eine additive Konstante), None wenn es keine gibt."""
    if name == "Double Coverage":
        return k
    if name == "Arbeitsfunktion":
        return 2 * k - 1
    return None
