"""Kern von Hand gerechnet: Startaufstellung, die drei Verfahren, Arbeitsfunktion, Optimum, Gegner, Quotient und Garantie."""

import math

import pytest

import kse_algorithm as A
import kse_constants as C
from kse_scenario import draw_gebiet, draw_requests, gebiet_orte, starts


def test_startaufstellung_und_gebiete():
    assert starts(1) == [6] and starts(2) == [0, 12] and starts(3) == [0, 6, 12] and starts(4) == [0, 4, 8, 12]
    assert gebiet_orte(2) == [5, 7] and gebiet_orte(3) == [4, 6, 8] and gebiet_orte(4) == [3, 5, 7, 9] and gebiet_orte(6) == [1, 3, 5, 7, 9, 11]


def test_ein_fahrzeug_von_hand():
    # Start 6, Einsätze 8, 2, 2, 5: 2 + 6 + 0 + 3 = 11
    reqs = [8, 2, 2, 5]
    for name in C.VERFAHREN:
        r = A.simulate(name, 1, [6], reqs)
        assert r.cost == 11 and r.optimum == 11, name
        assert r.cum == (2, 8, 8, 11)


def test_greedy_von_hand():
    r = A.simulate("Greedy", 2, [0, 12], [5, 7])
    assert r.cum == (5, 7) and r.positions[-1] == (7, 12)          # das Fahrzeug bei 12 steht untätig; 5 holt das Fahrzeug von 0 (5 < 7); 7 holt es von 5 (2 < 5)
    g = A.Greedy(2, [4, 8])
    assert g.step(6) == 2 and g.pos == [6, 8]                      # Gleichstand: das linke Fahrzeug


def test_double_coverage_von_hand():
    r = A.simulate("Double Coverage", 2, [0, 12], [5, 7])
    assert r.cum == (10, 10) and r.positions == ((0, 12), (5, 7), (5, 7))   # beide fahren 5, das zweite steht dann bei 7
    d = A.DoubleCoverage(2, [4, 8])
    assert d.step(1) == 3 and d.pos == [1, 8]                      # außerhalb: das nächste Fahrzeug
    assert d.step(11) == 3 and d.pos == [1, 11]
    assert d.step(11) == 0                                         # dort steht schon eines
    assert d.step(6) == 10 and d.pos == [6, 6]                     # Fahrzeuge bei 1 und 11, Einsatz 6: beide gleich weit (5), beide fahren 5, Kosten 10


def test_double_coverage_ungleiche_abstaende():
    d = A.DoubleCoverage(2, [0, 10])
    assert d.step(3) == 6 and d.pos == [3, 7]                      # beide fahren 3: das linke kommt an, das rechte steht bei 7
    d = A.DoubleCoverage(3, [0, 5, 12])
    assert d.step(4) == 2 and d.pos == [1, 4, 12]                  # 0 und 5 liegen um 4 und 1 entfernt: beide fahren 1, das rechte kommt an


def test_arbeitsfunktion_von_hand():
    wf = A.WorkFunction(1, [6])
    wf.step(8)
    assert wf.opt == 2
    r = A.simulate("Arbeitsfunktion", 2, [0, 12], [5])
    assert r.cum == (5,) and r.positions[-1] == (5, 12) and r.optimum == 5
    wf = A.WorkFunction(2, [0, 12])
    wf.step(5)
    idx = wf.index
    assert wf.w[idx[(5, 12)]] == 5 and wf.w[idx[(0, 5)]] == 7        # Handrechnung aus dem Einzelplan: w({5,12}) = 5, w({0,5}) = 7


def test_optimum_der_gegenbeispiel_folge():
    reqs = [5, 7] * 6
    assert A.opt_prefix(2, [0, 12], reqs)[:2] == [5, 7]              # kurz: das erste Fahrzeug macht alles
    assert A.opt_prefix(2, [0, 12], reqs)[-1] == 10                  # lang: das zweite Fahrzeug kommt einmal heran (5 + 5)


def test_gegner_fragt_den_unbesetzten_ort():
    assert A.free_point((0, 1, 2)) == 3 and A.free_point((1, 2, 3)) == 0 and A.free_point((0, 2, 3)) == 1
    r = A.simulate_adversary("Greedy", 2, 4)
    assert r.requests == (2, 1, 0, 1) and r.cum == (1, 2, 3, 4)       # Start 0, 1: frei ist 2; Gleichstand: das linke Fahrzeug fährt, dann wieder der freie Ort
    r = A.simulate_adversary("Double Coverage", 2, 3)
    assert r.positions[0] == (0, 1) and r.requests[0] == 2


def test_quotient_und_garantie():
    assert A.quotient(10, 5) == 2.0 and A.quotient(0, 0) == 1.0 and math.isinf(A.quotient(3, 0))
    assert A.guarantee("Greedy", 3) is None and A.guarantee("Double Coverage", 3) == 3 and A.guarantee("Arbeitsfunktion", 3) == 5


def test_tabellen_haben_die_erwartete_groesse():
    configs, index, neigh, cost = A.tables(3)
    assert len(configs) == math.comb(C.GRID + 3, 3) == len(index)
    assert neigh.shape == (len(configs), 3, C.GRID + 1) and cost.min() == 0


def test_muster_sind_reproduzierbar_im_gitter_und_verschieden():
    for m in C.MUSTER:
        if m == "Gegner":
            continue
        a = draw_requests(m, 3, 60, 5)
        assert a == draw_requests(m, 3, 60, 5) and a != draw_requests(m, 3, 60, 6)
        assert len(a) == 60 and min(a) >= 0 and max(a) <= C.GRID
    assert set(draw_requests("Gebiet mit 3 Orten", 3, 200, 1)) == {4, 6, 8}
    assert set(draw_gebiet(6, 300, 1)) == set(gebiet_orte(6))
