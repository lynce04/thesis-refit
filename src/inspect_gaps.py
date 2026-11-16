import pandas as pd

df = pd.read_csv("data/raw/CLEAN_REFIT_081116/CLEAN_House1.csv", parse_dates=["Time"])
df["gap_s"] = df["Time"].diff().dt.total_seconds()

print("period:", df["Time"].min(), "-", df["Time"].max())

gaps= df[df["gap_s"] > 60]
print(gaps["gap_s"].describe())
print("Total missing time(days):", gaps["gap_s"].sum() / 60 / 60 / 24)

largest= gaps.nlargest(10, "gap_s")
for idx, row in largest.iterrows():
    start = df.loc[int(idx) - 1, "Time"]
    print(start, "->", row["Time"], f"({row['gap_s']/3600:.1f} h)" )