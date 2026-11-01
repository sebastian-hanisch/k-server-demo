"""Kennzahlen, Verdikt-Logik und Experimente. Verdikte sind reine Funktionen (Art, Text); tests/test_verdicts.py prüft jede Zahl darin."""

import math
from dataclasses import dataclass

import numpy as np

import kse_algorithm as A
import kse_constants as C
from kse_scenario import draw_gebiet, draw_requests, starts

OK_QUOTIENT = 1.5                                # Verdikt: grün bis zum Quotienten 1,5, gelb bis zur Garantie k, sonst Warnung


@dataclass(frozen=True)
class Settings:
    k: int = C.DEFAULT_K
    verfahren: str = C.DEFAULT_VERFAHREN
    muster: str = C.DEFAULT_MUSTER
    t: int = C.DEFAULT_T
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    runs: dict                       # Verfahren -> Run
    ratios: dict                     # Verfahren -> Quotient Kosten / Optimum
    start: tuple


def fmt(x: float) -> str:
    """Quotient als Text; unendlich (Optimum ohne Kosten, Verfahren zahlt) als „unbeschränkt“."""
    return "unbeschränkt" if math.isinf(x) else f"{x:.2f}"


def analyse(s: Settings) -> Analysis:
    st = starts(s.k)
    runs = {}
    if s.muster == "Gegner":
        st = list(range(s.k))
        for name in C.VERFAHREN:
            runs[name] = A.simulate_adversary(name, s.k, s.t)
    else:
        reqs = draw_requests(s.muster, s.k, s.t, s.seed)
        for name in C.VERFAHREN:
            runs[name] = A.simulate(name, s.k, st, reqs)
    return Analysis(s, runs, {n: A.quotient(r.cost, r.optimum) for n, r in runs.items()}, tuple(st))


def ratio_curve(run: A.Run) -> list[float]:
    """Quotient nach jedem Einsatz (nur dort, wo das Optimum schon etwas kostet)."""
    return [A.quotient(c, o) if o > 0 else float("nan") for c, o in zip(run.cum, run.opt)]


# ---------------------------------------------------------------------------------------------------------------------------------
# Experimente mit festen Folgen und Seeds


def gegen_rows(k: int = C.GEGEN_K, orte=C.GEGEN_ORTE, ms=C.GEGEN_MS) -> list[dict]:
    """Experiment 1: zwei Fahrzeuge an den Enden, Einsätze abwechselnd auf zwei Orten in der Mitte; die Folge wächst."""
    mmax = max(ms)
    reqs = [orte[i % 2] for i in range(mmax)]
    runs = {n: A.simulate(n, k, starts(k), reqs) for n in C.VERFAHREN}
    rows = []
    for m in ms:
        row = {"m": m, "Optimum": runs["Greedy"].opt[m - 1], "Kosten Greedy": runs["Greedy"].cum[m - 1]}
        for n in C.VERFAHREN:
            row[n] = A.quotient(runs[n].cum[m - 1], runs[n].opt[m - 1])
        rows.append(row)
    return rows


def adv_rows(ks=C.ADV_KS, t: int = C.ADV_T) -> list[dict]:
    """Experiment 2: der Gegner fragt immer den unbesetzten von k + 1 Orten an."""
    rows = []
    for k in ks:
        row = {"k": k}
        for n in C.VERFAHREN:
            r = A.simulate_adversary(n, k, t)
            row[n] = A.quotient(r.cost, r.optimum)
        rows.append(row)
    return rows


def typ_rows(muster=C.TYP_MUSTER, k: int = C.TYP_K, t: int = C.TYP_T, seeds: int = C.TYP_SEEDS) -> list[dict]:
    """Experiment 3: typische Anfragemuster, Mittel und Maximum der Quotienten über feste Seeds."""
    rows = []
    for m in muster:
        qs = {n: [] for n in C.VERFAHREN}
        for seed in range(seeds):
            reqs = draw_requests(m, k, t, seed)
            for n in C.VERFAHREN:
                r = A.simulate(n, k, starts(k), reqs)
                qs[n].append(A.quotient(r.cost, r.optimum))
        rows.append({"Muster": m, "mean": {n: float(np.mean(v)) for n, v in qs.items()}, "max": {n: float(np.max(v)) for n, v in qs.items()}})
    return rows


def gebiet_rows(hs=C.GEBIET_HS, ts=C.GEBIET_TS, k: int = C.GEBIET_K, seeds: int = C.GEBIET_SEEDS) -> list[dict]:
    """Experiment 4: Einsätze gleichverteilt auf h Orten; die kürzeren Folgen sind Anfangsstrecken der längsten."""
    tmax = max(ts)
    rows = []
    for h in hs:
        qs = {(t, n): [] for t in ts for n in C.VERFAHREN}
        for seed in range(seeds):
            reqs = draw_gebiet(h, tmax, 100 + seed)
            for n in C.VERFAHREN:
                r = A.simulate(n, k, starts(k), reqs)
                for t in ts:
                    qs[(t, n)].append(A.quotient(r.cum[t - 1], r.opt[t - 1]))
        for t in ts:
            rows.append({"h": h, "T": t, **{n: float(np.mean(qs[(t, n)])) for n in C.VERFAHREN}})
    return rows


def laenge_rows(muster=C.LAENGE_MUSTER, ts=C.LAENGE_TS, k: int = C.LAENGE_K, seeds: int = C.LAENGE_SEEDS) -> list[dict]:
    """Experiment 5: Quotient von Double Coverage über die Länge der Folge (Anfangsstrecken einer Folge der Länge max(ts))."""
    tmax = max(ts)
    rows = []
    for m in muster:
        qs = {t: [] for t in ts}
        for seed in range(seeds):
            reqs = draw_requests(m, k, tmax, 200 + seed) if m not in C.GEBIET_ORTE else draw_gebiet(C.GEBIET_ORTE[m], tmax, 200 + seed)
            r = A.simulate("Double Coverage", k, starts(k), reqs)
            for t in ts:
                qs[t].append(A.quotient(r.cum[t - 1], r.opt[t - 1]))
        for t in ts:
            rows.append({"Muster": m, "T": t, "Quotient": float(np.mean(qs[t])), "Maximum": float(np.max(qs[t]))})
    return rows


# ---------------------------------------------------------------------------------------------------------------------------------
# Verdikte (rein: Art, Text)


def delta_text(value: float, reference: float, label: str) -> tuple[str, str]:
    """Text und Farbregel des Deltas: „mein Wert minus Referenz“. Gleiche Werte (auf zwei Stellen) bekommen keinen Pfeil und keine Farbe."""
    if math.isinf(value):
        return f"unbeschränkt gegen {label}", "inverse"
    d = value - reference
    if abs(d) < 0.005:
        return f"gleich wie {label}", "off"
    return f"{d:+.2f} gegen {label}", "inverse"


def verdict_kern(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Was kostet das hervorgehobene Verfahren gegenüber dem Offline-Optimum, und ist es das billigste?"""
    s = a.settings
    r = a.runs[s.verfahren]
    q = a.ratios[s.verfahren]
    g = A.guarantee(s.verfahren, s.k)
    gtxt = f"Garantie {g}" if g is not None else "keine Garantie"
    billigste = min(C.VERFAHREN, key=lambda n: (a.runs[n].cost, n))
    text = (f"**{s.verfahren}** zahlt bei {s.t} Einsätzen und {s.k} Fahrzeugen **{r.cost}** gegen das Optimum {r.optimum}: Quotient **{fmt(q)}** ({gtxt}, bis auf eine additive Konstante).")
    if s.muster == "Gegner":
        text += " Der Gegner richtet seine Folge nach jedem Verfahren neu aus; verglichen wird deshalb der Quotient, nicht die Strecke."
    elif billigste == s.verfahren:
        text += " Von den drei Verfahren ist es hier das billigste."
    else:
        text += f" Das billigste Verfahren ist hier {billigste} mit {a.runs[billigste].cost}."
    if math.isinf(q) or (s.k >= 2 and q > s.k):
        kind = "warning"
    elif q <= OK_QUOTIENT:
        kind = "success"
    else:
        kind = "info"
    return kind, text


def verdict_gegen(rows: list[dict]) -> tuple[str, str]:
    """Experiment 1: das Gegenbeispiel für Greedy."""
    a, b = rows[0], rows[-1]
    return "warning", (f"Bei {a['m']} Einsätzen ist Greedy mit Quotient {fmt(a['Greedy'])} noch nahe am Optimum, bei {b['m']} Einsätzen zahlt es {b['Kosten Greedy']} gegen das Optimum {b['Optimum']}: "
                       f"Quotient **{fmt(b['Greedy'])}**, und er wächst mit jedem weiteren Einsatz. Double Coverage liegt bei {fmt(b['Double Coverage'])}, die Arbeitsfunktion bei {fmt(b['Arbeitsfunktion'])}.")


def verdict_gegner(rows: list[dict]) -> tuple[str, str]:
    """Experiment 2: der Gegner."""
    dc = ", ".join(f"{fmt(r['Double Coverage'])}" for r in rows)
    wf = ", ".join(f"{fmt(r['Arbeitsfunktion'])}" for r in rows)
    ks = ", ".join(str(r["k"]) for r in rows)
    gmax = max(r["Greedy"] for r in rows)
    return "info", (f"Bei k = {ks} Fahrzeugen erreicht Double Coverage gegen den Gegner die Quotienten **{dc}** (genau k), die Arbeitsfunktion {wf} (ihre Garantie 2k − 1 wird nicht ausgereizt); "
                    f"Greedy kommt auf bis zu {fmt(gmax)}, denn es bewegt immer dasselbe Fahrzeug.")


def verdict_typisch(rows: list[dict]) -> tuple[str, str]:
    """Experiment 3: die Versicherungsprämie."""
    first = rows[0]
    g, d, w = (first["mean"][n] for n in C.VERFAHREN)
    worst = max(rows, key=lambda r: r["mean"]["Double Coverage"] / r["mean"]["Greedy"])
    extra = (worst["mean"]["Double Coverage"] / worst["mean"]["Greedy"] - 1) * 100
    return "info", (f"Bei {first['Muster']}en Einsätzen zahlt Greedy im Mittel das {g:.2f}-Fache des Optimums, die Arbeitsfunktion das {w:.2f}-Fache, Double Coverage das {d:.2f}-Fache. "
                    f"Im ungünstigsten Muster ({worst['Muster']}) kostet Double Coverage {extra:.0f} % mehr als Greedy: Die Garantie ist eine Versicherungsprämie.")


def verdict_gebiet(rows: list[dict]) -> tuple[str, str]:
    """Experiment 4: das konzentrierte Gebiet."""
    tmax = max(r["T"] for r in rows)
    kleine = [r for r in rows if r["T"] == tmax and r["h"] <= C.GEBIET_K]
    grosse = [r for r in rows if r["T"] == tmax and r["h"] > C.GEBIET_K]
    g_max = max(r["Greedy"] for r in kleine)
    d_max = max(r["Double Coverage"] for r in kleine)
    g_gross = ", ".join(f"{r['Greedy']:.2f}" for r in grosse)
    return "warning", (f"Hat das Gebiet höchstens {C.GEBIET_K} Orte (so viele wie Fahrzeuge), zahlt das Optimum nach der Anfahrt nichts mehr: Greedy kommt bei {tmax} Einsätzen auf bis zu **{g_max:.1f}**, "
                       f"Double Coverage auf höchstens {d_max:.2f}. Bei mehr Orten als Fahrzeugen sinkt Greedy auf {g_gross}.")


def verdict_laenge(rows: list[dict], k: int = C.LAENGE_K) -> tuple[str, str]:
    """Experiment 5: die additive Konstante."""
    tmax = max(r["T"] for r in rows)
    ende = [r for r in rows if r["T"] == tmax]
    schluss = ", ".join(f"{r['Muster']} {r['Quotient']:.2f}" for r in ende)
    ueber = [r["Muster"] for r in ende if r["Quotient"] > k]
    text = f"Bei {tmax} Einsätzen liegt Double Coverage bei {schluss}; die Garantie ist k = {k}."
    if ueber:
        text += (f" Bei {', '.join(ueber)} bleibt der Quotient auch bei {tmax} Einsätzen **über k**: Das Optimum zahlt nach der Anfahrt nichts mehr, "
                 "Double Coverage zahlt die Anfahrt mit beiden Fahrzeugen, und die Garantie gilt nur bis auf eine additive Konstante.")
    return "info", text
