import os
import pandas as pd
from sklearn.datasets import fetch_openml

print("[+] Fetching UCI German Credit dataset from OpenML...")
raw = fetch_openml("credit-g", version=1, as_frame=True)
df = raw.frame

# Standardize column naming
df["target"] = (df["class"] == "bad").astype(int)  # 1 = Default, 0 = Good
df.drop(columns=["class"], inplace=True)

os.makedirs("data", exist_ok=True)
csv_path = os.path.join("data", "german_credit.csv")
df.to_csv(csv_path, index=False)

print(f"[✓] Dataset saved to {csv_path} ({len(df)} rows, {len(df.columns)} columns)")