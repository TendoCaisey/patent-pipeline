import os
import pandas as pd

RAW_DIR   = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
CLEAN_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'clean')
os.makedirs(CLEAN_DIR, exist_ok=True)

SAMPLE_SIZE = 1_000_000

print("=" * 55)
print("  Patent Data Cleaning Pipeline")
print("=" * 55)

# 1. PATENTS — random sample across all years

print("\n[1/4] Loading patents...")
patents = pd.read_csv(
    os.path.join(RAW_DIR, 'g_patent.tsv'),
    sep='\t',
    low_memory=False,
    usecols=['patent_id', 'patent_type', 'patent_date', 'patent_title']
)
print(f"  Total rows in file: {len(patents):,}")

# Random sample so we get multiple years
patents = patents.sample(n=min(SAMPLE_SIZE, len(patents)), random_state=42)
print(f"  Sampled: {len(patents):,} rows")

patents = patents.rename(columns={
    'patent_type':  'type',
    'patent_date':  'filing_date',
    'patent_title': 'title',
})
patents['abstract'] = ''
patents['filing_date'] = pd.to_datetime(patents['filing_date'], errors='coerce')
patents['year'] = patents['filing_date'].dt.year

before = len(patents)
patents = patents.dropna(subset=['patent_id', 'title', 'filing_date'])
patents = patents.drop_duplicates(subset='patent_id')
print(f"  Dropped {before - len(patents):,} rows with missing data")

patents = patents[['patent_id', 'title', 'abstract', 'filing_date', 'year', 'type']]
print(f"  Clean patents: {len(patents):,} rows")
print(f"  Years covered: {sorted(patents['year'].dropna().unique().astype(int).tolist())[:10]} ...")

#updated id code
# Build set of patent_ids for filtering
patent_ids = set(patents['patent_id'].astype(str))

# ─────────────────────────────────────────────
# 2. INVENTORS — load all, keep only ones that
#    match our sampled patent_ids
# ─────────────────────────────────────────────
print("\n[2/4] Loading inventors...")

# Load location file for country data
print("  Loading location data...")
locations = pd.read_csv(
    os.path.join(RAW_DIR, 'g_location_disambiguated.tsv'),
    sep='\t',
    low_memory=False,
    usecols=['location_id', 'disambig_country', 'disambig_city', 'disambig_state']
)
# Clean up country names
locations['disambig_country'] = locations['disambig_country'].fillna('Unknown').str.strip()
print(f"  Loaded {len(locations):,} locations")

# Load inventors in chunks, match to our patent_ids
chunks = []
chunk_size = 100_000
reader = pd.read_csv(
    os.path.join(RAW_DIR, 'g_inventor_disambiguated.tsv'),
    sep='\t',
    low_memory=False,
    usecols=['patent_id', 'inventor_id',
             'disambig_inventor_name_first',
             'disambig_inventor_name_last',
             'location_id'],
    chunksize=chunk_size
)
for chunk in reader:
    chunk['patent_id'] = chunk['patent_id'].astype(str)
    matched = chunk[chunk['patent_id'].isin(patent_ids)]
    if len(matched) > 0:
        chunks.append(matched)

inventors_raw = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
print(f"  Matched inventor rows: {len(inventors_raw):,}")

# Join with locations to get country
inventors_raw = inventors_raw.merge(
    locations[['location_id', 'disambig_country', 'disambig_city']],
    on='location_id',
    how='left'
)

# Build full name
inventors_raw['name'] = (
    inventors_raw['disambig_inventor_name_first'].fillna('') + ' ' +
    inventors_raw['disambig_inventor_name_last'].fillna('')
).str.strip()

# Fill missing countries
inventors_raw['disambig_country'] = inventors_raw['disambig_country'].fillna('Unknown')

inventors_raw = inventors_raw.dropna(subset=['inventor_id'])
inventors_raw = inventors_raw[inventors_raw['name'] != '']

# Rename country column
inventors_raw = inventors_raw.rename(columns={'disambig_country': 'country'})

# Unique inventors
inventors = inventors_raw[['inventor_id', 'name', 'country']].drop_duplicates(subset='inventor_id')
print(f"  Unique inventors: {len(inventors):,}")

# Show country breakdown preview
top_countries = inventors['country'].value_counts().head(5)
print(f"  Top countries preview: {top_countries.to_dict()}")


# 3. COMPANIES — same approach, match patent_ids

print("\n[3/4] Loading companies...")
chunks = []
reader = pd.read_csv(
    os.path.join(RAW_DIR, 'g_assignee_disambiguated.tsv'),
    sep='\t',
    low_memory=False,
    usecols=['patent_id', 'assignee_id', 'disambig_assignee_organization'],
    chunksize=chunk_size
)
for chunk in reader:
    chunk['patent_id'] = chunk['patent_id'].astype(str)
    matched = chunk[chunk['patent_id'].isin(patent_ids)]
    if len(matched) > 0:
        chunks.append(matched)

companies_raw = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
print(f"  Matched company rows: {len(companies_raw):,}")

before = len(companies_raw)
companies_raw = companies_raw.dropna(subset=['disambig_assignee_organization', 'assignee_id'])
print(f"  Dropped {before - len(companies_raw):,} rows with missing name/id")

companies_raw = companies_raw.rename(columns={'disambig_assignee_organization': 'name'})
companies_raw['name'] = companies_raw['name'].str.strip().str.title()

companies = companies_raw[['assignee_id', 'name']].drop_duplicates(subset='assignee_id')
companies = companies.rename(columns={'assignee_id': 'company_id'})
print(f"  Unique companies: {len(companies):,}")


# 4. RELATIONSHIPS

print("\n[4/4] Building relationships table...")

patent_inventor = inventors_raw[['patent_id', 'inventor_id']].drop_duplicates()
patent_inventor['company_id'] = None

patent_company = companies_raw[['patent_id', 'assignee_id']].drop_duplicates()
patent_company = patent_company.rename(columns={'assignee_id': 'company_id'})
patent_company['inventor_id'] = None

relationships = pd.concat([patent_inventor, patent_company], ignore_index=True)
relationships = relationships[['patent_id', 'inventor_id', 'company_id']]
print(f"  Total relationship rows: {len(relationships):,}")


# 5. SAVE

print("\nSaving clean files...")
patents.to_csv(os.path.join(CLEAN_DIR, 'clean_patents.csv'), index=False)
inventors.to_csv(os.path.join(CLEAN_DIR, 'clean_inventors.csv'), index=False)
companies.to_csv(os.path.join(CLEAN_DIR, 'clean_companies.csv'), index=False)
relationships.to_csv(os.path.join(CLEAN_DIR, 'clean_relationships.csv'), index=False)

print("\n" + "=" * 55)
print("  Cleaning Complete! Summary:")
print("=" * 55)
print(f"  Patents:       {len(patents):,}")
print(f"  Inventors:     {len(inventors):,}")
print(f"  Companies:     {len(companies):,}")
print(f"  Relationships: {len(relationships):,}")
print(f"\n  Files saved to: data/clean/")