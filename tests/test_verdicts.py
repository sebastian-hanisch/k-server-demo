"""Verdikte: jede Zahl und jede Verzweigung der Texte. Die Verdikte sind reine Funktionen (Art, Text); die Zahlen im Text werden aus den Eingaben nachgerechnet."""

import math

import pytest

import kse_algorithm as A
import kse_constants as C
import kse_evaluation as ev


def _run(name, cost, opt, t=100):
    return A.Run(name, tuple([0] * t), tuple([cost] * t), ((0,),) * (t + 1), tuple([opt] * t))


def _analysis(k, verfahren, kosten, opt, muster="gleichverteilt", t=100):
    s = ev.Settings(k=k, verfahren=verfahren, muster=muster, t=t)
    runs = {n: _run(n, kosten[n], opt, t) for n in C.VERFAHREN}
    return ev.Analysis(s, runs, {n: A.quotient(runs[n].cost, runs[n].optimum) for n in C.VERFAHREN}, (0,))


KOSTEN = {"Greedy": 130, "Double Coverage": 200, "Arbeitsfunktion": 135}


def test_verdict_kern_zahlen_und_billigstes():
    kind, text = ev.verdict_kern(_analysis(3, "Double Coverage", KOSTEN, 100))
    assert "**Double Coverage** zahlt bei 100 Einsätzen und 3 Fahrzeugen **200** gegen das Optimum 100: Quotient **2.00** (Garantie 3, bis auf eine additive Konstante)" in text
    assert "Das billigste Verfahren ist hier Greedy mit 130." in text
    assert kind == "info"
    kind, text = ev.verdict_kern(_analysis(3, "Greedy", KOSTEN, 100))
    assert "Von den drei Verfahren ist es hier das billigste." in text and "keine Garantie" in text
    assert kind == "success"                                       # 1,30 liegt unter 1,5


@pytest.mark.parametrize("kosten,k,art", [(150, 3, "success"), (151, 3, "info"), (300, 3, "info"), (301, 3, "warning"), (200, 1, "info"), (100, 1, "success")])
def test_verdict_kern_schwellen(kosten, k, art):
    kos = {"Greedy": 100, "Double Coverage": kosten, "Arbeitsfunktion": 100}
    assert ev.verdict_kern(_analysis(k, "Double Coverage", kos, 100))[0] == art


def test_verdict_kern_unbeschraenkt_und_gegner():
    kos = {"Greedy": 300, "Double Coverage": 300, "Arbeitsfunktion": 300}
    kind, text = ev.verdict_kern(_analysis(3, "Greedy", kos, 0))
    assert kind == "warning" and "Quotient **unbeschränkt**" in text
    kind, text = ev.verdict_kern(_analysis(3, "Greedy", KOSTEN, 100, muster="Gegner"))
    assert "Der Gegner richtet seine Folge nach jedem Verfahren neu aus; verglichen wird deshalb der Quotient, nicht die Strecke." in text and "billigste" not in text


def test_verdict_gegen():
    rows = [{"m": 2, "Optimum": 7, "Kosten Greedy": 7, "Greedy": 1.0, "Double Coverage": 1.43, "Arbeitsfunktion": 1.0},
            {"m": 1000, "Optimum": 10, "Kosten Greedy": 2003, "Greedy": 200.3, "Double Coverage": 1.0, "Arbeitsfunktion": 1.8}]
    kind, text = ev.verdict_gegen(rows)
    assert kind == "warning"
    assert "Bei 2 Einsätzen ist Greedy mit Quotient 1.00 noch nahe am Optimum" in text
    assert "bei 1000 Einsätzen zahlt es 2003 gegen das Optimum 10: Quotient **200.30**" in text
    assert "Double Coverage liegt bei 1.00, die Arbeitsfunktion bei 1.80." in text


def test_verdict_gegner():
    rows = [{"k": 2, "Greedy": 150.0, "Double Coverage": 2.0, "Arbeitsfunktion": 2.0}, {"k": 4, "Greedy": 150.0, "Double Coverage": 4.0, "Arbeitsfunktion": 3.95}]
    kind, text = ev.verdict_gegner(rows)
    assert kind == "info"
    assert "Bei k = 2, 4 Fahrzeugen" in text and "**2.00, 4.00** (genau k)" in text and "die Arbeitsfunktion 2.00, 3.95" in text and "Greedy kommt auf bis zu 150.00" in text


def test_verdict_typisch():
    rows = [{"Muster": "gleichverteilt", "mean": {"Greedy": 1.15, "Double Coverage": 1.85, "Arbeitsfunktion": 1.17}, "max": {}},
            {"Muster": "wandernd", "mean": {"Greedy": 1.41, "Double Coverage": 1.92, "Arbeitsfunktion": 1.48}, "max": {}}]
    kind, text = ev.verdict_typisch(rows)
    assert kind == "info"
    assert "Greedy im Mittel das 1.15-Fache" in text and "die Arbeitsfunktion das 1.17-Fache" in text and "Double Coverage das 1.85-Fache" in text
    assert "(gleichverteilt) kostet Double Coverage 61 % mehr als Greedy" in text                  # 1,85 / 1,15 − 1 = 61 %


def test_verdict_gebiet():
    rows = [{"h": 2, "T": 1000, "Greedy": 164.9, "Double Coverage": 3.33, "Arbeitsfunktion": 2.22},
            {"h": 3, "T": 1000, "Greedy": 85.2, "Double Coverage": 2.0, "Arbeitsfunktion": 2.85},
            {"h": 4, "T": 1000, "Greedy": 2.44, "Double Coverage": 2.97, "Arbeitsfunktion": 1.41},
            {"h": 6, "T": 1000, "Greedy": 1.28, "Double Coverage": 1.96, "Arbeitsfunktion": 1.24},
            {"h": 2, "T": 100, "Greedy": 16.6, "Double Coverage": 3.33, "Arbeitsfunktion": 2.22}]
    kind, text = ev.verdict_gebiet(rows)
    assert kind == "warning"
    assert "höchstens 3 Orte" in text and "bei 1000 Einsätzen auf bis zu **164.9**" in text and "höchstens 3.33" in text and "sinkt Greedy auf 2.44, 1.28" in text


def test_verdict_laenge_mit_und_ohne_ueberschreitung():
    rows = [{"Muster": "Gebiet mit 2 Orten", "T": 25, "Quotient": 3.33, "Maximum": 3.33}, {"Muster": "Gebiet mit 2 Orten", "T": 1000, "Quotient": 3.33, "Maximum": 3.33},
            {"Muster": "gleichverteilt", "T": 25, "Quotient": 1.79, "Maximum": 2.2}, {"Muster": "gleichverteilt", "T": 1000, "Quotient": 1.8, "Maximum": 1.86}]
    kind, text = ev.verdict_laenge(rows)
    assert kind == "info"
    assert "Bei 1000 Einsätzen liegt Double Coverage bei Gebiet mit 2 Orten 3.33, gleichverteilt 1.80; die Garantie ist k = 3." in text
    assert "Bei Gebiet mit 2 Orten bleibt der Quotient auch bei 1000 Einsätzen **über k**" in text
    kind, text = ev.verdict_laenge([r for r in rows if r["Muster"] == "gleichverteilt"])
    assert "über k" not in text


def test_delta_text_und_fmt():
    assert ev.delta_text(1.8, 1.8, "Greedy") == ("gleich wie Greedy", "off")
    assert ev.delta_text(1.8, 1.23, "Greedy") == ("+0.57 gegen Greedy", "inverse")
    assert ev.delta_text(0.9, 1.0, "Greedy") == ("-0.10 gegen Greedy", "inverse")
    assert ev.delta_text(math.inf, 1.0, "Greedy") == ("unbeschränkt gegen Greedy", "inverse")
    assert ev.fmt(2.0) == "2.00" and ev.fmt(math.inf) == "unbeschränkt"
