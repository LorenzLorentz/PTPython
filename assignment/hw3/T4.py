import sys
import pandas as pd
import numpy as np

df = pd.read_csv(sys.stdin)
df = pd.concat([df, df.map(lambda x: int(100/x) if x!=0 else 0).rename(columns=lambda c: f"inv_{c}")], axis=1)
df = df.drop_duplicates()

print(df.to_csv(sep=" ", header=True, index=False), end="")