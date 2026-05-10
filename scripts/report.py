import os
import json
import sqlite3
import pandas as pd

# Paths 
BASE_DIR    = os.path.join(os.path.dirname(__file__), '..')
DB_PATH     = os.path.join(BASE_DIR, 'patents.db')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

#  Run Queries 
top_inventors = pd.read_sql_query("""
    SELECT i.name, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM relationships r
    JOIN inventors i ON r.inventor_id = i.inventor_id
    WHERE r.inventor_id IS NOT NULL
    GROUP BY i.inventor_id, i.name
    ORDER BY patent_count DESC LIMIT 10
""", conn)

top_companies = pd.read_sql_query("""
    SELECT c.name, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM relationships r
    JOIN companies c ON r.company_id = c.company_id
    WHERE r.company_id IS NOT NULL
    GROUP BY c.company_id, c.name
    ORDER BY patent_count DESC LIMIT 10
""", conn)

patents_per_year = pd.read_sql_query("""
    SELECT year, COUNT(*) AS total_patents
    FROM patents WHERE year IS NOT NULL
    GROUP BY year ORDER BY year ASC
""", conn)

total_patents = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM patents", conn
).iloc[0]['total']

total_inventors = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM inventors", conn
).iloc[0]['total']

total_companies = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM companies", conn
).iloc[0]['total']

conn.close()


# A. CONSOLE REPORT

print()
print("=" * 55)
print("       GLOBAL PATENT INTELLIGENCE REPORT")
print("=" * 55)

print(f"""
  Total Patents:    {int(total_patents):>10,}
  Total Inventors:  {int(total_inventors):>10,}
  Total Companies:  {int(total_companies):>10,}
  Years Covered:    {int(patents_per_year['year'].min())} – {int(patents_per_year['year'].max())}
""")

print("─" * 55)
print("  TOP 10 INVENTORS")
print("─" * 55)
for i, row in top_inventors.iterrows():
    print(f"  {i+1:>2}. {row['name']:<35} {int(row['patent_count']):>4} patents")

print()
print("─" * 55)
print("  TOP 10 COMPANIES")
print("─" * 55)
for i, row in top_companies.iterrows():
    print(f"  {i+1:>2}. {row['name']:<35} {int(row['patent_count']):>4} patents")

print()
print("─" * 55)
print("  PATENTS PER YEAR (last 10 years)")
print("─" * 55)
recent = patents_per_year.tail(10)
for _, row in recent.iterrows():
    bar = "█" * (int(row['total_patents']) // 100)
    print(f"  {int(row['year'])}  {int(row['total_patents']):>6,}  {bar}")

print()
print("=" * 55)


# B. CSV REPORTS

top_inventors.to_csv(
    os.path.join(REPORTS_DIR, 'top_inventors.csv'), index=False
)
top_companies.to_csv(
    os.path.join(REPORTS_DIR, 'top_companies.csv'), index=False
)
patents_per_year.to_csv(
    os.path.join(REPORTS_DIR, 'country_trends.csv'), index=False
)
print("\n  CSV reports saved:")
print("    reports/top_inventors.csv")
print("    reports/top_companies.csv")
print("    reports/country_trends.csv")


# C. JSON REPORT

report = {
    "total_patents":   int(total_patents),
    "total_inventors": int(total_inventors),
    "total_companies": int(total_companies),
    "years_covered": {
        "from": int(patents_per_year['year'].min()),
        "to":   int(patents_per_year['year'].max())
    },
    "top_inventors": [
        {"rank": i+1, "name": row['name'], "patents": int(row['patent_count'])}
        for i, row in top_inventors.iterrows()
    ],
    "top_companies": [
        {"rank": i+1, "name": row['name'], "patents": int(row['patent_count'])}
        for i, row in top_companies.iterrows()
    ],
    "patents_per_year": [
        {"year": int(row['year']), "total": int(row['total_patents'])}
        for _, row in patents_per_year.iterrows()
    ]
}

json_path = os.path.join(REPORTS_DIR, 'patent_report.json')
with open(json_path, 'w') as f:
    json.dump(report, f, indent=2)

print("    reports/patent_report.json")
print("\n  All reports generated successfully!")