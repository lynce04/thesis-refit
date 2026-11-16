import pandas as pd

df = pd.read_csv("data/raw/CLEAN_REFIT_081116/CLEAN_House1.csv", parse_dates=["Time"])
power = df.set_index("Time")["Aggregate"]

max_fill_s = 120

for step_s in [6, 8, 10, 15]:
    grid = power.resample(f"{step_s}s").last()
    empty_pct = grid.isna().mean() * 100
    filled = grid.ffill(limit=max_fill_s // step_s)
    still_empty_pct = filled.isna().mean() * 100
    print(
        f"{step_s:>2} s grid: {len(grid):,} points | "
        f"empty: {empty_pct:.1f} % | "
        f"filled: {empty_pct - still_empty_pct:.1f} % | "
        f"still empty: {still_empty_pct:.1f} %"
    )