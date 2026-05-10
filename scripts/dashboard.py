# import os
# import json
# import sqlite3
# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.ticker as mticker
# import seaborn as sns
# import streamlit as st

# #  Config 
# BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
# DB_PATH  = os.path.join(BASE_DIR, 'patents.db')

# st.set_page_config(
#     page_title="Global Patent Intelligence",
#     page_icon="💡",
#     layout="wide"
# )

# #  Load Data 
# @st.cache_data
# def load_data():
#     conn = sqlite3.connect(DB_PATH)

#     patents_per_year = pd.read_sql_query("""
#         SELECT year, COUNT(*) AS total_patents
#         FROM patents WHERE year IS NOT NULL
#         GROUP BY year ORDER BY year ASC
#     """, conn)

#     top_inventors = pd.read_sql_query("""
#         SELECT i.name, COUNT(DISTINCT r.patent_id) AS patent_count
#         FROM relationships r
#         JOIN inventors i ON r.inventor_id = i.inventor_id
#         WHERE r.inventor_id IS NOT NULL
#         GROUP BY i.inventor_id, i.name
#         ORDER BY patent_count DESC LIMIT 20
#     """, conn)

#     top_companies = pd.read_sql_query("""
#         SELECT c.name, COUNT(DISTINCT r.patent_id) AS patent_count
#         FROM relationships r
#         JOIN companies c ON r.company_id = c.company_id
#         WHERE r.company_id IS NOT NULL
#         GROUP BY c.company_id, c.name
#         ORDER BY patent_count DESC LIMIT 20
#     """, conn)

#     patent_types = pd.read_sql_query("""
#         SELECT type, COUNT(*) AS total
#         FROM patents WHERE type IS NOT NULL
#         GROUP BY type ORDER BY total DESC
#     """, conn)

#     recent_patents = pd.read_sql_query("""
#         SELECT p.patent_id, p.title, p.year, p.type,
#                i.name AS inventor_name,
#                c.name AS company_name
#         FROM patents p
#         LEFT JOIN relationships ri
#             ON p.patent_id = ri.patent_id AND ri.inventor_id IS NOT NULL
#         LEFT JOIN inventors i ON ri.inventor_id = i.inventor_id
#         LEFT JOIN relationships rc
#             ON p.patent_id = rc.patent_id AND rc.company_id IS NOT NULL
#         LEFT JOIN companies c ON rc.company_id = c.company_id
#         ORDER BY p.year DESC
#         LIMIT 500
#     """, conn)

#     totals = pd.read_sql_query("""
#         SELECT
#             (SELECT COUNT(*) FROM patents)   AS total_patents,
#             (SELECT COUNT(*) FROM inventors) AS total_inventors,
#             (SELECT COUNT(*) FROM companies) AS total_companies
#     """, conn).iloc[0]

#     conn.close()
#     return patents_per_year, top_inventors, top_companies, patent_types, recent_patents, totals

# patents_per_year, top_inventors, top_companies, patent_types, recent_patents, totals = load_data()

# # Sidebar 
# st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/United_States_Patent_and_Trademark_Office.svg/320px-United_States_Patent_and_Trademark_Office.svg.png", width=200)
# st.sidebar.title("Navigation")
# page = st.sidebar.radio("Go to", [
#     "📊 Overview",
#     "🏆 Top Inventors",
#     "🏢 Top Companies",
#     "📈 Trends Over Time",
#     "🔍 Explore Patents"
# ])

# year_min = int(patents_per_year['year'].min())
# year_max = int(patents_per_year['year'].max())
# st.sidebar.markdown("---")
# st.sidebar.markdown("**Filter by Year Range**")
# year_range = st.sidebar.slider(
#     "Select years", year_min, year_max, (year_min, year_max)
# )

# # Filter patents by year range
# filtered_years = patents_per_year[
#     (patents_per_year['year'] >= year_range[0]) &
#     (patents_per_year['year'] <= year_range[1])
# ]

# sns.set_theme(style="darkgrid")


# # PAGE 1: OVERVIEW

# if page == "📊 Overview":
#     st.title("💡 Global Patent Intelligence Dashboard")
#     st.markdown("Analyzing **100,000 US patents** from 1976 to 2025 — powered by USPTO PatentsView data.")
#     st.markdown("---")

#     # KPI Cards
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Total Patents",   f"{int(totals['total_patents']):,}")
#     col2.metric("Total Inventors", f"{int(totals['total_inventors']):,}")
#     col3.metric("Total Companies", f"{int(totals['total_companies']):,}")
#     col4.metric("Years Covered",   f"{year_min} – {year_max}")

#     st.markdown("---")

#     # Two charts side by side
#     col_left, col_right = st.columns(2)

#     with col_left:
#         st.subheader("📈 Patents Per Year")
#         fig, ax = plt.subplots(figsize=(7, 4))
#         ax.plot(filtered_years['year'], filtered_years['total_patents'],
#                 color='#2196F3', linewidth=2, marker='o', markersize=3)
#         ax.fill_between(filtered_years['year'], filtered_years['total_patents'],
#                         alpha=0.15, color='#2196F3')
#         ax.yaxis.set_major_formatter(mticker.FuncFormatter(
#             lambda x, _: f'{int(x):,}'))
#         ax.set_xlabel("Year")
#         ax.set_ylabel("Patents")
#         plt.tight_layout()
#         st.pyplot(fig)
#         plt.close()

#     with col_right:
#         st.subheader("🥧 Patent Type Breakdown")
#         fig, ax = plt.subplots(figsize=(7, 4))
#         total = patent_types['total'].sum()
#         patent_types['pct'] = patent_types['total'] / total * 100
#         explode = [0.05 if p < 5 else 0 for p in patent_types['pct']]
#         wedges, _, autotexts = ax.pie(
#             patent_types['total'],
#             labels=None,
#             autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
#             colors=sns.color_palette("crest", len(patent_types)),
#             startangle=140,
#             pctdistance=0.75,
#             explode=explode
#         )
#         for at in autotexts:
#             at.set_fontsize(9)
#             at.set_fontweight('bold')
#             at.set_color('white')
#         ax.legend(wedges,
#                   [f"{r['type']} ({int(r['total']):,})"
#                    for _, r in patent_types.iterrows()],
#                   loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
#         plt.tight_layout()
#         st.pyplot(fig)
#         plt.close()


# # PAGE 2: TOP INVENTORS

# elif page == "🏆 Top Inventors":
#     st.title("🏆 Top Inventors")
#     st.markdown("The most prolific inventors in the USPTO patent database.")
#     st.markdown("---")

#     n = st.slider("Show top N inventors", 5, 20, 10)
#     df = top_inventors.head(n).sort_values('patent_count')

#     col1, col2 = st.columns([2, 1])

#     with col1:
#         fig, ax = plt.subplots(figsize=(9, max(4, n * 0.45)))
#         bars = ax.barh(df['name'], df['patent_count'],
#                        color=sns.color_palette("crest", len(df)))
#         for bar, val in zip(bars, df['patent_count']):
#             ax.text(bar.get_width() + 0.3,
#                     bar.get_y() + bar.get_height() / 2,
#                     f'{int(val)}', va='center', fontsize=9, fontweight='bold')
#         ax.set_xlabel("Patent Count")
#         ax.set_title(f"Top {n} Inventors by Patent Count", fontweight='bold')
#         ax.set_xlim(0, df['patent_count'].max() * 1.15)
#         plt.tight_layout()
#         st.pyplot(fig)
#         plt.close()

#     with col2:
#         st.markdown("#### Rankings Table")
#         display_df = top_inventors.head(n).reset_index(drop=True)
#         display_df.index += 1
#         display_df.columns = ['Inventor', 'Patents']
#         st.dataframe(display_df, use_container_width=True)


# # PAGE 3: TOP COMPANIES

# elif page == "🏢 Top Companies":
#     st.title("🏢 Top Companies")
#     st.markdown("Companies holding the most patents in our dataset.")
#     st.markdown("---")

#     n = st.slider("Show top N companies", 5, 20, 10)
#     df = top_companies.head(n).sort_values('patent_count')
#     df['short_name'] = df['name'].apply(
#         lambda x: x if len(x) <= 28 else x[:26] + '...'
#     )

#     col1, col2 = st.columns([2, 1])

#     with col1:
#         fig, ax = plt.subplots(figsize=(9, max(4, n * 0.45)))
#         bars = ax.barh(df['short_name'], df['patent_count'],
#                        color=sns.color_palette("flare", len(df)))
#         for bar, val in zip(bars, df['patent_count']):
#             ax.text(bar.get_width() + 5,
#                     bar.get_y() + bar.get_height() / 2,
#                     f'{int(val):,}', va='center', fontsize=9, fontweight='bold')
#         ax.set_xlabel("Patent Count")
#         ax.set_title(f"Top {n} Companies by Patent Count", fontweight='bold')
#         ax.set_xlim(0, df['patent_count'].max() * 1.18)
#         plt.tight_layout()
#         st.pyplot(fig)
#         plt.close()

#     with col2:
#         st.markdown("#### Rankings Table")
#         display_df = top_companies.head(n).reset_index(drop=True)
#         display_df.index += 1
#         display_df.columns = ['Company', 'Patents']
#         st.dataframe(display_df, use_container_width=True)


# # PAGE 4: TRENDS OVER TIME

# elif page == "📈 Trends Over Time":
#     st.title("📈 Patent Trends Over Time")
#     st.markdown(f"Showing patents from **{year_range[0]}** to **{year_range[1]}** — adjust range in sidebar.")
#     st.markdown("---")

#     fig, ax = plt.subplots(figsize=(13, 5))
#     ax.plot(filtered_years['year'], filtered_years['total_patents'],
#             color='#2196F3', linewidth=2.5, marker='o', markersize=4)
#     ax.fill_between(filtered_years['year'], filtered_years['total_patents'],
#                     alpha=0.15, color='#2196F3')
#     ax.yaxis.set_major_formatter(mticker.FuncFormatter(
#         lambda x, _: f'{int(x):,}'))
#     ax.set_xlabel("Year", fontsize=12)
#     ax.set_ylabel("Total Patents", fontsize=12)
#     ax.set_title("US Patents Granted Per Year", fontsize=15, fontweight='bold')
#     plt.tight_layout()
#     st.pyplot(fig)
#     plt.close()

#     st.markdown("#### Year-by-Year Data")
#     st.dataframe(
#         filtered_years.rename(columns={
#             'year': 'Year', 'total_patents': 'Total Patents'
#         }).set_index('Year'),
#         use_container_width=True
#     )


# # PAGE 5: EXPLORE PATENTS

# elif page == "🔍 Explore Patents":
#     st.title("🔍 Explore Patents")
#     st.markdown("Search and browse individual patent records.")
#     st.markdown("---")

#     search = st.text_input("🔎 Search by title keyword", placeholder="e.g. solar, battery, wireless...")
#     type_filter = st.multiselect(
#         "Filter by patent type",
#         options=recent_patents['type'].dropna().unique().tolist(),
#         default=[]
#     )

#     df = recent_patents.copy()
#     if search:
#         df = df[df['title'].str.contains(search, case=False, na=False)]
#     if type_filter:
#         df = df[df['type'].isin(type_filter)]

#     st.markdown(f"**{len(df):,} patents found**")
#     st.dataframe(
#         df[['patent_id', 'title', 'year', 'type', 'inventor_name', 'company_name']]
#         .drop_duplicates(subset='patent_id')
#         .reset_index(drop=True),
#         use_container_width=True,
#         height=500
#     )

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

# ─── Paths ────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, 'data', 'clean')

st.set_page_config(
    page_title="Global Patent Intelligence",
    page_icon="💡",
    layout="wide"
)

# ─── Hardcoded summary data (from our pipeline results) ───
SUMMARY = {
    "total_patents":   1_000_000,
    "total_inventors": 1_287_067,
    "total_companies": 143_638,
    "year_min": 1976,
    "year_max": 2025,
}

TOP_INVENTORS = [
    {"name": "Shunpei Yamazaki",        "patents": 722},
    {"name": "Tao Luo",                 "patents": 481},
    {"name": "Kia Silverbrook",         "patents": 478},
    {"name": "Jonathan P. Ive",         "patents": 320},
    {"name": "Junyi Li",                "patents": 320},
    {"name": "Frederick E. Shelton IV", "patents": 295},
    {"name": "Kangguo Cheng",           "patents": 293},
    {"name": "Peter Gaal",              "patents": 280},
    {"name": "Duncan Robert Kerr",      "patents": 270},
    {"name": "Bartley K. Andre",        "patents": 264},
]

TOP_COMPANIES = [
    {"name": "Samsung Display Co., Ltd.",                "patents": 18660},
    {"name": "International Business Machines Corp.",    "patents": 17129},
    {"name": "Canon Kabushiki Kaisha",                   "patents": 9699},
    {"name": "Sony Group Corporation",                   "patents": 6783},
    {"name": "Fujitsu Limited",                          "patents": 6056},
    {"name": "Intel Corporation",                        "patents": 5699},
    {"name": "Kabushiki Kaisha Toshiba",                 "patents": 5672},
    {"name": "General Electric Company",                 "patents": 5379},
    {"name": "Lg Electronics Inc.",                      "patents": 5275},
    {"name": "Mitsubishi Electric Corporation",          "patents": 4873},
]

TOP_COUNTRIES = [
    {"country": "US", "patents": 536489},
    {"country": "JP", "patents": 168497},
    {"country": "DE", "patents": 64890},
    {"country": "CN", "patents": 49806},
    {"country": "KR", "patents": 46064},
    {"country": "TW", "patents": 33608},
    {"country": "GB", "patents": 29275},
    {"country": "CA", "patents": 27161},
    {"country": "FR", "patents": 26107},
]

PATENTS_PER_YEAR = [
    (1976,7396),(1977,7470),(1978,7417),(1979,5595),(1980,7041),
    (1981,7563),(1982,6615),(1983,6575),(1984,7635),(1985,8095),
    (1986,8045),(1987,9518),(1988,9008),(1989,10809),(1990,10375),
    (1991,11291),(1992,11415),(1993,11466),(1994,11981),(1995,12129),
    (1996,12911),(1997,13137),(1998,17301),(1999,17964),(2000,18599),
    (2001,19362),(2002,19681),(2003,19679),(2004,19281),(2005,16774),
    (2006,20717),(2007,19418),(2008,19706),(2009,20063),(2010,25881),
    (2011,26128),(2012,29379),(2013,31977),(2014,34539),(2015,34468),
    (2016,35557),(2017,37032),(2018,36181),(2019,41465),(2020,41227),
    (2021,38560),(2022,38184),(2023,37389),(2024,39688),(2025,40313),
]

PATENT_TYPES = [
    {"type": "utility",  "total": 963_000},
    {"type": "design",   "total": 30_000},
    {"type": "plant",    "total": 7_000},
]

# ─── Build DataFrames ─────────────────────────────────────
df_inventors  = pd.DataFrame(TOP_INVENTORS)
df_companies  = pd.DataFrame(TOP_COMPANIES)
df_countries  = pd.DataFrame(TOP_COUNTRIES)
df_years      = pd.DataFrame(PATENTS_PER_YEAR, columns=['year', 'total_patents'])
df_types      = pd.DataFrame(PATENT_TYPES)

# Load companies CSV (small enough to be on GitHub)
@st.cache_data
def load_companies():
    path = os.path.join(CLEAN_DIR, 'clean_companies.csv')
    if os.path.exists(path):
        return pd.read_csv(path, low_memory=False)
    return df_companies.rename(columns={'name': 'name', 'patents': 'patent_count'})

companies_df = load_companies()

# ─── Sidebar ──────────────────────────────────────────────
st.sidebar.title("🔭 Navigation")
page = st.sidebar.radio("Go to", [
    "📊 Overview",
    "🏆 Top Inventors",
    "🏢 Top Companies",
    "🌍 Top Countries",
    "📈 Trends Over Time",
])

st.sidebar.markdown("---")
st.sidebar.markdown("**Filter by Year Range**")
year_range = st.sidebar.slider("Select years", 1976, 2025, (1976, 2025))

filtered_years = df_years[
    (df_years['year'] >= year_range[0]) &
    (df_years['year'] <= year_range[1])
]

sns.set_theme(style="darkgrid")

# ═══════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ═══════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.title("💡 Global Patent Intelligence Dashboard")
    st.markdown("Analyzing **1,000,000 US patents** from 1976–2025 — powered by USPTO PatentsView data.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patents",   f"{SUMMARY['total_patents']:,}")
    col2.metric("Total Inventors", f"{SUMMARY['total_inventors']:,}")
    col3.metric("Total Companies", f"{SUMMARY['total_companies']:,}")
    col4.metric("Years Covered",   f"{SUMMARY['year_min']} – {SUMMARY['year_max']}")

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 Patents Per Year")
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(filtered_years['year'], filtered_years['total_patents'],
                color='#2196F3', linewidth=2, marker='o', markersize=3)
        ax.fill_between(filtered_years['year'], filtered_years['total_patents'],
                        alpha=0.15, color='#2196F3')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(
            lambda x, _: f'{int(x):,}'))
        ax.set_xlabel("Year")
        ax.set_ylabel("Patents")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_right:
        st.subheader("🥧 Patent Type Breakdown")
        fig, ax = plt.subplots(figsize=(7, 4))
        total_t = df_types['total'].sum()
        df_types['pct'] = df_types['total'] / total_t * 100
        explode = [0.05 if p < 5 else 0 for p in df_types['pct']]
        wedges, _, autotexts = ax.pie(
            df_types['total'], labels=None,
            autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
            colors=sns.color_palette("crest", len(df_types)),
            startangle=140, pctdistance=0.75, explode=explode
        )
        for at in autotexts:
            at.set_fontsize(9)
            at.set_fontweight('bold')
            at.set_color('white')
        ax.legend(wedges,
                  [f"{r['type']} ({int(r['total']):,})"
                   for _, r in df_types.iterrows()],
                  loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# ═══════════════════════════════════════════════════════════
# PAGE 2: TOP INVENTORS
# ═══════════════════════════════════════════════════════════
elif page == "🏆 Top Inventors":
    st.title("🏆 Top Inventors")
    st.markdown("The most prolific inventors in the USPTO patent database.")
    st.markdown("---")

    n = st.slider("Show top N inventors", 5, 10, 10)
    df = df_inventors.head(n).sort_values('patents')

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(9, max(4, n * 0.5)))
        bars = ax.barh(df['name'], df['patents'],
                       color=sns.color_palette("crest", len(df)))
        for bar, val in zip(bars, df['patents']):
            ax.text(bar.get_width() + 1,
                    bar.get_y() + bar.get_height() / 2,
                    f'{int(val)}', va='center', fontsize=9, fontweight='bold')
        ax.set_xlabel("Patent Count")
        ax.set_title(f"Top {n} Inventors", fontweight='bold')
        ax.set_xlim(0, df['patents'].max() * 1.15)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    with col2:
        st.markdown("#### Rankings")
        display = df_inventors.head(n).reset_index(drop=True)
        display.index += 1
        display.columns = ['Inventor', 'Patents']
        st.dataframe(display, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# PAGE 3: TOP COMPANIES
# ═══════════════════════════════════════════════════════════
elif page == "🏢 Top Companies":
    st.title("🏢 Top Companies")
    st.markdown("Companies holding the most patents in our dataset.")
    st.markdown("---")

    n = st.slider("Show top N companies", 5, 10, 10)
    df = df_companies.head(n).sort_values('patents')
    df['short_name'] = df['name'].apply(
        lambda x: x if len(x) <= 30 else x[:28] + '...'
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(9, max(4, n * 0.5)))
        bars = ax.barh(df['short_name'], df['patents'],
                       color=sns.color_palette("flare", len(df)))
        for bar, val in zip(bars, df['patents']):
            ax.text(bar.get_width() + 50,
                    bar.get_y() + bar.get_height() / 2,
                    f'{int(val):,}', va='center', fontsize=9, fontweight='bold')
        ax.set_xlabel("Patent Count")
        ax.set_title(f"Top {n} Companies", fontweight='bold')
        ax.set_xlim(0, df['patents'].max() * 1.18)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    with col2:
        st.markdown("#### Rankings")
        display = df_companies.head(n).reset_index(drop=True)
        display.index += 1
        display.columns = ['Company', 'Patents']
        st.dataframe(display, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# PAGE 4: TOP COUNTRIES
# ═══════════════════════════════════════════════════════════
elif page == "🌍 Top Countries":
    st.title("🌍 Patent Distribution by Country")
    st.markdown("Which countries produce the most patents?")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(df_countries['country'], df_countries['patents'],
                       color=sns.color_palette("crest", len(df_countries)))
        for bar, val in zip(bars, df_countries['patents']):
            ax.text(bar.get_width() + 100,
                    bar.get_y() + bar.get_height() / 2,
                    f'{int(val):,}', va='center', fontsize=10, fontweight='bold')
        ax.set_xlabel("Number of Patents", fontsize=12)
        ax.set_title("Top Countries by Patent Count",
                     fontweight='bold', fontsize=14)
        ax.set_xlim(0, df_countries['patents'].max() * 1.18)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    with col2:
        st.markdown("#### Country Rankings")
        display = df_countries.reset_index(drop=True)
        display.index += 1
        display.columns = ['Country', 'Patents']
        st.dataframe(display, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# PAGE 5: TRENDS OVER TIME
# ═══════════════════════════════════════════════════════════
elif page == "📈 Trends Over Time":
    st.title("📈 Patent Trends Over Time")
    st.markdown(f"Showing patents from **{year_range[0]}** to **{year_range[1]}**.")
    st.markdown("---")

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(filtered_years['year'], filtered_years['total_patents'],
            color='#2196F3', linewidth=2.5, marker='o', markersize=4)
    ax.fill_between(filtered_years['year'], filtered_years['total_patents'],
                    alpha=0.15, color='#2196F3')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f'{int(x):,}'))
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Total Patents", fontsize=12)
    ax.set_title("US Patents Granted Per Year",
                 fontsize=15, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("#### Year-by-Year Data")
    st.dataframe(
        filtered_years.rename(columns={
            'year': 'Year', 'total_patents': 'Total Patents'
        }).set_index('Year'),
        use_container_width=True
    )