# k-Server – wer fährt hin, wenn ein Einsatz kommt? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-k-server-demo.streamlit.app/)** -->

Sechstes Stück der Reihe **Online-Algorithmen** („Entscheiden ohne Kenntnis der Zukunft“) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Kind von [paging-demo](https://github.com/sebastian-hanisch/paging-demo) unter der Wurzel [ski-rental-demo](https://github.com/sebastian-hanisch/ski-rental-demo), neben [online-packen-demo](https://github.com/sebastian-hanisch/online-packen-demo), [online-allokation-demo](https://github.com/sebastian-hanisch/online-allokation-demo) und [sekretaerproblem-demo](https://github.com/sebastian-hanisch/sekretaerproblem-demo).
Anders als die Fall-Demos (ein Anwendungsfall, mehrere Verfahren im Vergleich) zeigt diese Demo **ein** Konzept, **die Wettbewerbsanalyse mit Wegen unterschiedlicher Länge**, an einem wachsenden Beispiel: vom Gegenbeispiel, das die naheliegende Regel widerlegt, über den Gegner, der jedem Verfahren den Faktor k abverlangt, bis zu der Frage, was die Garantie im Alltag kostet.
Kante zum Vorgänger: Paging ist der Fall, in dem alle Wege gleich lang sind; hier haben die Wege Längen, und aus „wer fliegt aus dem Speicher“ wird „welches Fahrzeug fährt hin“.

**Verwandte bestehende Demos:** `yard-demo` (Disposition von Hoffahrzeugen mit Online-Regeln, aber Heuristiken ohne Garantie und ohne Vergleich mit dem Offline-Optimum der Folge), `patiententransport-demo` (Dial-a-Ride-Familie, Offline-Planung mit bekannten Aufträgen), `online-matching-demo` (Zuordnen ohne Kenntnis der Zukunft).

## Warum dieses Problem

Auf einem Autobahnabschnitt stehen k Servicefahrzeuge. Einsätze kommen nacheinander an Orten, die man vorher nicht kennt; zu jedem fährt **ein Fahrzeug hin und bleibt dort stehen**. Die naheliegende Regel schickt das **nächste** Fahrzeug. Die Kernfrage: **Was kostet eine Regel gegenüber einer Planung, die alle Einsätze im Voraus kannte, und ist die Regel mit der besten Garantie auch die beste im Alltag?**

## Modell

Die Strecke hat die ganzzahligen Orte 0 bis 12, die Fahrzeuge starten gleichmäßig verteilt (bei k = 1 in der Mitte). Die Kosten sind die gefahrene Strecke. Drei Verfahren: **Greedy** (das nächste Fahrzeug fährt hin), **Double Coverage** (liegt der Einsatz zwischen zwei Fahrzeugen, fahren beide gleich schnell darauf zu, bis eines ankommt; außerhalb fährt das nächste) und der **Arbeitsfunktionsalgorithmus** (rechnet für jede Aufstellung der Fahrzeuge die besten bisherigen Kosten und wählt die Bewegung, die Kosten und diese Rechnung zusammen minimiert). **Referenz:** das Offline-Optimum der ganzen Folge, aus der Arbeitsfunktion gerechnet. Das Maß ist der **Quotient** Kosten / Optimum. Formeln im 📐-Expander der App.
Die Einsatzmuster: gleichverteilt, gebündelt (drei Brennpunkte), wandernd (Irrfahrt), Gebiete mit 2 bis 4 Orten und der **Gegner**, der nach jedem Schritt den Ort anfragt, an dem gerade kein Fahrzeug steht (unter k + 1 Orten).

## Methodik

| Abschnitt der App | Was gerechnet wird |
|---|---|
| Ergebnis | alle drei Verfahren auf der gewählten Folge; Strecke, Optimum, Quotient, Lauf der Fahrzeuge, kumulierte Kosten, Quotient über die Zeit |
| Experiment 1 | k = 2, Fahrzeuge bei 0 und 12, Einsätze abwechselnd bei 5 und 7, m = 2 bis 1000 |
| Experiment 2 | der Gegner, k = 2 / 3 / 4, 300 Einsätze |
| Experiment 3 | drei Muster, k = 3, 100 Einsätze, Mittel und Maximum über 30 feste Seeds |
| Experiment 4 | Gebiete mit h = 2 / 3 / 4 / 6 Orten, k = 3, 100 und 1000 Einsätze, Mittel über 20 feste Seeds |
| Experiment 5 | Double Coverage über die Länge der Folge (25 bis 1000 Einsätze), drei Muster, 20 feste Seeds |

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen in `tests/test_claims.py` nachgerechnet. Die Quotienten sind Kosten geteilt durch das Optimum; Zahlen mit Seed sind **Stichproben mit festem Seed**, Experiment 1 und 2 sind deterministisch.

| Frage | Befund |
|---|---|
| Drei Fahrzeuge, gleichverteilte Einsätze (Preset, 100 Einsätze, Seed 7)? | Optimum 112; Greedy zahlt 138 (Quotient **1,23**), Arbeitsfunktion 136 (1,21), Double Coverage **202 (1,80)**. |
| Greedy im Gegenbeispiel (Experiment 1)? | Bei m = 2 / 10 / 100 / 1000 Einsätzen zahlt Greedy 7 / 23 / 203 / **2003** gegen das Optimum 7 / 10 / 10 / 10: Quotient 1,00 / 2,30 / 20,30 / **200,30**, in geschlossener Form 5 + 2(m − 1). Double Coverage 1,43 / 1,00 / 1,00 / **1,00**, Arbeitsfunktion 1,00 / 1,80 / 1,80 / 1,80. Das zweite Fahrzeug steht bei Greedy ewig untätig. |
| Der Gegner (Experiment 2, 300 Einsätze)? | Double Coverage **2,00 / 3,00 / 4,00** für k = 2 / 3 / 4, also genau k; die Arbeitsfunktion 2,00 / 3,00 / **3,95** (ihre Garantie 2k − 1 wird nicht ausgereizt); Greedy **150** (Kosten 300, Optimum 2). |
| Was kostet die Garantie im Alltag (Experiment 3, Mittel über 30 Seeds)? | Greedy / Double Coverage / Arbeitsfunktion: gleichverteilt **1,15 / 1,85 / 1,17**, gebündelt 1,12 / 1,80 / 1,14, wandernd 1,41 / 1,92 / 1,48. Double Coverage kostet im Mittel bis zu **61 %** mehr als Greedy (gleichverteilt); das größte Einzelergebnis von Double Coverage liegt bei 2,03 (gleichverteilt) und 2,20 (wandernd). |
| Gebiet mit höchstens k Orten (Experiment 4, k = 3)? | h = 2: Greedy 16,62 bei 100 und **164,90** bei 1000 Einsätzen, Double Coverage 3,33 bei beiden, Arbeitsfunktion 2,22. h = 3: Greedy 9,64 / **85,22**, Double Coverage 2,00, Arbeitsfunktion 2,85. Der Quotient von Greedy wächst mit der Zahl der Einsätze, die beiden anderen nicht. |
| Gebiet mit mehr Orten als Fahrzeugen? | h = 4: Greedy 2,44 / 2,44, Double Coverage 2,80 / 2,97, Arbeitsfunktion 1,43 / 1,41; h = 6: Greedy 1,25 / 1,28, Double Coverage 1,97 / 1,96, Arbeitsfunktion 1,24. Hier ist Greedy wieder besser als Double Coverage. |
| Wann gilt die Garantie (Experiment 5, k = 3)? | Bei einem Gebiet mit 2 Orten liegt Double Coverage bei **3,33** über der Garantie k = 3, und zwar bei **jeder** Länge von 25 bis 1000 Einsätzen: Das Optimum zahlt nach der Anfahrt nichts mehr, und die Garantie gilt nur bis auf eine additive Konstante. Gebiet mit 3 Orten 2,00; gleichverteilt 1,79 bei 25 und 1,80 bei 1000 Einsätzen. |
| Weitere Presets (je ein Seed)? | Gebiet mit 3 Orten (500 Einsätze): Optimum 8, Greedy 350 (**43,75**), Double Coverage und Arbeitsfunktion je 16 (2,00). Wandernd (200 Einsätze): Greedy 1,20, Double Coverage 1,80, Arbeitsfunktion 1,26. Ein Fahrzeug: alle drei zahlen 439 = Optimum. |

## Ehrliche Grenzen

- Die Demo ist **nur an erfundenen Folgen** geprüft: die Muster sind einfache Zufallsmodelle auf einer kleinen Strecke (13 Orte).
- **Garantien bis auf eine additive Konstante:** Der Quotient kann bei kurzen Folgen über k liegen (Experiment 5). Die Tests prüfen nur gemessene, **unbewiesene** Schranken (Double Coverage ≤ k · OPT + k · D, Arbeitsfunktion ≤ (2k − 1) · OPT + (2k − 1) · D); die größte beobachtete Abweichung von Double Coverage lag in einer Vormessung bei etwa 1,05 Streckenlängen für k = 3.
- **Beim Gegner** bekommt jedes Verfahren seine eigene Folge; die Quotienten sind dort nicht zwischen den Verfahren vergleichbar, nur gegen k.
- Double Coverage ist auf der **Geraden** definiert; für andere Räume macht die App keine Aussage. Die Vermutung, dass k für jeden Raum reicht, gilt nach den gefundenen Quellen als **offen**; bewiesen ist für die Arbeitsfunktion der Faktor 2k − 1.
- Die **Primärquellen wurden nicht eingesehen**; es liegen nur Auszüge der Websuche vor (**offen**). Deshalb gibt es keinen Literaturtest.
- Das Fahrzeug **bleibt am Einsatzort stehen** (so ist das Problem definiert); Rückfahrt zum Stützpunkt, Einsatzdauer und Zeitfenster sind nicht modelliert.
- Nicht modelliert: randomisierte Verfahren, Bäume und Kreise, Aufträge mit Start und Ziel (Dial-a-Ride), echte Einsatzdaten.

## Verifikation

- **Umfang:** siehe `pytest --collect-only -q tests`, rund eine Minute lokal.
- **Kern von Hand** (`tests/test_algorithm.py`): Startaufstellungen, ein Fahrzeug (Optimum 11), Greedy, Double Coverage (Fahrzeuge 0 und 12, Einsatz 5: beide fahren 5, Kosten 10) und Arbeitsfunktion (w({5,12}) = 5, w({0,5}) = 7), Gegner, Quotient, Garantie.
- **Orakel** (`tests/test_oracle_kserver.py`): das Optimum der App (Arbeitsfunktion) gegen **zwei getrennte Verfahren**, die Zuordnung (`scipy.linear_sum_assignment`) und die dynamische Programmierung über Aufstellungen, auf 160 Zufallsinstanzen (k = 1 bis 4) und auf typischen Mustern; Greedy und Double Coverage gegen einfach geschriebene Schleifen; das Greedy-Gegenbeispiel in geschlossener Form; die **gleichmäßige Metrik gegen Belady** (80 Instanzen: Paging ist der Sonderfall).
- **Eigenschaften** (`tests/test_eigenschaften_kserver.py`): Optimum ≤ Kosten jedes Verfahrens; jeder Einsatz steht am Ende besetzt; mehr Fahrzeuge machen das Optimum nicht teurer; Double Coverage bewegt höchstens zwei **benachbarte** Fahrzeuge, Greedy höchstens eines; Spiegelung ändert Optimum und Double Coverage nicht; bei k = 1 sind alle Verfahren gleich und optimal; **jedes Verfahren ist gegen den Gegner mindestens k**, Double Coverage genau k; gemessene Schranken (siehe oben); im Gebiet mit höchstens k Orten zahlt das Optimum nur die Anfahrt.
- **Literatur:** kein Referenzwert-Test (siehe oben, **offen**).
- **Verdikte** (`tests/test_verdicts.py`): jede Zahl und jede Verzweigung der Texte. **Claims** (`tests/test_claims.py`): jede Zahl dieser README.
- **Presets, Layout, Oberfläche:** vollständig, Werte in den Reglergrenzen; Permalink übernimmt gültige Werte und begrenzt ungültige; Schnellstart oben in der Seitenleiste, aktives Preset hervorgehoben; AppTest-Rauchtest (jeder Button, jeder Regler an beiden Grenzen, jede Auswahl jedes Auswahlfelds); Footer; Laufzeit-Importe.
- **Browser:** im Desktop-Browser durchgeklickt (Standard, „Gegenbeispiel für Greedy“ und „Gegner“, Seitenleiste, Diagramme, Experiment 4); die übrigen drei Presets nur im AppTest-Rauchtest. Nicht mit echtem Touch-Gerät getestet.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, fünf Experimente, Grenzen, Formeln |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy (nur für das Orakel) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `kse_algorithm.py` | Kern: Arbeitsfunktion, die drei Verfahren, Optimum, Gegner |
| `kse_constants.py` | Regler-Grenzen, feste Annahmen, Experimente, Farben, Presets |
| `kse_evaluation.py` | Kennzahlen, Experimente, Verdikte |
| `kse_layout.py` | Fester Kopf (Stylesheet) |
| `kse_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `kse_scenario.py` | Startaufstellung und Einsatzmuster |
| `kse_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Kern, Randfälle, Orakel, Eigenschaften, Verdikte, Claims, Presets, Layout, Smoke-Test, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Andere Räume:** Bäume (Double Coverage gilt dort), Kreise, allgemeine Graphen. Die gleichmäßige Metrik ist Paging: [paging-demo](https://github.com/sebastian-hanisch/paging-demo).
- **Randomisierte Verfahren** und die Frage, wie gut Zufall hilft.
- **Aufträge mit Start und Ziel** (Dial-a-Ride), Online-Tourenplanung, Rückfahrt zum Stützpunkt, Zeitfenster.
- **Vorhersagen** der Einsatzorte: ein eigenes Stück der Reihe.
- **Echte Einsatzdaten** und PDF-Export.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
