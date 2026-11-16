import pandas as pd

df = pd.read_csv("data/raw/CLEAN_REFIT_081116/CLEAN_House1.csv", parse_dates=["Time"])
print(df.columns.tolist())

dt = df["Time"].diff().dt.total_seconds()
print(dt.describe())
print(dt.value_counts().head(10))
print("Lücken > 60 s:", (dt > 60).sum())
print(df["Issues"].value_counts())