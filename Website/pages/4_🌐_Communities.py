import streamlit as st
import pandas as pd
import plotly.express as px
from pyvis.network import Network
import streamlit.components.v1 as components
from neo4j_utils import Neo4jConnection

st.set_page_config(page_title="Sampling Communities", page_icon="🌐", layout="wide")
st.title("🌐 Sampling Communities")
st.sidebar.header("Community Selection")


@st.cache_resource
def get_conn():
    return Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")


conn = get_conn()


@st.cache_data
def get_community_list():
    query = """
    MATCH (s:Song)
    WITH s.sampling_community AS community, count(*) AS size
    WHERE size > 50
    RETURN community, size
    ORDER BY size DESC
    """
    return conn.query(query)


@st.cache_data
def get_community_profile(community):
    query = """
    MATCH (s:Song)
    WHERE s.sampling_community = $community
    RETURN 
      avg(s.mood_party) AS party,
      avg(s.mood_sad) AS sad,
      avg(s.mood_relaxed) AS relaxed,
      avg(s.mood_aggressive_aggressive) AS aggressive,
      avg(s.mood_acoustic_acoustic) AS acoustic,
      avg(s.timbre_bright) AS bright,
      avg(s.voice_instrumental_voice) AS voice
    """
    return conn.query(query, {"community": community})[0]


@st.cache_data
def get_top_songs(community, limit=20):
    query = """
    MATCH (s:Song)-[:HAS_ARTIST]->(a:Artist)
    WHERE s.sampling_community = $community
    MATCH (s)-[:BELONGS_TO_GENRE]->(g:Genre)
    RETURN
        s.title AS title,
        collect(DISTINCT a.name) AS artists,
        collect(DISTINCT g.name) AS genres,
        s.pagerank AS pagerank
    ORDER BY s.pagerank DESC
    LIMIT $limit
    """
    return pd.DataFrame(conn.query(query, {"community": community, "limit": limit}))


# Sidebar community selection
communities_data = get_community_list()
community_options = [f"Community {r['community']} ({r['size']} songs)" for r in communities_data]
community_map = {f"Community {r['community']} ({r['size']} songs)": r['community'] for r in communities_data}

selected_label = st.sidebar.selectbox("Select a Community", community_options)
selected_community = community_map[selected_label]

# Audio profile
st.subheader("Audio Profile of Community")
profile = get_community_profile(selected_community)
radar_df = pd.DataFrame({
    "Feature": list(profile.keys()),
    "Score": list(profile.values())
})
fig = px.line_polar(radar_df, r='Score', theta='Feature', line_close=True)
fig.update_traces(fill='toself')
st.plotly_chart(fig, use_container_width=True)

# Top songs table
st.subheader("Top Songs in Community")
top_songs_df = get_top_songs(selected_community)
if not top_songs_df.empty:
    st.dataframe(top_songs_df)
else:
    st.info("No songs with PageRank/audio features in this community.")


@st.cache_data
def get_community_edges(community: int, limit: int = 200):
    query = """
    MATCH (s1:Song)-[:SAMPLES]->(s2:Song)
    WHERE s1.sampling_community = $community AND s2.sampling_community = $community
    RETURN s1.title AS source, s2.title AS target
    LIMIT $limit
    """
    return pd.DataFrame(conn.query(query, {"community": community, "limit": limit}))


# Sampling network visualization
st.subheader("Sampling Network Within Community")

edge_df = get_community_edges(selected_community)

if edge_df.empty:
    st.info("No edges found in this community.")
else:
    net = Network(height="600px", width="100%", directed=True, notebook=False)
    for i, row in edge_df.iterrows():
        source = str(row["source"]) if pd.notnull(row["source"]) else None
        target = str(row["target"]) if pd.notnull(row["target"]) else None

        if source and target:
            net.add_node(source, label=source)
            net.add_node(target, label=target)
            net.add_edge(source, target)

    net.force_atlas_2based()
    net.save_graph("community_graph.html")
    components.html(open("community_graph.html", "r").read(), height=650)
