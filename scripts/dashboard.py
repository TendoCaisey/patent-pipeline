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
BASE_DIR  = os.path.join(os.path.dirname(__file__), '..')
CLEAN_DIR = os.path.join(BASE_DIR, 'data', 'clean')

st.set_page_config(
    page_title="Global Patent Intelligence",
    page_icon="💡",
    layout="wide"
)

# ─── Load Data from CSVs ──────────────────────────────────
@st.cache_data
def load_data():
    patents = pd.read_csv(
        os.path.join(CLEAN_DIR, 'clean_patents.csv'), low_memory=False
    )
    inventors = pd.read_csv(
        os.path.join(CLEAN_DIR, 'clean_inventors.csv'), low_memory=False
    )
    companies = pd.read_csv(
        os.path.join(CLEAN_DIR, 'clean_companies.csv'), low_memory=False
    )
    relationships = pd.read_csv(
        os.path.join(CLEAN_DIR, 'clean_relationships.csv'), low_memory=False
    )

    # ── Patents per year ──
    patents_per_year = (
        patents.dropna(subset=['year'])
        .groupby('year')
        .size()
        .reset_index(name='total_patents')
    )
    patents_per_year['year'] = patents_per_year['year'].astype(int)

    # ── Patent types ──
    patent_types = (
        patents.dropna(subset=['type'])
        .groupby('type')
        .size()
        .reset_index(name='total')
        .sort_values('total', ascending=False)
    )

    # ── Top inventors ──
    inv_rels = relationships.dropna(subset=['inventor_id'])
    inv_counts = (
        inv_rels.groupby('inventor_id')['patent_id']
        .nunique()
        .reset_index(name='patent_count')
    )
    top_inventors = (
        inv_counts.merge(inventors[['inventor_id', 'name']], on='inventor_id')
        .sort_values('patent_count', ascending=False)
        .head(20)
        [['name', 'patent_count']]
        .reset_index(drop=True)
    )

    # ── Top companies ──
    comp_rels = relationships.dropna(subset=['company_id'])
    comp_counts = (
        comp_rels.groupby('company_id')['patent_id']
        .nunique()
        .reset_index(name='patent_count')
    )
    top_companies = (
        comp_counts.merge(companies[['company_id', 'name']], on='company_id')
        .sort_values('patent_count', ascending=False)
        .head(20)
        [['name', 'patent_count']]
        .reset_index(drop=True)
    )

    # ── Top countries ──
    inv_with_country = inv_rels.merge(
        inventors[['inventor_id', 'country']], on='inventor_id', how='left'
    )
    top_countries = (
        inv_with_country.groupby('country')['patent_id']
        .nunique()
        .reset_index(name='patent_count')
        .sort_values('patent_count', ascending=False)
        .head(10)
    )

    # ── Totals ──
    totals = {
        'total_patents':   len(patents),
        'total_inventors': len(inventors),
        'total_companies': len(companies),
    }

    # ── Recent patents sample for explorer ──
    recent = patents.sort_values('year', ascending=False).head(500)

    return (patents, patents_per_year, patent_types,
            top_inventors, top_companies, top_countries,
            totals, recent)

(patents, patents_per_year, patent_types,
 top_inventors, top_companies, top_countries,
 totals, recent) = load_data()

year_min = int(patents_per_year['year'].min())
year_max = int(patents_per_year['year'].max())

# ─── Sidebar ──────────────────────────────────────────────
st.sidebar.title("🔭 Navigation")
page = st.sidebar.radio("Go to", [
    "📊 Overview",
    "🏆 Top Inventors",
    "🏢 Top Companies",
    "🌍 Top Countries",
    "📈 Trends Over Time",
    "🔍 Explore Patents"
])

st.sidebar.markdown("---")
st.sidebar.markdown("**Filter by Year Range**")
year_range = st.sidebar.slider(
    "Select years", year_min, year_max, (year_min, year_max)
)

filtered_years = patents_per_year[
    (patents_per_year['year'] >= year_range[0]) &
    (patents_per_year['year'] <= year_range[1])
]

sns.set_theme(style="darkgrid")

# ═══════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ═══════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.title("💡 Global Patent Intelligence Dashboard")
    st.markdown("Analyzing **1,000,000 US patents** from 1976 to 2025 — powered by USPTO PatentsView data.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patents",   f"{totals['total_patents']:,}")
    col2.metric("Total Inventors", f"{totals['total_inventors']:,}")
    col3.metric("Total Companies", f"{totals['total_companies']:,}")
    col4.metric("Years Covered",   f"{year_min} – {year_max}")

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
        total_t = patent_types['total'].sum()
        patent_types['pct'] = patent_types['total'] / total_t * 100
        explode = [0.05 if p < 5 else 0 for p in patent_types['pct']]
        wedges, _, autotexts = ax.pie(
            patent_types['total'],
            labels=None,
            autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
            colors=sns.color_palette("crest", len(patent_types)),
            startangle=140,
            pctdistance=0.75,
            explode=explode
        )
        for at in autotexts:
            at.set_fontsize(9)
            at.set_fontweight('bold')
            at.set_color('white')
        ax.legend(wedges,
                  [f"{r['type']} ({int(r['total']):,})"
                   for _, r in patent_types.iterrows()],
                  loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("---")
    st.subheader("🌍 Top 10 Countries")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        df_c = top_countries[top_countries['country'] != 'Unknown']
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(df_c['country'], df_c['patent_count'],
                       color=sns.color_palette("crest", len(df_c)))
        for bar, val in zip(bars, df_c['patent_count']):
            ax.text(bar.get_width() + 100,
                    bar.get_y() + bar.get_height() / 2,
                    f'{int(val):,}', va='center', fontsize=9)
        ax.set_xlabel("Patent Count")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    with col_b:
        st.dataframe(
            top_countries.rename(columns={'country': 'Country', 'patent_count': 'Patents'})
            .reset_index(drop=True),
            use_container_width=True
        )

# ═══════════════════════════════════════════════════════════
# PAGE 2: TOP INVENTORS
# ═══════════════════════════════════════════════════════════
elif page == "🏆 Top Inventors":
    st.title("🏆 Top Inventors")
    st.markdown("The most prolific inventors in the USPTO patent database.")
    st.markdown("---")

    n = st.slider("Show top N inventors", 5, 20, 10)
    df = top_inventors.head(n).sort_values('patent_count')

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(9, max(4, n * 0.45)))
        bars = ax.barh(df['name'], df['patent_count'],
                       color=sns.color_palette("crest", len(df)))
        for bar, val in zip(bars, df['patent_count']):
            ax.text(bar.get_width() + 0.3,
                    bar.get_y() + bar.get_height() / 2,
                    f'{int(val)}', va='center', fontsize=9, fontweight='bold')
        ax.set_xlabel("Patent Count")
        ax.set_title(f"Top {n} Inventors", fontweight='bold')
        ax.set_xlim(0, df['patent_count'].max() * 1.15)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    with col2:
        st.markdown("#### Rankings")
        display_df = top_inventors.head(n).reset_index(drop=True)
        display_df.index += 1
        display_df.columns = ['Inventor', 'Patents']
        st.dataframe(display_df, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# PAGE 3: TOP COMPANIES
# ═══════════════════════════════════════════════════════════
elif page == "🏢 Top Companies":
    st.title("🏢 Top Companies")
    st.markdown("Companies holding the most patents in our dataset.")
    st.markdown("---")

    n = st.slider("Show top N companies", 5, 20, 10)
    df = top_companies.head(n).sort_values('patent_count')
    df['short_name'] = df['name'].apply(
        lambda x: x if len(x) <= 28 else x[:26] + '...'
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(9, max(4, n * 0.45)))
        bars = ax.barh(df['short_name'], df['patent_count'],
                       color=sns.color_palette("flare", len(df)))
        for bar, val in zip(bars, df['patent_count']):
            ax.text(bar.get_width() + 5,
                    bar.get_y() + bar.get_height() / 2,
                    f'{int(val):,}', va='center', fontsize=9, fontweight='bold')
        ax.set_xlabel("Patent Count")
        ax.set_title(f"Top {n} Companies", fontweight='bold')
        ax.set_xlim(0, df['patent_count'].max() * 1.18)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    with col2:
        st.markdown("#### Rankings")
        display_df = top_companies.head(n).reset_index(drop=True)
        display_df.index += 1
        display_df.columns = ['Company', 'Patents']
        st.dataframe(display_df, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# PAGE 4: TOP COUNTRIES
# ═══════════════════════════════════════════════════════════
elif page == "🌍 Top Countries":
    st.title("🌍 Patent Distribution by Country")
    st.markdown("Which countries produce the most patents?")
    st.markdown("---")

    df_c = top_countries[top_countries['country'] != 'Unknown'].copy()

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(df_c['country'], df_c['patent_count'],
                       color=sns.color_palette("crest", len(df_c)))
        for bar, val in zip(bars, df_c['patent_count']):
            ax.text(bar.get_width() + 100,
                    bar.get_y() + bar.get_height() / 2,
                    f'{int(val):,}', va='center', fontsize=10, fontweight='bold')
        ax.set_xlabel("Number of Patents", fontsize=12)
        ax.set_title("Top Countries by Patent Count", fontweight='bold', fontsize=14)
        ax.set_xlim(0, df_c['patent_count'].max() * 1.18)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    with col2:
        st.markdown("#### Country Rankings")
        display_df = df_c.reset_index(drop=True)
        display_df.index += 1
        display_df.columns = ['Country', 'Patents']
        st.dataframe(display_df, use_container_width=True)

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
    ax.set_title("US Patents Granted Per Year", fontsize=15, fontweight='bold')
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

# ═══════════════════════════════════════════════════════════
# PAGE 6: EXPLORE PATENTS
# ═══════════════════════════════════════════════════════════
elif page == "🔍 Explore Patents":
    st.title("🔍 Explore Patents")
    st.markdown("Search and browse individual patent records.")
    st.markdown("---")

    search = st.text_input("🔎 Search by title keyword",
                           placeholder="e.g. solar, battery, wireless...")
    type_filter = st.multiselect(
        "Filter by patent type",
        options=patents['type'].dropna().unique().tolist(),
        default=[]
    )
    year_filter = st.slider("Filter by year",
                            year_min, year_max, (year_min, year_max))

    df = patents.copy()
    if search:
        df = df[df['title'].str.contains(search, case=False, na=False)]
    if type_filter:
        df = df[df['type'].isin(type_filter)]
    df = df[(df['year'] >= year_filter[0]) & (df['year'] <= year_filter[1])]

    st.markdown(f"**{len(df):,} patents found**")
    st.dataframe(
        df[['patent_id', 'title', 'year', 'type']]
        .drop_duplicates(subset='patent_id')
        .sort_values('year', ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        height=500
    )