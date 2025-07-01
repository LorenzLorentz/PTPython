import sys
import pandas as pd

df = pd.read_csv(sys.stdin)
df = pd.concat([df, df.map(lambda x: int(100/x) if x!=0 else 0).rename(columns=lambda c: f"inv_{c}")], axis=1)

print(" ".join(df.columns.tolist()))

seen_rows = set()
for row_tuple in df.itertuples(index=False, name=None):
    if row_tuple not in seen_rows:
        print(" ".join(map(str, row_tuple)))
        seen_rows.add(row_tuple)