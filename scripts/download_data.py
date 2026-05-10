import os
import zipfile

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

FILES = [
    "g_patent.tsv.zip",
    "g_inventor_disambiguated.tsv.zip",
    "g_assignee_disambiguated.tsv.zip",
    "g_location_disambiguated.tsv.zip",
]

print("=" * 50)
print("  Unzipping Patent Data Files")
print("=" * 50)

for filename in FILES:
    filepath = os.path.join(RAW_DIR, filename)

    if not os.path.exists(filepath):
        print(f"  NOT FOUND: {filename} — make sure it's in data/raw/")
        continue

    print(f"\n  Unzipping: {filename} ...")
    with zipfile.ZipFile(filepath, 'r') as z:
        z.extractall(RAW_DIR)
    print(f"  Done.")

print("\nAll done! Run: dir data\\raw to verify .tsv files exist")