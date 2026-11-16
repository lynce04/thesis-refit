# Decision log

Every decision for the thesis, with the reason and the numbers behind it.
Status: **fixed** (decided), **preliminary** (working assumption, may change), **open** (not decided yet).

---

## D1 Topic and scope — fixed
- Basis: approved exposé "Edge-basierte Geräte- und Anomalieerkennung – Vergleich kompakter Deep-Learning-Modelle auf einem ESP32-S3".
- Two tasks on one power signal P(t): event detection (short window around a power jump) and profile anomaly detection (30–60 min windows, 1-min values).
- Models compared for both tasks: LSTM, TCN, Tiny Transformer. Baselines: runtime limit rule, moving average / z-score.
- Training and evaluation on REFIT; own measurements (5–7 days, Shelly Plug M Gen3) only for calibration and practical test, not for training.

## D2 Event classes: load types instead of single appliances — fixed
- Classes: short high load (e.g. kettle), continuous load (e.g. monitor/TV/computer), motor load (e.g. fridge, fan).
- Reason: the practical test uses a kettle, a monitor and a fan. REFIT has kettles in many houses, but almost no monitors or fans as separate channels, so appliance-level classes trained on REFIT could not recognise the test devices. Load types exist in both and match the exposé's system diagram.
- Known limitation: fridges/freezers switch cyclically on their own, the fan is switched by hand. Same load type, different timing behaviour. To be discussed in the evaluation.
- Alternative rejected: appliance-level classes with fine-tuning on own data (contradicts "own data not used for training").

## D3 Dataset version and metadata — fixed
- REFIT cleaned version (CLEAN_REFIT_081116), files in data/raw/ (not in git).
- Appliance-to-channel mapping taken only from CLEAN_READ_ME_081116.txt / MetaData_Tables.xlsx, including noted appliance changes (dates in brackets).
- Facts from the ReadMe that affect preprocessing:
  - `Issues` = 1 when the sum of appliance channels exceeds the aggregate → discard or mark.
  - Sensors are not synchronised (polled every 6–8 s) → a jump in the aggregate and in the appliance channel may be in different rows; labelling needs a tolerance window.
  - Data was recorded only on change; outages exist (notably Feb 2014).

## D4 Data quality, House 1 — finding
- ~6.96 M rows, 2013-10-09 to 2015-07-10 (~639 days).
- Sampling is irregular: median 7 s, mean 7.9 s; frequent spacings 1–3 s and 12–15 s (often pairs adding up to ~14 s).
- 3,440 gaps > 60 s; median gap 66 s; total missing time ~83 days (~13 %). Largest: 2014-01-24 → 2014-03-06 (41.6 days), several multi-day outages in 2015.
- `Issues` = 1 in 58,183 rows (~0.8 %).
- Consequence: one row ≠ fixed time span → data must be put on a fixed time grid before cutting windows; windows must not cross long outages.

## D5 Value per grid bin: last value — preliminary
- `resample(...).last()` instead of `.mean()`.
- Reason: a mean inside a bin containing a jump creates a value that never existed and smears the jump; the last value keeps the jump sharp (shifted by at most one grid step).

## D6 Gap handling — preliminary
- Short gaps (≤ 2 min): forward fill (REFIT records on change, so the value most likely stayed the same).
- Longer gaps: no filling, split data into continuous segments.
- Open: exact limit; current overview uses `ffill(limit=...)`, which also fills the first 2 min of long outages.

## D7 Grid size — open
- Tested on House 1 with 2-min fill limit:

| Grid | Points | Empty | Filled (invented) | Still empty (long outages) |
|---|---|---|---|---|
| 6 s | 9,200,904 | 38.0 % | 25.5 % | 12.5 % |
| 8 s | 6,900,678 | 27.6 % | 15.1 % | 12.5 % |
| 10 s | 5,520,543 | 21.4 % | 8.9 % | 12.5 % |
| 15 s | 3,680,362 | 13.1 % | 0.5 % | 12.5 % |

- Trade-off: larger grid → fewer invented values, shorter windows (less RAM/latency on ESP32), coarser event timing.
- Next: check whether switching events survive on each grid (src/inspect_events_per_grid.py).

## D8 Shelly sampling — preliminary
- No configurable reporting interval found in the official API docs.
- ESP32 polls `Switch.GetStatus` (field `apower`) on a fixed timer matching the chosen grid.
- Open: internal update rate of `apower` → measure early (poll every 1 s for a few minutes).
- Option for task 2: `aenergy.by_minute` gives energy per completed minute.

## D9 Code conventions — fixed
- Python with venv, dependencies in requirements.txt, repo `thesis-refit`, data and venv excluded via .gitignore.
- All code names (variables, functions, columns, output text) in English.

---

## Open questions
- Event definition: jump threshold (currently 100 W as a starting value), window length.
- Train/validation/test split: by houses and/or time blocks — which houses.
- Which REFIT houses are used (depends on load-type coverage).
- Source and format of the annotated REFIT anomalies (Rashid et al. 2019).
- Profile window: 30 or 60 min, step size.