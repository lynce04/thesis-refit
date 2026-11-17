# Entscheidungsprotokoll

Alle Entscheidungen für die Bachelorarbeit mit Begründung und den Zahlen dahinter.
Status: **fest** (entschieden), **vorläufig** (Arbeitsannahme, kann sich ändern), **offen** (noch nicht entschieden).

---

## E1 Thema und Umfang – fest
- Grundlage: genehmigtes Exposé „Edge-basierte Geräte- und Anomalieerkennung – Vergleich kompakter Deep-Learning-Modelle auf einem ESP32-S3".
- Zwei Aufgaben auf demselben Leistungssignal P(t): Eventerkennung (kurzes Fenster um einen Leistungssprung) und Profil-Anomalieerkennung (30–60-Minuten-Fenster, Minutenwerte).
- Verglichene Modelle für beide Aufgaben: LSTM, TCN, Tiny Transformer. Referenzverfahren: Laufzeitgrenze, gleitender Mittelwert / Z-Score.
- Training und Evaluation auf REFIT; eigene Messungen (5–7 Tage, Shelly Plug M Gen3) nur zur Kalibrierung und zum Praxistest, nicht zum Training.

## E2 Eventklassen: Lasttypen statt einzelner Geräte – fest
- Klassen: kurze Hochlast (z. B. Wasserkocher), Dauerlast (z. B. Monitor, Fernseher, Computer), Motorlast (z. B. Kühlschrank, Ventilator).
- Begründung: Der Praxistest nutzt Wasserkocher, Monitor und Ventilator. REFIT enthält Wasserkocher in vielen Häusern, aber kaum Monitore oder Ventilatoren als eigene Kanäle. Ein auf REFIT-Geräteklassen trainiertes Modell könnte die Testgeräte nicht erkennen. Lasttypen gibt es in beiden Datenquellen, und sie entsprechen dem Systemschaubild im Exposé.
- Bekannte Einschränkung: Kühl- und Gefriergeräte schalten zyklisch selbst, der Ventilator wird von Hand geschaltet. Gleicher Lasttyp, anderes zeitliches Verhalten. Wird in der Evaluation diskutiert.
- Verworfene Alternative: Geräteklassen mit Nachtraining auf eigenen Daten (widerspricht „eigene Daten nicht zum Training").

## E3 Datensatzversion und Metadaten – fest
- REFIT, bereinigte Version (CLEAN_REFIT_081116), Dateien in data/raw/ (nicht in Git).
- Zuordnung Gerät ↔ Kanal ausschließlich aus CLEAN_READ_ME_081116.txt / MetaData_Tables.xlsx, inklusive der vermerkten Gerätewechsel (Datumsangaben in Klammern).
- Fakten aus der ReadMe, die die Vorverarbeitung betreffen:
  - `Issues` = 1, wenn die Summe der Gerätekanäle größer ist als der Gesamtverbrauch → verwerfen oder markieren.
  - Sensoren sind nicht synchron (Abfrage alle 6–8 s) → Sprung im Gesamtsignal und im Gerätekanal können in verschiedenen Zeilen liegen; die Labelzuordnung braucht ein Toleranzfenster.
  - Werte wurden nur bei Änderung erfasst; es gibt Ausfälle (vor allem Februar 2014).

## E4 Datenqualität Haus 1 – Befund
- ca. 6,96 Mio. Zeilen, 09.10.2013 bis 10.07.2015 (ca. 639 Tage).
- Messtakt unregelmäßig: Median 7 s, Mittelwert 7,9 s; häufige Abstände 1–3 s und 12–15 s (oft Paare, die zusammen ca. 14 s ergeben).
- 3.440 Lücken > 60 s; Median einer Lücke 66 s; insgesamt fehlen ca. 83 Tage (ca. 13 %). Größte Lücke: 24.01.2014 → 06.03.2014 (41,6 Tage), mehrere mehrtägige Ausfälle 2015.
- `Issues` = 1 in 58.183 Zeilen (ca. 0,8 %).
- Folgerung: Eine Zeile entspricht keiner festen Zeitspanne → Daten vor dem Fensterschneiden auf ein festes Zeitraster bringen; Fenster dürfen nicht über lange Ausfälle reichen.

## E5 Wert pro Rasterfach: letzter Wert – vorläufig
- `resample(...).last()` statt `.mean()`.
- Begründung: Ein Mittelwert in einem Fach mit Sprung erzeugt einen Wert, den es nie gab, und verschmiert den Sprung. Der letzte Wert erhält den Sprung scharf (verschoben um höchstens einen Rasterabstand).

## E6 Umgang mit Lücken – vorläufig
- Kurze Lücken (≤ 2 min): mit dem letzten Wert auffüllen (REFIT erfasst nur bei Änderung, der Wert ist also wahrscheinlich gleich geblieben).
- Längere Lücken: nicht auffüllen, Daten in zusammenhängende Abschnitte teilen.
- Offen: genaue Grenze; die aktuelle Übersicht nutzt `ffill(limit=...)`, das auch die ersten 2 min langer Ausfälle füllt.
- Bei Vergleichen gilt auf beiden Seiten dieselbe Regel: Sprünge über Lücken > 2 min zählen nicht.

## E7 Rastergröße – vorläufig: 8 s
- Test auf Haus 1 mit 2-Minuten-Füllgrenze und Sprungschwelle 100 W (src/inspect_resampling.py, src/inspect_events_per_grid.py):

| Raster | Punkte | Aufgefüllt (erfunden) | Weiter leer (lange Ausfälle) | Sprünge ≥ 100 W | Verlust ggü. Original |
|---|---|---|---|---|---|
| Original | 6.960.008 Zeilen | – | – | 188.939 | – |
| 6 s | 9.200.904 | 25,5 % | 12,5 % | 182.862 | 3,2 % |
| 8 s | 6.900.678 | 15,1 % | 12,5 % | 172.843 | 8,5 % |
| 10 s | 5.520.543 | 8,9 % | 12,5 % | 162.998 | 13,7 % |
| 15 s | 3.680.362 | 0,5 % | 12,5 % | 144.415 | 23,6 % |

- Zielkonflikt: Größeres Raster → weniger aufgefüllte Werte, aber deutlich mehr verlorene Sprünge.
- Die beiden Fehlerarten wiegen unterschiedlich schwer: Aufgefüllte Werte wiederholen meist nur den letzten Wert (REFIT erfasst nur bei Änderung), verlorene Sprünge sind echter Informationsverlust. Das spricht für ein kleineres Raster.
- Fenstergrößen sind bei allen Rastern klein (z. B. 2 min = 20 Punkte bei 6 s, 15 bei 8 s), RAM auf dem ESP32 ist hier kein entscheidendes Kriterium.
- Vorläufige Wahl 8 s: Kompromiss zwischen Sprungverlust (8,5 %) und aufgefüllten Werten (15,1 %); entspricht dem nominellen REFIT-Takt (ca. 8 s) und liegt nahe am häufigsten Abstand (7 s).
- Einschränkung: Gezählt werden Sprünge zwischen Nachbarpunkten, nicht echte Geräteereignisse. Ein Schaltvorgang kann sich über mehrere Zeilen verteilen, und kurze Spitzen unter einem Rasterabstand gehen auf groben Rastern verloren.
- Erneut prüfen, sobald Labels vorliegen: welche Lasttypen verlieren auf welchem Raster Events.

## E8 Abtastung der Shelly – vorläufig
- In der offiziellen API-Doku keine einstellbare Meldeperiode gefunden.
- Der ESP32 fragt `Switch.GetStatus` (Feld `apower`) mit festem Timer im gewählten Raster ab.
- Offen: interne Aktualisierungsrate von `apower` → früh messen (einige Minuten lang jede Sekunde abfragen).
- Option für Aufgabe 2: `aenergy.by_minute` liefert die Energie je abgeschlossener Minute.

## E9 Code-Konventionen – fest
- Python mit venv, Abhängigkeiten in requirements.txt, Repository `thesis-refit`, Daten und venv per .gitignore ausgeschlossen.
- Zugangsdaten (z. B. WLAN-Passwort für den ESP32) liegen in Dateien, die per .gitignore ausgeschlossen sind (`.env`, `secrets.h`).
- Alle Namen im Code (Variablen, Funktionen, Spalten, Ausgabetexte) auf Englisch.

## E10 Sprache und Format der Arbeit – fest
- Die Arbeit wird auf Deutsch geschrieben, in LaTeX (Vorlage HTW-Thesis). Dieses Protokoll ebenfalls auf Deutsch, der Code bleibt englisch (E9).

## E11 Hardware – bestellt
- Mikrocontroller: ESP32-S3-DevKitC-1 N16R8 (Nachbau von diymore, 2 Stück): 16 MB Flash, 8 MB PSRAM.
- Messsteckdose: Shelly Plug M Gen3 (2 Stück), EU-Version für Schuko/Typ-F-Steckdosen, 220–240 V, max. 13 A / 3000 W (ohmsche Last), lokale HTTP-Schnittstelle.
- Folgerungen für den Messaufbau:
  - Die Summe der Testgeräte muss deutlich unter 3000 W bleiben → Wasserkocher mit höchstens ca. 2200 W wählen.
  - Der Monitor braucht ein Eingangssignal (z. B. Laptop), sonst geht er in Standby und liefert keine Dauerlast.
  - Die Testgeräte hängen über eine Mehrfachsteckdose an einer Messsteckdose.
- Offen: Begründung der Hardwahl gegenüber Alternativen im Kapitel Technologieauswahl.

---

## Offene Fragen
- Event-Definition: Sprungschwelle (aktuell 100 W als Startwert), Fensterlänge.
- Aufteilung Training/Validierung/Test: nach Häusern und/oder Zeitblöcken – welche Häuser.
- Welche REFIT-Häuser genutzt werden (abhängig von der Abdeckung der Lasttypen).
- Quelle und Format der annotierten REFIT-Anomalien (Rashid et al. 2019).
- Profilfenster: 30 oder 60 min, Schrittweite.
- Zeitraum des Leistungsgraphen auf der Webseite (F6).