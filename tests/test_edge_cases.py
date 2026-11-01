"""Randfälle: kleinste und größte Flotte, alle Muster, Folgen ohne Kosten, Gegner ohne Seed, Extremwerte der Regler."""

import math

import pytest

import kse_algorithm as A
import kse_constants as C
import kse_evaluation as ev


@pytest.mark.parametrize("muster", C.MUSTER)
@pytest.mark.parametrize("k", [C.K_MIN, C.K_MAX])
def test_jedes_muster_laeuft_bei_kleinster_und_groesster_flotte(k, muster):
    a = ev.analyse(ev.Settings(k=k, muster=muster, t=50))
    for n in C.VERFAHREN:
        r = a.runs[n]
        assert len(r.cum) == len(r.requests) == len(r.opt) == 50 and len(r.positions) == 51
        assert r.cost >= r.optimum >= 0
    kind, text = ev.verdict_kern(a)
    assert kind in ("success", "info", "warning") and text


def test_folge_ohne_kosten_hat_den_quotienten_eins():
    r = A.simulate("Greedy", 3, [0, 6, 12], [6] * 5)
    assert r.cost == 0 and r.optimum == 0 and A.quotient(r.cost, r.optimum) == 1.0
    assert all(math.isnan(x) for x in ev.ratio_curve(r))             # ohne Optimumskosten ist der Quotient am Anfang nicht definiert


def test_unbeschraenkter_quotient_wird_als_text_gezeigt():
    r = A.Run("Greedy", (0,), (3,), ((0,), (1,)), (0,))
    assert math.isinf(A.quotient(r.cost, r.optimum)) and ev.fmt(math.inf) == "unbeschränkt"
    assert math.isnan(ev.ratio_curve(r)[0])                         # die Kurve lässt Stellen ohne Optimumskosten aus


def test_leere_folge_hat_keine_kosten():
    r = A.simulate("Double Coverage", 2, [0, 12], [])
    assert r.cost == 0 and r.optimum == 0 and r.cum == () and r.positions == ((0, 12),)


def test_gegner_ist_deterministisch_der_seed_wirkt_nicht():
    a = ev.analyse(ev.Settings(muster="Gegner", seed=1))
    b = ev.analyse(ev.Settings(muster="Gegner", seed=999))
    assert a.runs == b.runs
    assert a.start == (0, 1, 2)


def test_andere_muster_haengen_vom_seed_ab():
    a = ev.analyse(ev.Settings(muster="gleichverteilt", seed=1))
    b = ev.analyse(ev.Settings(muster="gleichverteilt", seed=2))
    assert a.runs["Greedy"].requests != b.runs["Greedy"].requests


@pytest.mark.parametrize("seed", [0, C.SEED_MAX])
def test_grenzen_des_seeds(seed):
    a = ev.analyse(ev.Settings(seed=seed))
    assert a.runs["Greedy"].cost >= a.runs["Greedy"].optimum


@pytest.mark.parametrize("t", C.T_OPTIONS)
def test_alle_laengen_laufen(t):
    a = ev.analyse(ev.Settings(t=t, verfahren="Arbeitsfunktion"))
    assert len(a.runs["Arbeitsfunktion"].cum) == t


def test_alle_verfahren_starten_mit_derselben_aufstellung():
    a = ev.analyse(ev.Settings(k=4))
    assert {r.positions[0] for r in a.runs.values()} == {(0, 4, 8, 12)}
