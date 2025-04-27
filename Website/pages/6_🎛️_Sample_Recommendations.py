import streamlit as st
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from neo4j_utils import Neo4jConnection
from scipy.spatial.distance import cdist


# ───────────────── PAGE SETUP ─────────────────
st.set_page_config(page_title="🎛️ Sample Recommendations", layout="wide")
st.title("🎛️ Beat-Maker Sample Recommendations")

@st.cache_resource
def get_conn():
    return Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")


conn = get_conn()

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

# Sample selector
stem_query = st.text_input("Search a sample (song title / artist):")
if stem_query:
    raw_hits = conn.query("""
 MATCH (s:Song)                       // 1) start with the song
OPTIONAL MATCH (s)-[:HAS_ARTIST]->(a:Artist)
WITH s, collect(a.name) AS artists   // 2) gather all artist names first
WHERE toLower(s.title) CONTAINS toLower($q)
   OR any(n IN artists WHERE toLower(n) CONTAINS toLower($q))
MATCH (s)-[:RELEASED_IN]->(y:Year)
RETURN id(s) AS id,
       s.title  AS title,
       artists  AS artist,                          // list of names
       coalesce(y.value, s.release_year) AS year    // fallback
ORDER BY year DESC
LIMIT 20
    """, {"q": stem_query})

    df_hits = pd.DataFrame(raw_hits)
    if df_hits.empty:
        st.info("No matches")
        st.stop()

    artist_str = lambda a: ", ".join(a) if isinstance(a, (list, tuple)) else str(a)
    options = {
        f"{r.title} – {artist_str(r.artist)} ({r.year})": r
        for r in df_hits.itertuples()
    }

    choice = st.selectbox("Pick your sample", list(options.keys()))

    if choice:
        stem_row = options[choice]
        stem_id = int(stem_row.id)
        stem_year = int(stem_row.year)

        # random walks
        walks = conn.query("""
          CALL gds.randomWalk.stream(
              'songGraph',
              {
                sourceNodes: [$stem],     // start from the stem song
                walkLength:   4,          // number of hops in each walk
                walksPerNode: 800,        // how many walks to launch
                relationshipWeightProperty: null
              }
            )
            YIELD nodeIds
            UNWIND nodeIds[1..] AS v      // drop the origin from each walk
            RETURN v AS id, count(*) AS hits;
        """, {"stem": stem_id})
        walk_df = pd.DataFrame(walks)
        walk_df["walk_prob"] = walk_df.hits / walk_df.hits.sum()

        # Pull audio features and metadata
        cand_ids = walk_df.id.tolist()
        feature_props = ",\n       ".join([f"t.{c} AS {c}" for c in FEATURE_COLS])

        meta_query = f"""
        UNWIND $ids AS i
        MATCH (t:Song) WHERE id(t)=i
        MATCH (t)-[:HAS_ARTIST]->(a:Artist)
        MATCH (t)-[:RELEASED_IN]->(y:Year)
        RETURN id(t) AS id,
               t.title AS title,
               collect(DISTINCT a.name) AS artist,
               y.value AS year,
               t.n2v AS vec_struct,
               {feature_props}
        """
        meta_df = pd.DataFrame(conn.query(meta_query, {"ids": cand_ids}))
        if meta_df.empty:
            st.warning("Candidates returned 0 rows.")
            st.stop()

        # structural similarity (Node2Vec)
        struct_mat = np.stack(meta_df.vec_struct.apply(lambda v: np.array(v, np.float32)))
        stem_struct = np.array(conn.query(
            "MATCH (s) WHERE id(s)=$id RETURN s.n2v AS v",
            {"id": stem_id})[0]["v"], np.float32).reshape(1, -1)
        meta_df["struct_cos"] = 1 - cdist(stem_struct, struct_mat, "cosine").flatten()

        # audio similarity (scalar features)
        audio_df = meta_df[FEATURE_COLS].astype(float)
        if audio_df.isna().all().all():
            meta_df["audio_cos"] = 0.0
            st.info("⚠️  No scalar audio features present; using graph signals only.")
        else:
            audio_mat = audio_df.to_numpy(dtype=np.float32)
            col_mean = audio_mat.mean(axis=0, keepdims=True)
            col_std = audio_mat.std(axis=0, ddof=0, keepdims=True)
            col_std[col_std == 0] = 1  # avoid /0

            audio_mat_std = (audio_mat - col_mean) / col_std

            stem_audio = conn.query(f"""
                MATCH (s:Song) WHERE id(s)=$id
                RETURN {', '.join(f's.{c} AS {c}' for c in FEATURE_COLS)}
            """, {"id": stem_id})[0]
            stem_audio = np.array([[stem_audio[c] for c in FEATURE_COLS]],
                                  dtype=np.float32)
            stem_audio_std = (stem_audio - col_mean) / col_std
            audio_cos = 1 - cdist(stem_audio_std, audio_mat_std, metric="cosine").flatten()

            meta_df["audio_cos"] = audio_cos


        df = meta_df.merge(walk_df[["id", "walk_prob"]], how="inner")
        df = df[df.year < stem_year].copy()  # vintage filter

        # Slide bar for alpha
        alpha = st.slider("α  (0 = similarity-only, 1 = random-walk-only)",
                          0.0, 1.0, 0.6, 0.05)

        # fallback: if audio_cos is NaN → use struct_cos
        sim = df.audio_cos.where(df.audio_cos.notna(), df.struct_cos)

        df["score"] = alpha * df.walk_prob + (1 - alpha) * sim

        topk = st.slider("Show top-K", 5, 50, 20)
        st.dataframe(
            df.sort_values("score", ascending=False)
            .head(topk)[["title", "artist", "year", "score"]]
            .style.format({"score": "{:.3f}"})
        )
