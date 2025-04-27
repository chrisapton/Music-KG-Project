import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from neo4j_utils import Neo4jConnection

# ─────────────────────── PAGE SETUP ───────────────────────
st.set_page_config(page_title="🎧 Song Recommendations", page_icon="🎧", layout="wide")
st.title("🎧 Song Recommendations from Sampling Patterns")
st.sidebar.header("Recommendation Settings")

# ─────────────────────── CONNECT TO NEO4J ───────────────────────
@st.cache_resource
def get_conn():
    return Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")

conn = get_conn()

# ─────────────────────── CONNECT TO SPOTIFY ───────────────────────
@st.cache_resource
def get_spotify_client():
    client_id = st.secrets["SPOTIFY_CLIENT_ID"]
    client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(auth_manager=auth_manager)

sp = get_spotify_client()

# ─────────────────────── FUNCTION TO GET SPOTIFY POPULARITY ───────────────────────
@st.cache_data(show_spinner="Fetching Spotify popularity...")
def get_spotify_popularity(song_title, artist_name=None):
    try:
        query = f"track:{song_title}"
        if artist_name and artist_name != "Unknown":
            query += f" artist:{artist_name}"

        result = sp.search(q=query, type="track", limit=1)
        items = result.get("tracks", {}).get("items", [])
        if items:
            return items[0]["popularity"]
    except Exception as e:
        st.error(f"Spotify API error: {e}")
    
    return 0  # Default if not found

# ─────────────────────── GET ALL SONGS ───────────────────────
@st.cache_data
def get_all_songs():
    query = "MATCH (s:Song) RETURN DISTINCT s.title AS title ORDER BY s.title"
    return [r["title"] for r in conn.query(query) if r["title"]]

song_list = get_all_songs()
selected_song = st.selectbox("Select a song to base recommendations on", song_list)

if not selected_song:
    st.stop()

# ─────────────────────── GET SELECTED SONG POPULARITY ───────────────────────
selected_song_popularity = get_spotify_popularity(selected_song)

st.markdown(f"**Selected Song Spotify Popularity**: 🎵 **{selected_song_popularity}** / 100")


# ─────────────────────── GET RECOMMENDATIONS ───────────────────────
@st.cache_data(show_spinner="Fetching recommendations...")
def get_recommendations(title):
    query = """
    MATCH (s:Song {title: $title})-[:SAMPLES]->(sampled:Song)
    WITH sampled
    MATCH (rec:Song)-[:SAMPLES]->(sampled)
    WHERE rec.title <> $title
    OPTIONAL MATCH (rec)-[:HAS_ARTIST]->(a:Artist)
    OPTIONAL MATCH (sampled)-[:HAS_ARTIST]->(sampled_artist:Artist)
    RETURN rec.title AS recommended_title,
           collect(DISTINCT a.name) AS artists,
           sampled.title AS sampled_source,
           collect(DISTINCT sampled_artist.name) AS sampled_artists
    LIMIT 15
    """
    return conn.query(query, {"title": title})

# ─────────────────────── FETCH AND DISPLAY ───────────────────────
recs = get_recommendations(selected_song)
df = pd.DataFrame(recs)

if df.empty:
    st.warning("No recommendations found. This song may not have any sampling connections.")
else:
    df["artists"] = df["artists"].apply(lambda a: ", ".join(a) if a else "Unknown")
    df["sampled_artists"] = df["sampled_artists"].apply(lambda a: ", ".join(a) if a else "Unknown")

    # Fetch live Spotify popularity
    df["Spotify Popularity"] = df.apply(
        lambda row: get_spotify_popularity(row["recommended_title"], row["artists"].split(",")[0] if row["artists"] else None),
        axis=1
    )

    df = df.rename(columns={
        "recommended_title": "Recommended Song",
        "artists": "Artists",
        "sampled_source": "Shared Sample",
        "sampled_artists": "Shared Sample Artist(s)"
    })

    df = df.sort_values("Spotify Popularity", ascending=False)

    st.subheader(f"Songs that sampled the same tracks as **{selected_song}**")
    st.dataframe(df, use_container_width=True)

# ─────────────────────── OPTIONAL: SHOW SAMPLING GRAPH ───────────────────────
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
