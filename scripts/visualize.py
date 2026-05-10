import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

#  Paths 
BASE_DIR    = os.path.join(os.path.dirname(__file__), '..')
DB_PATH     = os.path.join(BASE_DIR, 'patents.db')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# Style 
sns.set_theme(style="darkgrid")
PALETTE = sns.color_palette("crest", 10)

print("=" * 55)
print("  Generating Patent Visualizations")
print("=" * 55)


# CHART 1: Patents Per Year (line chart)

print("\n  [1/4] Patents per year...")

df_years = pd.read_sql_query("""
    SELECT year, COUNT(*) AS total_patents
    FROM patents WHERE year IS NOT NULL
    GROUP BY year ORDER BY year ASC
""", conn)

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(df_years['year'], df_years['total_patents'],
        color='#2196F3', linewidth=2.5, marker='o', markersize=3)
ax.fill_between(df_years['year'], df_years['total_patents'],
                alpha=0.15, color='#2196F3')

ax.set_title('US Patents Granted Per Year (1976–2025)',
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Total Patents', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f'{int(x):,}'
))
ax.set_xlim(df_years['year'].min(), df_years['year'].max())
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, 'chart_patents_per_year.png'),
            dpi=150, bbox_inches='tight')
plt.close()
print("    Saved: chart_patents_per_year.png")

# CHART 2: Top 10 Inventors (horizontal bar)

print("\n  [2/4] Top inventors...")

df_inv = pd.read_sql_query("""
    SELECT i.name, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM relationships r
    JOIN inventors i ON r.inventor_id = i.inventor_id
    WHERE r.inventor_id IS NOT NULL
    GROUP BY i.inventor_id, i.name
    ORDER BY patent_count DESC LIMIT 10
""", conn)

df_inv = df_inv.sort_values('patent_count')

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(df_inv['name'], df_inv['patent_count'],
               color=sns.color_palette("crest", len(df_inv)))

# Add value labels on bars
for bar, val in zip(bars, df_inv['patent_count']):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f'{int(val)}', va='center', fontsize=10, fontweight='bold')

ax.set_title('Top 10 Inventors by Patent Count',
             fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Number of Patents', fontsize=12)
ax.set_xlim(0, df_inv['patent_count'].max() * 1.15)
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, 'chart_top_inventors.png'),
            dpi=150, bbox_inches='tight')
plt.close()
print("    Saved: chart_top_inventors.png")


# CHART 3: Top 10 Companies (horizontal bar)

print("\n  [3/4] Top companies...")

df_comp = pd.read_sql_query("""
    SELECT c.name, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM relationships r
    JOIN companies c ON r.company_id = c.company_id
    WHERE r.company_id IS NOT NULL
    GROUP BY c.company_id, c.name
    ORDER BY patent_count DESC LIMIT 10
""", conn)

df_comp = df_comp.sort_values('patent_count')

# Shorten long company names for display
df_comp['short_name'] = df_comp['name'].apply(
    lambda x: x if len(x) <= 30 else x[:28] + '...'
)

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(df_comp['short_name'], df_comp['patent_count'],
               color=sns.color_palette("flare", len(df_comp)))

for bar, val in zip(bars, df_comp['patent_count']):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
            f'{int(val):,}', va='center', fontsize=10, fontweight='bold')

ax.set_title('Top 10 Companies by Patent Count',
             fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Number of Patents', fontsize=12)
ax.set_xlim(0, df_comp['patent_count'].max() * 1.18)
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, 'chart_top_companies.png'),
            dpi=150, bbox_inches='tight')
plt.close()
print("    Saved: chart_top_companies.png")





# CHART 4: Patent Type Breakdown (pie chart)

print("\n  [4/4] Patent types...")

df_types = pd.read_sql_query("""
    SELECT type, COUNT(*) AS total
    FROM patents
    WHERE type IS NOT NULL
    GROUP BY type
    ORDER BY total DESC
""", conn)

fig, ax = plt.subplots(figsize=(9, 7))

# Separate small slices to avoid overlap
total = df_types['total'].sum()
df_types['pct'] = df_types['total'] / total * 100

# Explode small slices outward so labels don't collide
explode = [0.05 if p < 5 else 0 for p in df_types['pct']]

wedges, texts, autotexts = ax.pie(
    df_types['total'],
    labels=None,               # remove inline labels — use legend instead
    autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
    colors=sns.color_palette("crest", len(df_types)),
    startangle=140,
    pctdistance=0.75,
    explode=explode
)

for text in autotexts:
    text.set_fontsize(11)
    text.set_fontweight('bold')
    text.set_color('white')

# Clean legend on the side instead of inline labels
ax.legend(
    wedges,
    [f"{row['type']} ({int(row['total']):,})" for _, row in df_types.iterrows()],
    title="Patent Types",
    loc="center left",
    bbox_to_anchor=(1, 0, 0.5, 1),
    fontsize=10
)

ax.set_title('Patent Type Distribution',
             fontsize=15, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, 'chart_patent_types.png'),
            dpi=150, bbox_inches='tight')
plt.close()
print("    Saved: chart_patent_types.png")