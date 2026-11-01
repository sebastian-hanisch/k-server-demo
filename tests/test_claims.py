"""Claims: jede Zahl der README, über dieselben Auswertungsfunktionen wie in der App nachgerechnet (feste Seeds, deterministisch)."""

import pytest

import kse_algorithm as A
import kse_constants as C
import kse_evaluation as ev

G, D, W = C.VERFAHREN


def r2(x):
    return round(x, 2)


def _preset(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_klassisches_preset():
    a = _preset("Klassisch (k = 3, gleichverteilt)")
    assert {n: a.runs[n].cost for n in C.VERFAHREN} == {G: 138, D: 202, W: 136} and a.runs[G].optimum == 112
    assert [r2(a.ratios[n]) for n in C.VERFAHREN] == [1.23, 1.80, 1.21]


def test_gegenbeispiel():
    rows = {r["m"]: r for r in ev.gegen_rows()}
    assert [rows[m]["Kosten Greedy"] for m in (2, 10, 100, 1000)] == [7, 23, 203, 2003]
    assert [rows[m]["Optimum"] for m in (2, 10, 100, 1000)] == [7, 10, 10, 10]
    assert [r2(rows[m][G]) for m in (2, 10, 100, 1000)] == [1.00, 2.30, 20.30, 200.30]
    assert all(rows[m]["Kosten Greedy"] == 5 + 2 * (m - 1) for m in rows)
    assert [r2(rows[m][D]) for m in (2, 10, 100, 1000)] == [1.43, 1.00, 1.00, 1.00]
    assert [r2(rows[m][W]) for m in (2, 10, 100, 1000)] == [1.00, 1.80, 1.80, 1.80]


def test_gegner():
    rows = {r["k"]: r for r in ev.adv_rows()}
    assert [r2(rows[k][D]) for k in (2, 3, 4)] == [2.00, 3.00, 4.00]
    assert [r2(rows[k][W]) for k in (2, 3, 4)] == [2.00, 3.00, 3.95]
    assert [r2(rows[k][G]) for k in (2, 3, 4)] == [150.0] * 3
    r = A.simulate_adversary("Greedy", 3, 300)
    assert r.cost == 300 and r.optimum == 2                                      # „Kosten 300, Optimum 2“


def test_typische_muster():
    rows = {r["Muster"]: r for r in ev.typ_rows()}
    assert [r2(rows["gleichverteilt"]["mean"][n]) for n in C.VERFAHREN] == [1.15, 1.85, 1.17]
    assert [r2(rows["gebündelt"]["mean"][n]) for n in C.VERFAHREN] == [1.12, 1.80, 1.14]
    assert [r2(rows["wandernd"]["mean"][n]) for n in C.VERFAHREN] == [1.41, 1.92, 1.48]
    aufschlag = {m: rows[m]["mean"][D] / rows[m]["mean"][G] - 1 for m in rows}
    assert round(100 * max(aufschlag.values())) == 61 and max(aufschlag, key=aufschlag.get) == "gleichverteilt"
    assert r2(rows["gleichverteilt"]["max"][D]) == 2.03 and r2(rows["wandernd"]["max"][D]) == 2.20


def test_gebiete():
    rows = {(r["h"], r["T"]): r for r in ev.gebiet_rows()}
    assert [r2(rows[(2, t)][G]) for t in (100, 1000)] == [16.62, 164.90]
    assert [r2(rows[(2, t)][D]) for t in (100, 1000)] == [3.33, 3.33] and [r2(rows[(2, t)][W]) for t in (100, 1000)] == [2.22, 2.22]
    assert [r2(rows[(3, t)][G]) for t in (100, 1000)] == [9.64, 85.22]
    assert [r2(rows[(3, t)][D]) for t in (100, 1000)] == [2.00, 2.00] and [r2(rows[(3, t)][W]) for t in (100, 1000)] == [2.85, 2.85]
    assert [r2(rows[(4, t)][G]) for t in (100, 1000)] == [2.44, 2.44]
    assert [r2(rows[(4, t)][D]) for t in (100, 1000)] == [2.80, 2.97] and [r2(rows[(4, t)][W]) for t in (100, 1000)] == [1.43, 1.41]
    assert [r2(rows[(6, t)][G]) for t in (100, 1000)] == [1.25, 1.28]
    assert [r2(rows[(6, t)][D]) for t in (100, 1000)] == [1.97, 1.96] and [r2(rows[(6, t)][W]) for t in (100, 1000)] == [1.24, 1.24]
    assert rows[(6, 1000)][G] < rows[(6, 1000)][D] and rows[(4, 1000)][G] < rows[(4, 1000)][D]   # mit mehr Orten als Fahrzeugen ist Greedy wieder besser als Double Coverage


def test_garantie_gilt_nur_bis_auf_eine_konstante():
    rows = {(r["Muster"], r["T"]): r["Quotient"] for r in ev.laenge_rows()}
    assert all(r2(rows[("Gebiet mit 2 Orten", t)]) == 3.33 for t in C.LAENGE_TS) and 3.33 > C.LAENGE_K
    assert all(r2(rows[("Gebiet mit 3 Orten", t)]) == 2.00 for t in C.LAENGE_TS)
    assert r2(rows[("gleichverteilt", 25)]) == 1.79 and r2(rows[("gleichverteilt", 1000)]) == 1.80


def test_weitere_presets():
    a = _preset("Gebiet mit 3 Orten")
    assert a.runs[G].optimum == 8 and a.runs[G].cost == 350 and r2(a.ratios[G]) == 43.75 and a.runs[D].cost == a.runs[W].cost == 16 and r2(a.ratios[D]) == 2.00
    a = _preset("Wandernd (Stau)")
    assert [r2(a.ratios[n]) for n in C.VERFAHREN] == [1.20, 1.80, 1.26]
    a = _preset("Ein Fahrzeug (k = 1)")
    assert {r.cost for r in a.runs.values()} == {439} and a.runs[G].optimum == 439


def test_orakel_zahlen_der_readme():
    assert C.GRID == 12 and C.TYP_SEEDS == 30 and C.GEBIET_SEEDS == 20 and C.LAENGE_SEEDS == 20 and C.ADV_T == 300 and C.TYP_T == 100
    assert 4 * 40 == 160                                                          # Zufallsinstanzen im Orakeltest (k = 1 bis 4, je 40)
