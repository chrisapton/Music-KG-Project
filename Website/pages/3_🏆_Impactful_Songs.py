import streamlit as st
import pandas as pd
from neo4j_utils import Neo4jConnection
import urllib.parse

# ─────────────────────── PAGE SETUP ───────────────────────
st.set_page_config(page_title="PageRank Leaderboard", page_icon="🏆", layout="wide")
st.title("🏆 Top 50 Most Influential Songs in This Network")

# ─────────────────────── NEO4J QUERY ───────────────────────
conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")

query = """
MATCH (s:Song)
WHERE s.pagerank IS NOT NULL
OPTIONAL MATCH (s)<-[:SAMPLES]-(:Song)
WITH s, count(*) AS sampled_by
ORDER BY s.pagerank DESC
LIMIT 50
OPTIONAL MATCH (s)-[:HAS_ARTIST]->(a:Artist)
RETURN s.title AS title,
       collect(DISTINCT a.name) AS artists,
       sampled_by,
       round(s.pagerank, 2) AS pagerank
"""

results = conn.query(query)
conn.close()

# ─────────────────────── DATAFRAME FORMAT ───────────────────────
df = pd.DataFrame(results)
df["Rank"] = range(1, len(df) + 1)
df["artists"] = df["artists"].apply(lambda names: ", ".join(names) if names else "N/A")

df = df[["Rank", "title", "artists", "sampled_by", "pagerank"]]
df.columns = ["Rank", "Song Title", "Artist(s)", "Sampled By", "PageRank Score"]


def make_clickable(title):
    query_params = urllib.parse.urlencode({
        "search_type": "Song",
        "query": title
    })
    return f"[{title}](/Search_and_Explore/?{query_params})"

df["Song Title"] = df["Song Title"].apply(make_clickable)
st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)

# ─────────────────────── DISPLAY ───────────────────────
# st.table(df)








