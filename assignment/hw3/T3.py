import sys
import pandas as pd

df = pd.read_csv(sys.stdin)
df = df[~df.duplicated(subset=["text"], keep="first") | (df["keep_if_dup"] == "Yes")]
print(df.to_csv(index=False, sep=' ', header=False))