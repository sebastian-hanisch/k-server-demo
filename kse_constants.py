"""Konstanten: Regler-Grenzen, feste Annahmen, Experimente, Farben und Presets."""

# Gerade (Autobahnabschnitt): ganzzahlige Orte 0 bis GRID, Fahrzeuge starten gleichmäßig verteilt
GRID = 12
K_MIN, K_MAX, DEFAULT_K = 1, 4, 3
T_OPTIONS = (50, 100, 200, 500)
DEFAULT_T = 100
SEED_MAX, DEFAULT_SEED = 999999, 7

VERFAHREN = ("Greedy", "Double Coverage", "Arbeitsfunktion")
DEFAULT_VERFAHREN = "Double Coverage"
VERFAHREN_HILFE = {
    "Greedy": "Das nächste Fahrzeug fährt hin. Einfach und im Alltag oft gut, hat aber keine Garantie.",
    "Double Coverage": "Liegt der Einsatz zwischen zwei Fahrzeugen, fahren beide gleich schnell darauf zu, bis eines ankommt; außerhalb fährt das nächste. Garantie k auf der Geraden.",
    "Arbeitsfunktion": "Rechnet die besten Kosten für jede mögliche Aufstellung der Fahrzeuge und wählt die Bewegung, die Kosten und Arbeitsfunktion zusammen minimiert. Garantie 2k − 1 in jedem Raum.",
}

MUSTER = ("gleichverteilt", "gebündelt", "wandernd", "Gebiet mit 2 Orten", "Gebiet mit 3 Orten", "Gebiet mit 4 Orten", "Gegner")
DEFAULT_MUSTER = "gleichverteilt"
MUSTER_HILFE = {
    "gleichverteilt": "Jeder Ort der Strecke ist gleich wahrscheinlich.",
    "gebündelt": "Drei Brennpunkte (Orte 2, 6 und 10), um die die Einsätze streuen.",
    "wandernd": "Der Einsatzort wandert in kleinen Schritten (höchstens 2) von der Mitte aus, wie ein Stau.",
    "Gebiet mit 2 Orten": "Alle Einsätze fallen auf nur 2 Orte im Abstand 2 um die Mitte (zum Beispiel eine Baustelle).",
    "Gebiet mit 3 Orten": "Alle Einsätze fallen auf nur 3 Orte im Abstand 2 um die Mitte.",
    "Gebiet mit 4 Orten": "Alle Einsätze fallen auf nur 4 Orte im Abstand 2 um die Mitte.",
    "Gegner": "Der Gegner fragt immer einen Ort an, an dem gerade kein Fahrzeug steht (unter k + 1 Orten 0 bis k); jedes Verfahren bekommt seine eigene Folge.",
}
GEBIET_ORTE = {"Gebiet mit 2 Orten": 2, "Gebiet mit 3 Orten": 3, "Gebiet mit 4 Orten": 4}
BRENNPUNKTE, STREUUNG = (2, 6, 10), 1.0
SCHRITT_MAX = 2

# feste Experimente (nie ein einzelner Seed als Befund)
GEGEN_K, GEGEN_ORTE, GEGEN_MS = 2, (5, 7), (2, 10, 100, 1000)
ADV_KS, ADV_T = (2, 3, 4), 300
TYP_K, TYP_T, TYP_SEEDS = 3, 100, 30
TYP_MUSTER = ("gleichverteilt", "gebündelt", "wandernd")
GEBIET_K, GEBIET_HS, GEBIET_TS, GEBIET_SEEDS = 3, (2, 3, 4, 6), (100, 1000), 20
LAENGE_MUSTER = ("Gebiet mit 2 Orten", "Gebiet mit 3 Orten", "gleichverteilt")
LAENGE_TS = (25, 50, 100, 200, 500, 1000)
LAENGE_K, LAENGE_SEEDS = 3, 20

COLORS = {"Greedy": "#c0392b", "Double Coverage": "#2F6B65", "Arbeitsfunktion": "#4c78a8"}
COLOR_OPT = "#7c7c7c"
COLOR_GUARANTEE = "#d97706"
COLOR_REQUEST = "rgba(150,150,150,0.8)"

PRESETS = {
    "Klassisch (k = 3, gleichverteilt)": {"k": 3, "verfahren": "Double Coverage", "muster": "gleichverteilt", "t": 100, "seed": DEFAULT_SEED},
    "Gegenbeispiel für Greedy": {"k": 2, "verfahren": "Greedy", "muster": "Gebiet mit 2 Orten", "t": 500, "seed": DEFAULT_SEED},
    "Gegner (k = 3)": {"k": 3, "verfahren": "Double Coverage", "muster": "Gegner", "t": 200, "seed": DEFAULT_SEED},
    "Gebiet mit 3 Orten": {"k": 3, "verfahren": "Greedy", "muster": "Gebiet mit 3 Orten", "t": 500, "seed": DEFAULT_SEED},
    "Wandernd (Stau)": {"k": 3, "verfahren": "Arbeitsfunktion", "muster": "wandernd", "t": 200, "seed": DEFAULT_SEED},
    "Ein Fahrzeug (k = 1)": {"k": 1, "verfahren": "Double Coverage", "muster": "gleichverteilt", "t": 100, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Klassisch (k = 3, gleichverteilt)": "Drei Fahrzeuge, Einsätze überall gleich wahrscheinlich: Greedy und Arbeitsfunktion liegen dicht beieinander, Double Coverage zahlt für seine Garantie.",
    "Gegenbeispiel für Greedy": "Zwei Fahrzeuge an den Enden, alle Einsätze auf zwei Orten in der Mitte: Greedy bewegt immer dasselbe Fahrzeug, der Quotient wächst mit der Zahl der Einsätze.",
    "Gegner (k = 3)": "Der Gegner fragt immer den unbesetzten Ort an: Double Coverage erreicht genau den Quotienten k, nicht weniger.",
    "Gebiet mit 3 Orten": "Drei Orte, drei Fahrzeuge: das Optimum zahlt nach der Anfahrt nichts mehr, Greedy zahlt immer weiter.",
    "Wandernd (Stau)": "Der Einsatzort wandert wie ein Stau; die Arbeitsfunktion liegt 26 % über dem Optimum, Greedy 20 %.",
    "Ein Fahrzeug (k = 1)": "Bei einem Fahrzeug gibt es nichts zu entscheiden: alle drei Verfahren sind gleich und optimal.",
}
