import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Music KG Explorer",
    page_icon="🎶",
    layout="wide",
)

# ──────────────────── HEADER ────────────────────
st.title("🎶 Music Sampling Knowledge Graph Explorer")

st.markdown(
    """
    Explore the **Music Sampling Knowledge Graph** to discover how songs and artists are connected through sampling.
    """
)

# ──────────────────── FEATURE OVERVIEW ────────────────────

cols = st.columns(2)
with cols[0]:
    st.markdown("### 🔍 Search & Explore")
    st.markdown("Look up **any song or artist** and instantly see who they sample and who sampled them.")
with cols[1]:
    st.markdown("### 🏆 Impactful Songs")
    st.markdown("Discover the **most influential songs** in the sampling network.")

cols2 = st.columns(2)
with cols2[0]:
    st.markdown("### 📊 Genre Sampling Flow")
    st.markdown("Genre-to-genre **sampling flow** shows how genres influence each other through sampling.")
with cols2[1]:
    st.markdown("### 🌐 Sampling Communities")
    st.markdown("Explore **sampling communities** to see how artists and genres cluster together in the sampling network.")

cols3 = st.columns(2)
with cols3[0]:
    st.markdown("### 🎧 Song Recommendations")
    st.markdown("Discover **new music** based on your favorite songs and their sampling patterns.")
with cols3[1]:
    st.markdown("### 🎛️ Sample Recommendations")
    st.markdown("Find **new samples** based on the audio features and sampling network of your favorite songs or artists.")


st.divider()

# ──────────────────── FOOTER ────────────────────
st.caption(
    "Built for the USC DSCI‑558 Music Sampling KG project · Data sources: WhoSampled, MusicBrainz, AcousticBrainz, Spotify."
)