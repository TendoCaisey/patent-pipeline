import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

FILES = {
    "patents":    "g_patent.tsv",
    "inventors":  "g_inventor_disambiguated.tsv",
    "companies":  "g_assignee_disambiguated.tsv",
}

for name, filename in FILES.items():
    filepath = os.path.join(RAW_DIR, filename)
    print(f"\n{'='*55}")
    print(f"  {name.upper()} — {filename}")
    print(f"{'='*55}")

    df = pd.read_csv(filepath, sep='\t', nrows=5, low_memory=False)

    print(f"  Columns: {list(df.columns)}")
    print(f"  Shape (5 rows): {df.shape}")
    print(df.head(3).to_string())