"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import kse_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _logaxis(fig, values, title, lo=1.0, extra=()):
    """Logarithmische y-Achse von lo bis über den größten (endlichen) Wert."""
    top = max([v for v in list(values) + list(extra) if math.isfinite(v)] + [lo * 2])
    fig.update_yaxes(type="log", range=[math.log10(lo) - 0.02, math.log10(top) + 0.1], title_text=title)


def build_route(run, k: int, name: str):
    """Fahrzeuge (von links gezählt) und Einsätze über der Zeit; die Einsätze sind graue Punkte."""
    xs = list(range(len(run.positions)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(1, len(run.requests) + 1)), y=list(run.requests), mode="markers", name="Einsatz", marker=dict(color=C.COLOR_REQUEST, size=5),
                             hovertemplate="Einsatz %{x} bei Ort %{y}<extra></extra>"))
    palette = ("#2F6B65", "#4c78a8", "#c0392b", "#7c3aed")
    for j in range(k):
        fig.add_trace(go.Scatter(x=xs, y=[p[j] for p in run.positions], mode="lines", line=dict(color=palette[j % len(palette)], width=2, shape="hv"), name=f"Fahrzeug {j + 1} (von links)",
                                 hovertemplate="nach Einsatz %{x}: Ort %{y}<extra></extra>"))
    fig.update_xaxes(title_text="Einsatz")
    fig.update_yaxes(title_text=f"Ort auf der Strecke ({name})", range=[-0.5, C.GRID + 0.5])
    return _base(fig, height=320)


def build_cumulative(a, highlighted: str):
    """Kumulierte Kosten der drei Verfahren und das Optimum (für die Folge des hervorgehobenen Verfahrens)."""
    fig = go.Figure()
    for n in C.VERFAHREN:
        r = a.runs[n]
        fig.add_trace(go.Scatter(x=list(range(1, len(r.cum) + 1)), y=list(r.cum), mode="lines", name=n, line=dict(color=C.COLORS[n], width=4 if n == highlighted else 2),
                                 hovertemplate="nach Einsatz %{x}: %{y}<extra>" + n + "</extra>"))
    h = a.runs[highlighted]
    fig.add_trace(go.Scatter(x=list(range(1, len(h.opt) + 1)), y=list(h.opt), mode="lines", name=f"Optimum (Folge von {highlighted})", line=dict(color=C.COLOR_OPT, width=2, dash="dash"),
                             hovertemplate="nach Einsatz %{x}: %{y}<extra>Optimum</extra>"))
    fig.update_xaxes(title_text="Einsatz")
    fig.update_yaxes(title_text="Gefahrene Strecke (kumuliert)", rangemode="tozero")
    return _base(fig)


def build_ratio(a, curves: dict, k: int):
    """Quotient Kosten / Optimum nach jedem Einsatz, logarithmisch, mit den Garantien k und 2k − 1."""
    fig = go.Figure()
    allv = []
    for n in C.VERFAHREN:
        ys = curves[n]
        allv += [v for v in ys if math.isfinite(v)]
        fig.add_trace(go.Scatter(x=list(range(1, len(ys) + 1)), y=ys, mode="lines", name=n, line=dict(color=C.COLORS[n], width=3), connectgaps=False,
                                 hovertemplate="nach Einsatz %{x}: %{y:.2f}<extra>" + n + "</extra>"))
    if k >= 2:
        fig.add_hline(y=k, line=dict(color=C.COLOR_GUARANTEE, dash="dash"), annotation_text=f"Garantie Double Coverage k = {k}", annotation_position="top left")
    _logaxis(fig, allv, "Quotient zum Optimum (logarithmisch)", extra=[k])
    fig.update_xaxes(title_text="Einsatz")
    return _base(fig)


def build_gegen(rows):
    xs = [str(r["m"]) for r in rows]
    fig = go.Figure()
    allv = []
    for n in C.VERFAHREN:
        ys = [r[n] for r in rows]
        allv += ys
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name=n, line=dict(color=C.COLORS[n], width=3), hovertemplate="m = %{x}: %{y:.2f}<extra>" + n + "</extra>"))
    _logaxis(fig, allv, "Quotient zum Optimum (logarithmisch)")
    fig.update_xaxes(title_text="Zahl der Einsätze m", type="category")
    return _base(fig)


def build_adv(rows):
    xs = [f"k = {r['k']}" for r in rows]
    fig = go.Figure()
    allv = []
    for n in C.VERFAHREN:
        ys = [r[n] for r in rows]
        allv += ys
        fig.add_trace(go.Bar(x=xs, y=ys, name=n, marker_color=C.COLORS[n], hovertemplate="%{x}: %{y:.2f}<extra>" + n + "</extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[r["k"] for r in rows], mode="markers", name="Faktor k", marker=dict(color=C.COLOR_GUARANTEE, symbol="diamond", size=12), hovertemplate="%{x}<extra>Faktor k</extra>"))
    fig.update_layout(barmode="group")
    _logaxis(fig, allv, "Quotient zum Optimum (logarithmisch)")
    return _base(fig, height=320)


def build_typ(rows):
    xs = [r["Muster"] for r in rows]
    fig = go.Figure()
    for n in C.VERFAHREN:
        fig.add_trace(go.Bar(x=xs, y=[r["mean"][n] for r in rows], name=n, marker_color=C.COLORS[n], text=[f"{r['mean'][n]:.2f}" for r in rows], textposition="outside",
                             hovertemplate="%{x}: %{y:.2f}<extra>" + n + "</extra>"))
    fig.update_layout(barmode="group")
    top = max(r["mean"][n] for r in rows for n in C.VERFAHREN)
    fig.update_yaxes(title_text="Mittlerer Quotient zum Optimum", range=[0, top * 1.2])
    return _base(fig, height=320)


def build_gebiet(rows):
    xs = [f"{r['h']} Orte, {r['T']} Einsätze" for r in rows]
    fig = go.Figure()
    allv = []
    for n in C.VERFAHREN:
        ys = [r[n] for r in rows]
        allv += ys
        fig.add_trace(go.Bar(x=xs, y=ys, name=n, marker_color=C.COLORS[n], hovertemplate="%{x}: %{y:.2f}<extra>" + n + "</extra>"))
    fig.update_layout(barmode="group")
    fig.add_hline(y=C.GEBIET_K, line=dict(color=C.COLOR_GUARANTEE, dash="dash"), annotation_text=f"k = {C.GEBIET_K}", annotation_position="top left")
    _logaxis(fig, allv, "Mittlerer Quotient (logarithmisch)", extra=[C.GEBIET_K])
    return _base(fig)


def build_laenge(rows, k: int):
    fig = go.Figure()
    palette = ("#2F6B65", "#4c78a8", "#c0392b")
    muster = list(dict.fromkeys(r["Muster"] for r in rows))
    for i, m in enumerate(muster):
        sub = [r for r in rows if r["Muster"] == m]
        fig.add_trace(go.Scatter(x=[str(r["T"]) for r in sub], y=[r["Quotient"] for r in sub], mode="lines+markers", name=m, line=dict(color=palette[i % 3], width=3),
                                 hovertemplate="%{x} Einsätze: %{y:.2f}<extra>" + m + "</extra>"))
    fig.add_hline(y=k, line=dict(color=C.COLOR_GUARANTEE, dash="dash"), annotation_text=f"Garantie k = {k}", annotation_position="top left")
    top = max(r["Quotient"] for r in rows)
    fig.update_yaxes(title_text="Quotient von Double Coverage", range=[0, max(top, k) * 1.15])
    fig.update_xaxes(title_text="Zahl der Einsätze", type="category")
    return _base(fig)
