import streamlit as st
import pandas as pd
from neo4j_utils import Neo4jConnection

# ─────────────────────── PAGE SETUP ───────────────────────
st.set_page_config(page_title="🎧 Song Recommendations", page_icon="🎧", layout="wide")
st.title("🎧 Song Recommendations from Sampling Patterns")
st.sidebar.header("Recommendation Settings")

# ─────────────────────── CONNECT ───────────────────────
@st.cache_resource
def get_conn():
    return Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")

conn = get_conn()

# ─────────────────────── GET SONG LIST ───────────────────────
@st.cache_data
def get_all_songs():
    query = "MATCH (s:Song) RETURN DISTINCT s.title AS title ORDER BY s.title"
    return [r["title"] for r in conn.query(query) if r["title"]]

song_list = get_all_songs()
selected_song = st.selectbox("Select a song to base recommendations on", song_list)

if not selected_song:
    st.stop()

# ─────────────────────── GET RECOMMENDATIONS ───────────────────────
@st.cache_data(show_spinner="Fetching recommendations...")
def get_recommendations(title):
    query = """
    MATCH (s:Song {title: $title})-[:SAMPLES]->(sampled:Song)
    WITH sampled
    MATCH (rec:Song)-[:SAMPLES]->(sampled)
    WHERE rec.title <> $title
    OPTIONAL MATCH (rec)-[:HAS_ARTIST]->(a:Artist)
    RETURN rec.title AS recommended_title,
           collect(DISTINCT a.name) AS artists,
           sampled.title AS sampled_source,
           rec.spotify_popularity AS popularity
    ORDER BY popularity DESC
    LIMIT 15
    """
    return conn.query(query, {"title": title})

recs = get_recommendations(selected_song)
df = pd.DataFrame(recs)

# ─────────────────────── DISPLAY RECOMMENDATIONS ───────────────────────
if df.empty:
    st.warning("No recommendations found. This song may not have any sampling connections.")
else:
    df["artists"] = df["artists"].apply(lambda a: ", ".join(a) if a else "Unknown")
    df["popularity"] = df["popularity"].fillna(0).astype(int)
    df = df.rename(columns={
        "recommended_title": "Recommended Song",
        "artists": "Artists",
        "sampled_source": "Shared Sample",
        "popularity": "Spotify Popularity"
    })

    st.subheader(f"Songs that also sampled what **{selected_song}** did")
    st.dataframe(df, use_container_width=True)

# ─────────────────────── OPTIONAL: SHOW PATH GRAPH ───────────────────────
with st.expander("🔗 Show sampling graph (co-samplers)"):
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph()
    G.add_node(selected_song, color="blue")

    for row in recs:
        G.add_node(row["recommended_title"], color="orange")
        G.add_node(row["sampled_source"], color="gray")
        G.add_edge(selected_song, row["sampled_source"])
        G.add_edge(row["recommended_title"], row["sampled_source"])

    pos = nx.spring_layout(G, seed=42)
    colors = [G.nodes[n].get("color", "gray") for n in G.nodes]
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_color=colors, font_size=9, arrows=True)
    st.pyplot(plt)
