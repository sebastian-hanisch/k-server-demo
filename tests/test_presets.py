"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen; Permalink; feste Experimente."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

import kse_constants as C
import kse_evaluation as ev
import kse_presets as P

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_control_ranges():
    for name, preset in C.PRESETS.items():
        assert C.K_MIN <= preset["k"] <= C.K_MAX and preset["verfahren"] in C.VERFAHREN and preset["muster"] in C.MUSTER, name
        assert preset["t"] in C.T_OPTIONS and 0 <= preset["seed"] <= C.SEED_MAX, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_every_choice_has_a_help_text_and_defaults_are_valid():
    assert set(C.VERFAHREN_HILFE) == set(C.VERFAHREN) and set(C.MUSTER_HILFE) == set(C.MUSTER) and set(C.COLORS) == set(C.VERFAHREN)
    assert C.DEFAULT_VERFAHREN in C.VERFAHREN and C.DEFAULT_MUSTER in C.MUSTER and C.DEFAULT_T in C.T_OPTIONS and C.K_MIN <= C.DEFAULT_K <= C.K_MAX
    assert list(C.T_OPTIONS) == sorted(C.T_OPTIONS) and set(C.GEBIET_ORTE) <= set(C.MUSTER)


def test_experiment_grids_are_inside_the_controls():
    assert set(C.ADV_KS) <= set(range(C.K_MIN, C.K_MAX + 1)) and C.TYP_K <= C.K_MAX and C.GEBIET_K <= C.K_MAX and C.LAENGE_K <= C.K_MAX
    assert set(C.TYP_MUSTER) <= set(C.MUSTER) and set(C.LAENGE_MUSTER) <= set(C.MUSTER) and set(C.GEGEN_ORTE) <= set(range(C.GRID + 1))
    assert all(len(set(C.BRENNPUNKTE)) == 3 and 0 <= b <= C.GRID for b in C.BRENNPUNKTE)


def test_experiment_rows_have_the_documented_shape():
    rows = ev.gegen_rows(ms=(2, 5))
    assert [r["m"] for r in rows] == [2, 5] and all(set(C.VERFAHREN) <= set(r) for r in rows)
    assert [r["k"] for r in ev.adv_rows(ks=(2,), t=20)] == [2]
    rows = ev.typ_rows(muster=("wandernd",), t=20, seeds=2)
    assert rows[0]["Muster"] == "wandernd" and set(rows[0]["mean"]) == set(C.VERFAHREN) and set(rows[0]["max"]) == set(C.VERFAHREN)
    rows = ev.gebiet_rows(hs=(2,), ts=(10, 20), seeds=2)
    assert [(r["h"], r["T"]) for r in rows] == [(2, 10), (2, 20)]
    rows = ev.laenge_rows(muster=("Gebiet mit 2 Orten", "wandernd"), ts=(10, 20), seeds=2)
    assert [(r["Muster"], r["T"]) for r in rows] == [("Gebiet mit 2 Orten", 10), ("Gebiet mit 2 Orten", 20), ("wandernd", 10), ("wandernd", 20)]


def _app_with(params: dict) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    for key, value in params.items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_permalink_uebernimmt_gueltige_werte():
    at = _app_with({"k": "2", "verfahren": "Greedy", "muster": "wandernd", "t": "200", "seed": "5"})
    state = {k: at.session_state[k] for k in P.SETTING_SPECS}
    assert state == {"k_slider": 2, "verfahren_select": "Greedy", "muster_select": "wandernd", "t_select": 200, "seed_input": 5}


def test_permalink_begrenzt_und_ignoriert_ungueltiges():
    at = _app_with({"k": "99", "t": "77", "verfahren": "gibt es nicht", "muster": "x", "seed": "99999999"})
    assert at.session_state["k_slider"] == C.K_MAX
    assert at.session_state["t_select"] == C.DEFAULT_T                  # 77 ist keine erlaubte Auswahl
    assert at.session_state["verfahren_select"] == C.DEFAULT_VERFAHREN
    assert at.session_state["muster_select"] == C.DEFAULT_MUSTER
    assert at.session_state["seed_input"] == C.SEED_MAX
