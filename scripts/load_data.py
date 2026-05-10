import os
import sqlite3
import pandas as pd

# Paths 
BASE_DIR   = os.path.join(os.path.dirname(__file__), '..')
CLEAN_DIR  = os.path.join(BASE_DIR, 'data', 'clean')
SCHEMA_FILE = os.path.join(BASE_DIR, 'schema.sql')
DB_PATH    = os.path.join(BASE_DIR, 'patents.db')

print("=" * 55)
print("  Loading Data into SQLite Database")
print("=" * 55)

# Connect to database 
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
print(f"\n  Database: {os.path.abspath(DB_PATH)}")

#  Create tables from schema.sql 
print("\n  Creating tables from schema.sql...")
with open(SCHEMA_FILE, 'r') as f:
    schema = f.read()
cursor.executescript(schema)
conn.commit()
print("  Tables created successfully.")

#  Helper: load CSV into table 
def load_table(csv_filename, table_name):
    filepath = os.path.join(CLEAN_DIR, csv_filename)
    df = pd.read_csv(filepath, low_memory=False)

    print(f"\n  Loading {csv_filename} → [{table_name}]")
    print(f"    Rows to insert: {len(df):,}")

    # Clear existing data first (so script is re-runnable)
    cursor.execute(f"DELETE FROM {table_name}")

    # Insert into SQLite
    df.to_sql(table_name, conn, if_exists='append', index=False)
    print(f"    Inserted: {len(df):,} rows ✓")

#  Load all tables 
load_table('clean_patents.csv',       'patents')
load_table('clean_inventors.csv',     'inventors')
load_table('clean_companies.csv',     'companies')
load_table('clean_relationships.csv', 'relationships')

conn.commit()

# Verify by counting rows 
print("\n" + "=" * 55)
print("  Verification — Row Counts in Database:")
print("=" * 55)

for table in ['patents', 'inventors', 'companies', 'relationships']:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<20} {count:>10,} rows")

conn.close()
print("\n  Database ready: patents.db")