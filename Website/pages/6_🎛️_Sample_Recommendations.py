import streamlit as st
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from neo4j_utils import Neo4jConnection

# ─────────────────────── PAGE SETUP ───────────────────────
st.set_page_config(page_title="🎛️ Sample Recommendations", page_icon="🎛️", layout="wide")
st.title("🎛️ Beat-Maker Sample Recommendations")
st.sidebar.header("Recommendation Settings")

# ─────────────────────── CONNECT TO NEO4J ───────────────────────
@st.cache_resource
def get_conn():
    return Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")

conn = get_conn()

# ─────────────────────── FEATURE COLUMNS ───────────────────────
FEATURE_COLS = [
    "danceability_danceable",
    "genre_dortmund_alternative", "genre_dortmund_blues",
    "genre_dortmund_electronic", "genre_dortmund_folkcountry",
    "genre_dortmund_funksoulrnb", "genre_dortmund_jazz",
    "genre_dortmund_pop", "genre_dortmund_raphiphop",
    "genre_dortmund_rock",
    "genre_electronic_ambient", "genre_electronic_dnb",
    "genre_electronic_house", "genre_electronic_techno",
    "genre_electronic_trance",
    "genre_rosamerica_cla", "genre_rosamerica_dan",
    "genre_rosamerica_hip", "genre_rosamerica_jaz",
    "genre_rosamerica_pop", "genre_rosamerica_rhy",
    "genre_rosamerica_roc", "genre_rosamerica_spe",
    "genre_tzanetakis_blu", "genre_tzanetakis_cla",
    "genre_tzanetakis_cou", "genre_tzanetakis_dis",
    "genre_tzanetakis_hip", "genre_tzanetakis_jaz",
    "genre_tzanetakis_met", "genre_tzanetakis_pop",
    "genre_tzanetakis_reg", "genre_tzanetakis_roc",
    "ismir04_rhythm_ChaChaCha", "ismir04_rhythm_Jive",
    "ismir04_rhythm_Quickstep",
    "ismir04_rhythm_Rumba_American",
    "ismir04_rhythm_Rumba_International",
    "ismir04_rhythm_Rumba_Misc",
    "ismir04_rhythm_Samba", "ismir04_rhythm_Tango",
    "ismir04_rhythm_VienneseWaltz", "ismir04_rhythm_Waltz",
    "mood_acoustic_acoustic", "mood_aggressive_aggressive",
    "mood_electronic_electronic", "mood_happy_happy",
    "mood_party", "mood_relaxed", "mood_sad",
    "timbre_bright", "tonal_atonal_atonal",
    "voice_instrumental_voice"
]

# ─────────────────────── SEARCH FOR STEM SAMPLE ───────────────────────
stem_query = st.text_input("Search a sample (song title / artist):")

if not stem_query:
    st.stop()

# ─────────────────────── FETCH MATCHES ───────────────────────
@st.cache_data(show_spinner="Searching samples...")
def search_samples(query):
    results = conn.query("""
        MATCH (s:Song)
        OPTIONAL MATCH (s)-[:HAS_ARTIST]->(a:Artist)
        WITH s, collect(a.name) AS artists
        WHERE toLower(s.title) CONTAINS toLower($q)
           OR any(n IN artists WHERE toLower(n) CONTAINS toLower($q))
        MATCH (s)-[:RELEASED_IN]->(y:Year)
        RETURN id(s) AS id,
               s.title AS title,
               artists AS artist,
               coalesce(y.value, s.release_year) AS year
        ORDER BY year DESC
        LIMIT 20
    """, {"q": query})
    return results

matches = search_samples(stem_query)

if not matches:
    st.warning("No matches found.")
    st.stop()

df_hits = pd.DataFrame(matches)
artist_str = lambda a: ", ".join(a) if isinstance(a, (list, tuple)) else str(a)

options = {
    f"{r.title} – {artist_str(r.artist)} ({r.year})": r
    for r in df_hits.itertuples()
}

choice = st.selectbox("Pick your sample", list(options.keys()))
if not choice:
    st.stop()

stem_row = options[choice]
stem_id = int(stem_row.id)
stem_year = int(stem_row.year)

# ─────────────────────── RANDOM WALKS ───────────────────────
@st.cache_data(show_spinner="Generating random walks...")
def get_random_walks(stem_node_id):
    query = """
    CALL gds.randomWalk.stream('songGraph', {
        sourceNodes: [$stem],
        walkLength: 4,
        walksPerNode: 800
    })
    YIELD nodeIds
    UNWIND nodeIds[1..] AS v
    RETURN v AS id, count(*) AS hits
    """
    return conn.query(query, {"stem": stem_node_id})

walks = get_random_walks(stem_id)
walk_df = pd.DataFrame(walks)

if walk_df.empty:
    st.warning("Random walks found no candidates.")
    st.stop()

walk_df["walk_prob"] = walk_df.hits / walk_df.hits.sum()

# ─────────────────────── FETCH CANDIDATES METADATA ───────────────────────
@st.cache_data(show_spinner="Fetching candidate metadata...")
def get_candidate_metadata(ids):
    feature_props = ", ".join([f"t.{c} AS {c}" for c in FEATURE_COLS])
    query = f"""
    UNWIND $ids AS i
    MATCH (t:Song) WHERE id(t) = i
    MATCH (t)-[:HAS_ARTIST]->(a:Artist)
    MATCH (t)-[:RELEASED_IN]->(y:Year)
    RETURN id(t) AS id,
           t.title AS title,
           collect(DISTINCT a.name) AS artist,
           y.value AS year,
           t.n2v AS vec_struct,
           {feature_props}
    """
    return conn.query(query, {"ids": ids})

meta = get_candidate_metadata(walk_df.id.tolist())
meta_df = pd.DataFrame(meta)

if meta_df.empty:
    st.warning("Candidates returned 0 results.")
    st.stop()

# ─────────────────────── SIMILARITY COMPUTATIONS ───────────────────────

# Structural (node2vec)
stem_struct = np.array(conn.query(
    "MATCH (s) WHERE id(s) = $id RETURN s.n2v AS v", {"id": stem_id}
)[0]["v"], np.float32).reshape(1, -1)

if meta_df.vec_struct.isnull().all():
    st.warning("Candidates missing structural vectors.")
    st.stop()

struct_mat = np.stack(meta_df.vec_struct.dropna().apply(lambda v: np.array(v, np.float32)))
meta_df["struct_cos"] = 1 - cdist(stem_struct, struct_mat, "cosine").flatten()

# Audio features
audio_df = meta_df[FEATURE_COLS].astype(float)

if audio_df.isna().all().all():
    meta_df["audio_cos"] = np.nan
    st.info("⚠️  No scalar audio features found; using structure only.")
else:
    audio_mat = audio_df.to_numpy(dtype=np.float32)
    col_mean = audio_mat.mean(axis=0, keepdims=True)
    col_std = audio_mat.std(axis=0, ddof=0, keepdims=True)
    col_std[col_std == 0] = 1

    audio_mat_std = (audio_mat - col_mean) / col_std

    stem_audio_raw = conn.query(f"""
        MATCH (s:Song) WHERE id(s)=$id
        RETURN {', '.join(f's.{c}' for c in FEATURE_COLS)}
    """, {"id": stem_id})[0]
    
    stem_audio = np.array([[stem_audio_raw.get(c, 0.0) for c in FEATURE_COLS]], dtype=np.float32)
    stem_audio_std = (stem_audio - col_mean) / col_std

    meta_df["audio_cos"] = 1 - cdist(stem_audio_std, audio_mat_std, metric="cosine").flatten()

# ─────────────────────── SCORE & DISPLAY ───────────────────────
df = meta_df.merge(walk_df[["id", "walk_prob"]], how="inner")
df = df[df.year < stem_year].copy()

alpha = st.sidebar.slider("Mix: Similar Sound (0) vs Sampling Graph (1)", 0.0, 1.0, 0.6, 0.05)

sim = df.audio_cos.where(df.audio_cos.notna(), df.struct_cos)
df["score"] = alpha * df.walk_prob + (1 - alpha) * sim

st.subheader(f"🔎 Recommended Samples Based on: **{stem_row.title}**")
st.dataframe(
    df.sort_values("score", ascending=False)
      .head(100)[["title", "artist", "year", "score"]]
      .style.format({"score": "{:.3f}"})
)

import networkx as nx
import matplotlib.pyplot as plt

# ─────────────────────── SAMPLING GRAPH ───────────────────────
with st.expander("🔗 Show sampling graph (outgoing edges only)"):

    @st.cache_data(show_spinner="Loading sampling tree...")
    def fetch_sampling_tree_full(stem_id):
        query = """
        MATCH path = (s:Song)-[:SAMPLES*1..3]->(sampled:Song)
        WHERE id(s) = $id
        UNWIND relationships(path) AS rel
        WITH startNode(rel) AS src, endNode(rel) AS tgt
        OPTIONAL MATCH (src)-[:HAS_ARTIST]->(src_artist:Artist)
        OPTIONAL MATCH (tgt)-[:HAS_ARTIST]->(tgt_artist:Artist)
        RETURN 
          id(src) AS src_id,
          src.title AS src_title,
          collect(DISTINCT src_artist.name) AS src_artists,
          id(tgt) AS tgt_id,
          tgt.title AS tgt_title,
          collect(DISTINCT tgt_artist.name) AS tgt_artists
        """
        return conn.query(query, {"id": stem_id})

    tree_data = fetch_sampling_tree_full(stem_id)

    if not tree_data:
        st.info("No outgoing samples found from this song.")
    else:
        G = nx.DiGraph()
        id_to_label = {}

        # Add the root node
        stem_artist_str = ", ".join(stem_row.artist) if isinstance(stem_row.artist, list) else str(stem_row.artist)
        stem_label = f"{stem_row.title} – {stem_artist_str}"
        id_to_label[stem_id] = stem_label
        G.add_node(stem_label, color="blue")

        for record in tree_data:
            src_artists = [a for a in record["src_artists"] if a] if isinstance(record["src_artists"], list) else []
            tgt_artists = [a for a in record["tgt_artists"] if a] if isinstance(record["tgt_artists"], list) else []

            src_label = f"{record['src_title']} – {', '.join(src_artists)}" if src_artists else record['src_title']
            tgt_label = f"{record['tgt_title']} – {', '.join(tgt_artists)}" if tgt_artists else record['tgt_title']

            if record["src_id"] not in id_to_label:
                id_to_label[record["src_id"]] = src_label
                G.add_node(src_label, color="orange" if record["src_id"] == stem_id else "gray")

            if record["tgt_id"] not in id_to_label:
                id_to_label[record["tgt_id"]] = tgt_label
                G.add_node(tgt_label, color="orange")

            G.add_edge(id_to_label[record["src_id"]], id_to_label[record["tgt_id"]])

        # 👉 Try Kamada-Kawai layout — works much better for connected graphs
        pos = nx.kamada_kawai_layout(G)

        node_colors = [G.nodes[n].get("color", "gray") for n in G.nodes]

        plt.figure(figsize=(14, 10))
        nx.draw(
            G, pos,
            with_labels=True,
            node_color=node_colors,
            font_size=7,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=12,
        )
        st.pyplot(plt)






