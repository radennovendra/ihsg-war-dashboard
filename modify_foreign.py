import pandas as pd

path = "data/foreign_cache/foreign_yesterday.csv"
df = pd.read_csv(path)

df["ForeignNet"] = df["ForeignNet"] * 0.9
df.to_csv(path, index=False)

print("modified yesterday")