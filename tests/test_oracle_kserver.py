"""Orakel: das Offline-Optimum auf zwei getrennten Wegen (Zuordnung mit scipy, dynamische Programmierung über Aufstellungen) gegen die Arbeitsfunktion;
Verfahren gegen zweite, einfach geschriebene Fassungen; gleichmäßige Metrik gegen Belady; geschlossene Formeln der Gegenbeispiele."""

import math
import random

import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

import kse_algorithm as A
import kse_constants as C
from kse_scenario import draw_requests, starts


def opt_assign(start, reqs) -> float:
    """Pfadüberdeckung: jede Anfrage bekommt genau einen Vorgänger (Start eines Fahrzeugs oder frühere Anfrage), jeder Vorgänger höchstens einen Nachfolger."""
    T, k = len(reqs), len(start)
    big = 1e9
    cost = np.full((T, k + T), big)
    for j, r in enumerate(reqs):
        for s, p in enumerate(start):
            cost[j, s] = abs(r - p)
        for i in range(j):
            cost[j, k + i] = abs(r - reqs[i])
    rows, cols = linear_sum_assignment(cost)
    return float(cost[rows, cols].sum())


def opt_dp(start, reqs, dist=lambda a, b: abs(a - b)) -> float:
    """Dynamische Programmierung über Aufstellungen; nur ein Fahrzeug bewegt sich je Einsatz (träge Lösung genügt)."""
    dp = {tuple(sorted(start)): 0.0}
    for r in reqs:
        new = {}
        for C_, v in dp.items():
            if r in C_:
                new[C_] = min(new.get(C_, math.inf), v)
                continue
            for x in set(C_):
                L = list(C_)
                L.remove(x)
                L.append(r)
                C2 = tuple(sorted(L))
                new[C2] = min(new.get(C2, math.inf), v + dist(x, r))
        dp = new
    return min(dp.values())


@pytest.mark.parametrize("k", [1, 2, 3, 4])
def test_optimum_auf_drei_wegen_gleich(k):
    rng = random.Random(10 + k)
    for _ in range(40):
        st = [rng.randint(0, C.GRID) for _ in range(k)]
        reqs = [rng.randint(0, C.GRID) for _ in range(rng.randint(1, 18))]
        wf = A.opt_prefix(k, st, reqs)[-1]
        assert wf == pytest.approx(opt_assign(st, reqs)), (st, reqs)
        assert wf == pytest.approx(opt_dp(st, reqs)), (st, reqs)


def test_optimum_der_anfangsstrecken_gleicht_dem_optimum_der_kurzen_folge():
    rng = random.Random(3)
    st = starts(3)
    reqs = [rng.randint(0, C.GRID) for _ in range(15)]
    pre = A.opt_prefix(3, st, reqs)
    for t in range(1, 16):
        assert pre[t - 1] == pytest.approx(opt_assign(st, reqs[:t]))


def test_optimum_auf_typischen_mustern_gleicht_der_zuordnung():
    for muster in C.MUSTER:
        if muster == "Gegner":
            continue
        reqs = draw_requests(muster, 3, 60, 4)
        assert A.opt_prefix(3, starts(3), reqs)[-1] == pytest.approx(opt_assign(starts(3), reqs)), muster


def _greedy_schleife(start, reqs):
    pos = list(start)
    total = 0
    for r in reqs:
        i = min(range(len(pos)), key=lambda j: (abs(pos[j] - r), j))
        total += abs(pos[i] - r)
        pos[i] = r
        pos.sort()                                                  # sortiert wie das Verfahren, damit der Gleichstand dieselbe Reihenfolge hat
    return total


def test_greedy_gleicht_einer_schleife_ohne_klassen():
    rng = random.Random(5)
    for k in (1, 2, 3, 4):
        for _ in range(30):
            reqs = [rng.randint(0, C.GRID) for _ in range(40)]
            assert A.simulate("Greedy", k, starts(k), reqs).cost == _greedy_schleife(starts(k), reqs)


def _dc_schleife(start, reqs):
    """Double Coverage mit reellen Positionen (Bruch statt ganzer Zahlen), getrennt geschrieben."""
    pos = sorted(float(x) for x in start)
    total = 0.0
    for r in reqs:
        if r in pos:
            continue
        links = [x for x in pos if x < r]
        rechts = [x for x in pos if x > r]
        if not links:
            i = pos.index(min(rechts)); total += pos[i] - r; pos[i] = r
        elif not rechts:
            i = pos.index(max(links)); total += r - pos[i]; pos[i] = r
        else:
            a, b = max(links), min(rechts)
            d = min(r - a, b - r)
            total += 2 * d
            pos[pos.index(a)] = a + d
            pos[pos.index(b)] = b - d
        pos.sort()
    return total


def test_double_coverage_gleicht_der_schleife():
    rng = random.Random(6)
    for k in (1, 2, 3, 4):
        for _ in range(30):
            reqs = [rng.randint(0, C.GRID) for _ in range(40)]
            assert A.simulate("Double Coverage", k, starts(k), reqs).cost == pytest.approx(_dc_schleife(starts(k), reqs))


@pytest.mark.parametrize("m", [2, 3, 10, 100, 1000])
def test_greedy_gegenbeispiel_in_geschlossener_form(m):
    reqs = [5 if i % 2 == 0 else 7 for i in range(m)]
    r = A.simulate("Greedy", 2, [0, 12], reqs)
    assert r.cost == 5 + 2 * (m - 1)                               # erst 5 vom linken Fahrzeug, dann jedes Mal 2
    assert r.optimum == opt_assign([0, 12], reqs)
    assert r.optimum == min(10, 5 + 2 * (m - 1))                   # das zweite Fahrzeug holt man erst, wenn es sich lohnt (5 + 5 = 10)


def test_gleichmaessige_metrik_gleicht_belady():
    rng = random.Random(4)
    uniform = lambda a, b: 0 if a == b else 1
    for _ in range(80):
        k = rng.randint(2, 4)
        st = rng.sample(range(8), k)
        reqs = [rng.randint(0, 7) for _ in range(rng.randint(5, 25))]
        cache = set(st)
        faults = 0
        for i, r in enumerate(reqs):
            if r in cache:
                continue
            faults += 1
            nxt = {c: next((j for j in range(i + 1, len(reqs)) if reqs[j] == c), math.inf) for c in cache}
            cache.remove(max(cache, key=lambda c: nxt[c]))
            cache.add(r)
        assert opt_dp(st, reqs, uniform) == faults
