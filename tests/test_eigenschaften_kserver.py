"""Eigenschaften, die für jede Eingabe gelten müssen: Optimum als Untergrenze, Monotonie, Gültigkeit der Läufe, Struktur von Double Coverage,
Gegner (jedes Verfahren mindestens k), gemessene Schranken, Spiegelung, k = 1."""

import random

import pytest

import kse_algorithm as A
import kse_constants as C
import kse_evaluation as E
from kse_scenario import draw_gebiet, draw_requests, gebiet_orte, starts

MUSTER_FIX = [m for m in C.MUSTER if m != "Gegner"]


def _runs(k, muster, t, seed):
    reqs = draw_requests(muster, k, t, seed)
    return {n: A.simulate(n, k, starts(k), reqs) for n in C.VERFAHREN}


@pytest.mark.parametrize("muster", MUSTER_FIX)
@pytest.mark.parametrize("k", [1, 2, 3, 4])
def test_optimum_ist_untergrenze_und_laeufe_sind_gueltig(k, muster):
    for name, r in _runs(k, muster, 80, 3).items():
        assert r.cost >= r.optimum, name
        assert all(a <= b for a, b in zip(r.cum, r.cum[1:])) and all(a <= b for a, b in zip(r.opt, r.opt[1:]))
        for req, p in zip(r.requests, r.positions[1:]):
            assert req in p, (name, req, p)                        # nach jedem Einsatz steht dort ein Fahrzeug
        assert all(len(p) == k and list(p) == sorted(p) and 0 <= p[0] and p[-1] <= C.GRID for p in r.positions)


def test_verschiebung_der_sortierten_aufstellung_ist_hoechstens_die_gefahrene_strecke():
    for name, r in _runs(3, "gleichverteilt", 60, 4).items():
        total = sum(sum(abs(x - y) for x, y in zip(a, b)) for a, b in zip(r.positions, r.positions[1:]))
        assert total <= r.cost, name                                # die geordnete Zuordnung ist die billigste Zuordnung der Fahrzeuge


def test_mehr_fahrzeuge_machen_das_optimum_nicht_teurer():
    rng = random.Random(7)
    for _ in range(30):
        st = [rng.randint(0, C.GRID) for _ in range(2)]
        extra = rng.randint(0, C.GRID)
        reqs = [rng.randint(0, C.GRID) for _ in range(25)]
        assert A.opt_prefix(3, st + [extra], reqs)[-1] <= A.opt_prefix(2, st, reqs)[-1]


def test_double_coverage_bewegt_hoechstens_zwei_benachbarte_fahrzeuge():
    for muster in MUSTER_FIX:
        r = _runs(3, muster, 150, 8)["Double Coverage"]
        for a, b in zip(r.positions, r.positions[1:]):
            moved = [i for i in range(3) if a[i] != b[i]]
            assert len(moved) <= 2 and (len(moved) < 2 or moved[1] - moved[0] == 1), (a, b)


def test_greedy_bewegt_hoechstens_ein_fahrzeug():
    r = _runs(3, "wandernd", 150, 9)["Greedy"]
    for a, b in zip(r.positions, r.positions[1:]):
        assert len(set(a) ^ set(b)) <= 2                            # ein Ort wird frei, ein Ort wird besetzt


@pytest.mark.parametrize("name", C.VERFAHREN)
def test_ein_fahrzeug_alle_verfahren_gleich_und_optimal(name):
    for muster in MUSTER_FIX:
        r = _runs(1, muster, 60, 2)[name]
        assert r.cost == r.optimum


def test_spiegelung_aendert_optimum_und_double_coverage_nicht():
    rng = random.Random(11)
    for k in (2, 3):
        st = starts(k)
        mir = [C.GRID - x for x in st]
        for _ in range(15):
            reqs = [rng.randint(0, C.GRID) for _ in range(30)]
            m = [C.GRID - x for x in reqs]
            assert A.opt_prefix(k, st, reqs)[-1] == A.opt_prefix(k, mir, m)[-1]
            assert A.simulate("Double Coverage", k, st, reqs).cost == A.simulate("Double Coverage", k, mir, m).cost


@pytest.mark.parametrize("k", [2, 3, 4])
def test_gegner_erzwingt_mindestens_den_faktor_k_von_jedem_verfahren(k):
    for name in C.VERFAHREN:
        r = A.simulate_adversary(name, k, 300)
        assert r.cost >= 300                                       # jeder Einsatz fällt auf einen unbesetzten Ort, kostet also mindestens 1
        assert A.quotient(r.cost, r.optimum) >= k - 0.1, name


@pytest.mark.parametrize("k", [2, 3, 4])
def test_double_coverage_erreicht_gegen_den_gegner_genau_k(k):
    r = A.simulate_adversary("Double Coverage", k, 300)
    assert A.quotient(r.cost, r.optimum) == pytest.approx(k, abs=0.01)


def test_gemessene_schranken_von_double_coverage_und_arbeitsfunktion():
    """Schranken **nur gemessen** (nicht bewiesen): DC <= k * OPT + k * D und WFA <= (2k - 1) * OPT + (2k - 1) * D auf Zufallsfolgen und Gebieten."""
    rng = random.Random(12)
    D = C.GRID
    for k in (1, 2, 3, 4):
        for _ in range(40):
            st = starts(k)
            if rng.random() < 0.5:
                reqs = [rng.randint(0, C.GRID) for _ in range(rng.randint(1, 60))]
            else:
                orte = [rng.randint(0, C.GRID) for _ in range(rng.randint(1, k + 1))]
                reqs = [rng.choice(orte) for _ in range(rng.randint(1, 60))]
            o = A.opt_prefix(k, st, reqs)[-1]
            dc = A.simulate("Double Coverage", k, st, reqs).cost
            wf = A.simulate("Arbeitsfunktion", k, st, reqs).cost
            assert dc <= k * o + k * D, (k, dc, o)
            assert wf <= (2 * k - 1) * o + (2 * k - 1) * D, (k, wf, o)


@pytest.mark.parametrize("h", [2, 3])
def test_gebiet_mit_hoechstens_k_orten_optimum_zahlt_nur_die_anfahrt_greedy_zahlt_weiter(h):
    reqs = draw_gebiet(h, 600, 5)
    g = A.simulate("Greedy", 3, starts(3), reqs)
    assert g.opt[599] == g.opt[100]                                # nach der Anfahrt kostet nichts mehr
    assert g.cum[599] > 4 * g.cum[99]                              # Greedy zahlt weiter, die Kosten wachsen etwa linear mit der Zahl der Einsätze
    dc = A.simulate("Double Coverage", 3, starts(3), reqs)
    assert dc.cum[599] == dc.cum[99]                               # Double Coverage zahlt nur die Anfahrt


def test_gebiet_orte_liegen_im_gitter_und_sind_verschieden():
    for h in (2, 3, 4, 6):
        orte = gebiet_orte(h)
        assert len(set(orte)) == h and min(orte) >= 0 and max(orte) <= C.GRID


def test_verfahren_sind_deterministisch():
    a = E.analyse(E.Settings(muster="wandernd", seed=3))
    b = E.analyse(E.Settings(muster="wandernd", seed=3))
    assert a.runs == b.runs
