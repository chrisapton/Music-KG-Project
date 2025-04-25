import streamlit as st
import pandas as pd
import plotly.express as px
from neo4j_utils import Neo4jConnection

st.set_page_config(page_title="Sampling Communities", page_icon="🌐", layout="wide")
st.title("🌐 Sampling Communities")
st.sidebar.header("Community Filters")


@st.cache_resource
def get_conn():
    return Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")


conn = get_conn()


@st.cache_data
def get_community_list():
    query = """
    MATCH (s:Song)
    RETURN DISTINCT s.sampling_community AS community
    ORDER BY community
    """
    return [r["community"] for r in conn.query(query)]


@st.cache_data
def get_community_profile(community):
    query = """
    MATCH (s:Song)
    WHERE s.sampling_community = $community
    RETURN 
      avg(s.danceability_danceable) AS danceable,
      avg(s.mood_party) AS party,
      avg(s.mood_sad) AS sad,
      avg(s.timbre_bright) AS bright,
      avg(s.tonal_atonal_atonal) AS atonal
    """
    return conn.query(query, {"community": community})[0]


@st.cache_data
def get_top_songs(community, limit=20):
    query = """
    MATCH (s:Song)
    WHERE s.sampling_community = $community
    RETURN s.whosampled_id AS whosampled_id, s.title AS title, s.danceability_danceable AS danceable
    ORDER BY s.danceability_danceable DESC
    LIMIT $limit
    """
    return pd.DataFrame(conn.query(query, {"community": community, "limit": limit}))


# ─────────────────────── SIDEBAR FILTERS ───────────────────────
communities = get_community_list()
selected_community = st.sidebar.selectbox("Select a Community", communities)

# ─────────────────────── AUDIO PROFILE VISUAL ───────────────────────
st.subheader("🎚️ Audio Profile of Community")
profile = get_community_profile(selected_community)
radar_df = pd.DataFrame({
    "Feature": list(profile.keys()),
    "Score": list(profile.values())
})
fig = px.line_polar(radar_df, r='Score', theta='Feature', line_close=True)
fig.update_traces(fill='toself')
st.plotly_chart(fig, use_container_width=True)

# ─────────────────────── TOP SONGS TABLE ───────────────────────
st.subheader("🎵 Top Songs in Community")
top_songs_df = get_top_songs(selected_community)
if top_songs_df.empty:
    st.info("No songs found in this community.")
else:
    st.dataframe(top_songs_df)
