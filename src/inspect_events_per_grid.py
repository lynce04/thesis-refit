import pandas as pd
# rule: fill gaps up to 2 minutes
max_fill_s = 120
threshold = 100
# load data, time column as timestamps
df = pd.read_csv("data/raw/CLEAN_REFIT_081116/CLEAN_House1.csv", parse_dates=["Time"])
# keep only total power, indexed by time
power = df.set_index("Time")["Aggregate"]

# reference: original data, ignoring jumps across long gaps
df["gap_s"] = df["Time"].diff().dt.total_seconds()
df["delta_p"] = df["Aggregate"].diff()
valid = df["gap_s"] <= max_fill_s
is_event = (df["delta_p"].abs() >= threshold) & valid
print(f"original: {is_event.sum():,} events")

# for each grid size
for step_s in [6, 8, 10, 15]:
    # put power on the grid, keep last value per bin
    grid = power.resample(f"{step_s}s").last()
    # fill short holes, leave long outages empty
    grid = grid.ffill(limit=max_fill_s // step_s)
    # power change between consecutive grid points
    delta_p = grid.diff()
    # count points where |change| >= threshold
    is_event = delta_p.abs() >= threshold
    print(f"{step_s:>2} s grid: {is_event.sum():,} events")