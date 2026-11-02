"""k-Server – wer fährt hin, wenn ein Einsatz kommt? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Sechstes Stück der Reihe „Online-Algorithmen“: k Servicefahrzeuge auf einem Autobahnabschnitt, Einsätze kommen nacheinander, ein Fahrzeug fährt hin und bleibt dort.
Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import kse_algorithm as A
import kse_constants as C
from kse_evaluation import (
    Settings,
    adv_rows,
    analyse,
    delta_text,
    fmt,
    gebiet_rows,
    gegen_rows,
    laenge_rows,
    ratio_curve,
    typ_rows,
    verdict_gebiet,
    verdict_gegen,
    verdict_gegner,
    verdict_kern,
    verdict_laenge,
    verdict_typisch,
)
from kse_layout import dunkles_design, kopf_css
from kse_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from kse_visualization import build_adv, build_cumulative, build_gebiet, build_gegen, build_laenge, build_ratio, build_route, build_typ

st.set_page_config(page_title="k-Server – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner="Fahre die Einsätze …")
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _gegen():
    return gegen_rows()


@st.cache_data(show_spinner=False)
def _adv():
    return adv_rows()


@st.cache_data(show_spinner="Rechne 30 Folgen je Muster …")
def _typ():
    return typ_rows()


@st.cache_data(show_spinner="Rechne Gebiete mit 1000 Einsätzen über 20 Seeds …")
def _gebiet():
    return gebiet_rows()


@st.cache_data(show_spinner=False)
def _laenge():
    return laenge_rows()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in kse_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🚐 k-Server – wer fährt hin, wenn ein Einsatz kommt?")
st.markdown(
    """
**Sechstes Stück der Reihe „Online-Algorithmen“** (Entscheiden ohne Kenntnis der Zukunft). Auf einem Autobahnabschnitt stehen **k Servicefahrzeuge**. Einsätze kommen nacheinander an Orten, die man vorher nicht kennt; zu jedem fährt **ein Fahrzeug hin und bleibt dort stehen**. Gemessen wird die gefahrene Strecke gegen eine Planung, die alle Einsätze im Voraus kannte.
Die naheliegende Regel, **das nächste Fahrzeug fahren zu lassen**, ist im Alltag gut und hat doch **keine Garantie**. Die Garantie von Double Coverage kostet im Alltag bis zu rund 60 % mehr als Greedy; die Arbeitsfunktion zahlt sie mit wenigen Prozent Aufpreis. Paging (Stück 2) ist der Sonderfall, in dem alle Wege gleich lang sind.

Weiter unten: die **Kernfrage**, fünf Experimente (**Gegenbeispiel für Greedy**, **der Gegner**, **typische Muster**, **konzentriertes Gebiet**, **wann die Garantie gilt**), **🚧 Wo die Annahmen enden**, **⚠️ Annahmen, Grenzen und bekannte Probleme** und **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert k-Server", expanded=True):
    st.markdown(
        """
1. **Die Strecke** hat die Orte 0 bis 12, die k Fahrzeuge starten gleichmäßig verteilt. Bei jedem Einsatz muss danach ein Fahrzeug am Einsatzort stehen; die Kosten sind die gefahrene Strecke.
2. **Die Referenz** kennt alle Einsätze vorher: das **Offline-Optimum**. Das Verhältnis der Kosten eines Verfahrens zum Optimum heißt **Quotient**; gesucht ist ein Verfahren, dessen Quotient immer klein bleibt.
3. **Greedy** schickt das nächste Fahrzeug. **Double Coverage** schickt, wenn der Einsatz zwischen zwei Fahrzeugen liegt, **beide** gleich schnell los, bis eines ankommt; das hält die Fahrzeuge verteilt. Der **Arbeitsfunktionsalgorithmus** rechnet für jede mögliche Aufstellung die besten bisherigen Kosten und wählt die Bewegung, die Kosten und diese Rechnung zusammen minimiert.
4. **Garantien:** Double Coverage ist auf der Geraden höchstens k-mal so teuer wie das Optimum, kein Verfahren ohne Zufall kann besser sein; die Arbeitsfunktion hat die Garantie 2k − 1 in jedem Raum. Beide gelten **bis auf eine additive Konstante** (die Anfahrt am Anfang). Greedy hat keine.
5. **Der Preis der Garantie:** Wer sich gegen den schlimmsten Fall versichert, zahlt bei Double Coverage im Alltag deutlich mehr, bei der Arbeitsfunktion nur wenig. Die Experimente zeigen beides.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Verfahren**")
    verfahren = st.selectbox("Verfahren (hervorgehoben)", C.VERFAHREN, key="verfahren_select", help="Alle drei Verfahren laufen mit; das gewählte steht im Ergebnis und im Verdikt.")
    st.caption(C.VERFAHREN_HILFE[verfahren])
    st.markdown("**Flotte und Einsätze**")
    k = st.slider("Fahrzeuge k", *bounds("k_slider"), key="k_slider", help="Wie viele Fahrzeuge auf der Strecke stehen.")
    muster = st.selectbox("Einsatzmuster", C.MUSTER, key="muster_select", help="Wo die Einsätze anfallen.")
    st.caption(C.MUSTER_HILFE[muster])
    t = st.select_slider("Einsätze T", options=C.T_OPTIONS, key="t_select")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Wirkt auf alle Muster außer dem Gegner (der ist deterministisch).")
    st.button("🎲 Neue Einsätze ziehen", width="stretch", on_click=randomize_seed)

sync_query_params({"k_slider": int(k), "verfahren_select": verfahren, "muster_select": muster, "t_select": int(t), "seed_input": int(seed)})

settings = Settings(int(k), verfahren, muster, int(t), int(seed))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
st.caption(f"{k} Fahrzeuge · {t} Einsätze · Muster „{muster}“ · hervorgehoben: {verfahren}")
run = a.runs[verfahren]
g = A.guarantee(verfahren, int(k))
m1, m2, m3, m4 = st.columns(4)
m1.metric("Gefahrene Strecke", f"{run.cost}", delta=f"{verfahren}", delta_color="off", help="Kosten des hervorgehobenen Verfahrens über alle Einsätze.")
m2.metric("Optimum", f"{run.optimum}", delta="Referenz", delta_color="off", help="Kleinste mögliche Strecke, wenn alle Einsätze im Voraus bekannt sind (beim Gegner: für die Folge dieses Verfahrens).")
d1, c1 = delta_text(a.ratios[verfahren], a.ratios["Greedy"], "Greedy")
m3.metric("Quotient", fmt(a.ratios[verfahren]), delta=d1, delta_color=c1, help="Kosten geteilt durch das Optimum; kleiner ist besser.")
m4.metric("Garantie", f"{g}" if g is not None else "keine", delta="bis auf eine Konstante" if g is not None else "Greedy", delta_color="off", help="Double Coverage: k; Arbeitsfunktion: 2k − 1.")
st.plotly_chart(build_route(run, int(k), verfahren), width="stretch", key="route_chart")
st.caption("Wo die Fahrzeuge (von links gezählt) nach jedem Einsatz stehen; die grauen Punkte sind die Einsätze. Bleibt eine Linie ewig bei null Bewegung, steht das Fahrzeug untätig.")
st.plotly_chart(build_cumulative(a, verfahren), width="stretch", key="cumulative_chart")
st.caption("Gefahrene Strecke über die Zeit, dazu das Optimum der Folge (gestrichelt). Wächst eine Linie dauerhaft steiler als das Optimum, hat das Verfahren die Garantie verloren.")
curves = {n: ratio_curve(a.runs[n]) for n in C.VERFAHREN}
st.plotly_chart(build_ratio(a, curves, int(k)), width="stretch", key="ratio_chart")
st.caption("Quotient nach jedem Einsatz (logarithmische Achse); gestrichelt die Garantie k von Double Coverage. Am Anfang schwankt er stark, weil auch das Optimum noch klein ist.")

with st.expander("Zahlen aller drei Verfahren"):
    st.dataframe(
        pd.DataFrame([{"Verfahren": n, "Strecke": a.runs[n].cost, "Optimum": a.runs[n].optimum, "Quotient": fmt(a.ratios[n]), "Garantie": A.guarantee(n, int(k)) or "keine"} for n in C.VERFAHREN]),
        hide_index=True, width="stretch",
    )

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was kostet das Verfahren gegenüber dem Optimum?")
kind, text = verdict_kern(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Das Gegenbeispiel für Greedy")
rows_ge = _gegen()
st.caption("Zwei Fahrzeuge an den Enden der Strecke (Orte 0 und 12), die Einsätze fallen abwechselnd auf die Orte 5 und 7. Greedy fährt immer dasselbe Fahrzeug hin und her, das zweite steht ewig untätig. Logarithmische Achse.")
st.plotly_chart(build_gegen(rows_ge), width="stretch", key="gegen_chart")
kind, text = verdict_gegen(rows_ge)
getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Experiment 2: Der Gegner")
rows_ad = _adv()
st.caption(f"k + 1 Orte (0 bis k), die Fahrzeuge starten auf 0 bis k − 1; der Gegner fragt nach jedem Einsatz den unbesetzten Ort an. {C.ADV_T} Einsätze, jedes Verfahren bekommt seine eigene Folge. Logarithmische Achse; die Rauten sind der Faktor k.")
st.plotly_chart(build_adv(rows_ad), width="stretch", key="adv_chart")
kind, text = verdict_gegner(rows_ad)
getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Experiment 3: Typische Muster")
rows_ty = _typ()
st.caption(f"{C.TYP_K} Fahrzeuge, {C.TYP_T} Einsätze, Mittel über {C.TYP_SEEDS} feste Seeds. Die Einsätze sind keine Gegner, sondern fallen nach einem Muster an.")
st.plotly_chart(build_typ(rows_ty), width="stretch", key="typ_chart")
kind, text = verdict_typisch(rows_ty)
getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Experiment 4: Ein konzentriertes Gebiet")
rows_gb = _gebiet()
st.caption(f"{C.GEBIET_K} Fahrzeuge starten bei 0, 6 und 12; die Einsätze fallen gleichverteilt auf h Orte im Abstand 2 um die Mitte; Mittel über {C.GEBIET_SEEDS} feste Seeds, die kürzere Folge ist jeweils der Anfang der längeren. Logarithmische Achse.")
st.plotly_chart(build_gebiet(rows_gb), width="stretch", key="gebiet_chart")
kind, text = verdict_gebiet(rows_gb)
getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Experiment 5: Wann gilt die Garantie?")
rows_la = _laenge()
st.caption(f"Double Coverage mit {C.LAENGE_K} Fahrzeugen, Mittel über {C.LAENGE_SEEDS} feste Seeds; die kürzere Folge ist jeweils der Anfang der längsten. Die gestrichelte Linie ist die Garantie k.")
st.plotly_chart(build_laenge(rows_la, C.LAENGE_K), width="stretch", key="laenge_chart")
kind, text = verdict_laenge(rows_la)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Strecke ist eine Gerade** | Double Coverage gilt auf Geraden und Bäumen; in Netzen mit Kreisen und Ringen gilt nur die Arbeitsfunktion (2k − 1), und die Vermutung, dass k überall reicht, ist offen. | – |
| **Das Fahrzeug bleibt am Einsatzort stehen** | Rückfahrt zum Stützpunkt, Einsatzdauer und Zeitfenster machen aus dem Problem ein Tourenproblem. | Online-Tourenplanung (nicht in der Reihe) |
| **Ein Einsatz je Schritt, kein Warten** | Mehrere gleichzeitige Einsätze und Aufträge mit Start und Ziel (Dial-a-Ride) sind schwerer; nicht modelliert. | `patiententransport-demo` für die Offline-Planung |
| **Keine Vorhersage der Orte** | Wer die nächsten Einsatzorte schätzen kann, braucht weniger Versicherung als Double Coverage. | Vorhersagen |
| **Alle Wege gleich lang** | Dann ist das Problem Paging und der Faktor k trifft es genau. | Paging |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(
        f"""
**Annahmen.** Die Strecke hat die ganzzahligen Orte 0 bis {C.GRID}; die Fahrzeuge starten gleichmäßig verteilt (bei k = 1 in der Mitte, beim Gegner auf 0 bis k − 1). Kosten sind gefahrene Orte. Das **Offline-Optimum** wird aus der Arbeitsfunktion gerechnet (Minimum über alle Aufstellungen); die Tests prüfen es gegen zwei getrennte Verfahren (Zuordnung und dynamische Programmierung). Die Muster sind erfunden: gleichverteilt, drei Brennpunkte, eine Irrfahrt mit Schritten bis {C.SCHRITT_MAX}, Gebiete mit 2 bis 6 Orten und der Gegner.

**Grenzen.** Die Demo ist nur an erfundenen Folgen geprüft. Die Garantien k und 2k − 1 gelten **bis auf eine additive Konstante**; deshalb kann der Quotient bei kurzen Folgen über k liegen (Experiment 5 zeigt es). Der Quotient am Anfang einer Folge schwankt stark. Greedy ist im Gegenbeispiel und im Gebiet **nicht beschränkt**, im Mittel über typische Muster aber ungefähr so billig wie die Arbeitsfunktion (Greedy 1 bis 5 % weniger). Die Experimente laufen über feste Seeds und sind Mittelwerte.

**Bekannte Probleme und Unsicherheiten.** Double Coverage ist auf der Geraden definiert; die App behauptet nichts für andere Räume. Die Arbeitsfunktion gilt als wahrscheinlich k-kompetitiv, bewiesen ist 2k − 1. Beim Gegner hängt die Folge vom Verfahren ab; die Quotienten sind dort nicht zwischen den Verfahren vergleichbar, nur gegen k.
        """
    )

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** Auf der Geraden stehen $k$ Fahrzeuge an den Orten $s_1 \le \dots \le s_k$. Ein Einsatz am Ort $r_t$ verlangt, dass nach dem Schritt ein Fahrzeug bei $r_t$ steht; die Kosten sind die Summe aller gefahrenen Strecken. Ein Verfahren entscheidet bei $r_t$, ohne $r_{t+1}, r_{t+2}, \dots$ zu kennen.

| Symbol | Bedeutung |
|---|---|
| $k$ | Zahl der Fahrzeuge |
| $r_t$ | Ort des $t$-ten Einsatzes |
| $\mathrm{ALG}$, $\mathrm{OPT}$ | Kosten des Verfahrens und des Offline-Optimums |
| $w_t(X)$ | Arbeitsfunktion: geringste Kosten, die Einsätze bis $t$ zu bedienen und in der Aufstellung $X$ zu enden |
| $D$ | Durchmesser der Strecke |

**Wettbewerbsverhältnis.** Ein Verfahren heißt $c$-kompetitiv, wenn $\mathrm{ALG} \le c \cdot \mathrm{OPT} + b$ für jede Folge mit einer Konstanten $b$ gilt, die nicht von der Folge abhängt (hier: von der Startaufstellung und $D$).

**Double Coverage.** Liegt $r_t$ außerhalb aller Fahrzeuge, fährt das nächste hin. Liegt $r_t$ zwischen den Nachbarn $s_i < r_t < s_{i+1}$, bewegen sich beide mit gleicher Geschwindigkeit darauf zu, bis eines ankommt; die Kosten sind $2\min(r_t - s_i,\, s_{i+1} - r_t)$. Auf der Geraden gilt $\mathrm{ALG} \le k \cdot \mathrm{OPT} + b$.

**Arbeitsfunktion.** $w_0(X)$ ist die Entfernung der Startaufstellung zu $X$ (Zuordnung der Fahrzeuge in Reihenfolge). Danach
$w_t(X) = \min_{x \in X} \big( w_{t-1}(X - x + r_t) + |x - r_t| \big)$,
und $\mathrm{OPT}_t = \min_X w_t(X)$. Der Algorithmus fährt mit dem Fahrzeug $x$ von seiner Aufstellung $A$ nach $r_t$, das $w_t(A - x + r_t) + |x - r_t|$ minimiert. Er ist $(2k-1)$-kompetitiv.

**Untere Schranke.** Auf $k + 1$ Orten fragt ein Gegner immer den unbesetzten an: jedes deterministische Verfahren zahlt in jedem Schritt mindestens 1, das Optimum höchstens einmal je $k$ Schritte, also Quotient $\ge k$.

**Literatur (nicht nachgebaut; Auszüge per Websuche gesehen, Volltexte nicht eingesehen).** Die Garantie $2k-1$ der Arbeitsfunktion geht auf E. Koutsoupias und C. Papadimitriou zurück; die Faktor-$k$-Vermutung und Double Coverage auf der Geraden auf M. Manasse, L. McGeoch, D. Sleator und M. Chrobak u. a. N. Bansal u. a. (arXiv 1608.08527) behandeln Double Coverage, wenn das Optimum weniger Fahrzeuge hat als das Verfahren ((h,k)-Server-Problem). Hier sind die Zahlen durch vollständiges Durchrechnen belegt, nicht bewiesen.
        """
    )

st.markdown("---")
st.caption(
    "Verwandte Demos: [Ski-Rental](https://github.com/sebastian-hanisch/ski-rental-demo), [Paging](https://github.com/sebastian-hanisch/paging-demo), "
    "[Online-Packen](https://github.com/sebastian-hanisch/online-packen-demo), [Online-Allokation](https://github.com/sebastian-hanisch/online-allokation-demo) und [Sekretärproblem](https://github.com/sebastian-hanisch/sekretaerproblem-demo) (weitere Stücke der Reihe), "
    "Disposition von Hoffahrzeugen (`yard-demo`, Heuristiken ohne Garantie), Krankentransport (`patiententransport-demo`, Offline-Planung mit Dial-a-Ride), "
    "[Online-Matching](https://sebastianhanisch-online-matching-demo.streamlit.app/) (Zuordnen ohne Kenntnis der Zukunft)."
)
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Online-Algorithmen: Entscheiden ohne Zukunft](https://sebastianhanisch.net/konzepte-online-algorithmen.html)."
)
