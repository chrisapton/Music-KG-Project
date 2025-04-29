import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from neo4j_utils import Neo4jConnection
import networkx as nx
import streamlit.components.v1 as components
from pyvis.network import Network

st.set_page_config(page_title="🎧 Song Recommendations", page_icon="🎧", layout="wide")
st.title("🎧 Song Recommendations from Sampling Patterns")


# Neo4j connection
@st.cache_resource
def get_conn():
    return Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")


conn = get_conn()


# Spotify client setup
@st.cache_resource
def get_spotify_client():
    client_id = st.secrets["SPOTIFY_CLIENT_ID"]
    client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(auth_manager=auth_manager)


sp = get_spotify_client()


# Get Spotify popularity for a song
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


# Search for songs
@st.cache_data(show_spinner="Searching songs...")
def search_songs(query):
    results = conn.query("""
        MATCH (s:Song)
        OPTIONAL MATCH (s)-[:HAS_ARTIST]->(a:Artist)
        WITH s, collect(DISTINCT a.name) AS artists
        WHERE toLower(s.title) CONTAINS toLower($q)
           OR (size(artists) > 0 AND any(name IN artists WHERE toLower(name) CONTAINS toLower($q)))
        MATCH (s)-[:RELEASED_IN]->(y:Year)
        RETURN id(s) AS id,
               s.title AS title,
               artists AS artist,
               coalesce(y.value, s.release_year) AS year
        ORDER BY year DESC
        LIMIT 20
    """, {"q": query})
    return results


# Search input
song_query = st.text_input("Search for a song (title or artist):")

if not song_query:
    st.stop()

matches = search_songs(song_query)

if not matches:
    st.warning("No songs found matching your search.")
    st.stop()


df_matches = pd.DataFrame(matches)
artist_str = lambda a: ", ".join(a) if isinstance(a, (list, tuple)) else str(a)

options = {
    f"{r.title} – {artist_str(r.artist)} ({r.year})": r
    for r in df_matches.itertuples()
}

selected_choice = st.selectbox("Select a song:", list(options.keys()))
if not selected_choice:
    st.stop()

selected_row = options[selected_choice]
selected_song = selected_row.title
selected_song_id = selected_row.id


# Get Spotify popularity for the selected song
artist_name = ", ".join(selected_row.artist) if isinstance(selected_row.artist, (list, tuple)) else selected_row.artist
selected_song_popularity = get_spotify_popularity(selected_song, artist_name)

st.markdown(f"**Selected Song Spotify Popularity**: 🎵 **{selected_song_popularity}** / 100")


# Get recommendations based on sampling
@st.cache_data(show_spinner="Fetching recommendations...")
def get_recommendations(title, artist_names):
    query = """
    MATCH (s:Song)
    OPTIONAL MATCH (s)-[:HAS_ARTIST]->(a:Artist)
    WITH s, collect(DISTINCT a.name) AS artists
    WHERE toLower(s.title) = toLower($title)
      AND any(name IN artists WHERE toLower(name) IN $artist_names)
    
    MATCH (s)-[:SAMPLES]->(sampled:Song)
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
    return conn.query(query, {
        "title": title,
        "artist_names": [name.lower() for name in artist_names] if artist_names else []
    })


# Display recommendations
recs = get_recommendations(selected_song, selected_row.artist)
df = pd.DataFrame(recs)

if df.empty:
    st.warning("No recommendations found. This song may not have any sampling connections.")
else:
    # Keep Artists and Sampled Artists as lists
    df["artists"] = df["artists"].apply(lambda a: a if isinstance(a, list) else [])
    df["sampled_artists"] = df["sampled_artists"].apply(lambda a: a if isinstance(a, list) else [])

    # Fetch live Spotify popularity
    df["Spotify Popularity"] = df.apply(
        lambda row: get_spotify_popularity(row["recommended_title"], row["artists"][0] if row["artists"] else None),
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

    st.data_editor(
        df[["Recommended Song", "Artists", "Shared Sample", "Shared Sample Artist(s)", "Spotify Popularity"]],
        column_config={
            "Artists": st.column_config.ListColumn("Artists"),
            "Shared Sample Artist(s)": st.column_config.ListColumn("Shared Sample Artist(s)")
        },
        use_container_width=True,
        disabled=True
    )


with st.expander("Show sampling graph (co-samplers)"):
    G = nx.DiGraph()

    # Add the selected song node
    selected_song_label = f"{selected_song} – {artist_str(selected_row.artist)}"
    G.add_node(selected_song_label, color="blue")

    for row in recs:
        recommended_label = f"{row['recommended_title']} – {', '.join(row['artists']) if isinstance(row['artists'], list) else row['artists']}"
        sampled_label = f"{row['sampled_source']} – {', '.join(row['sampled_artists']) if isinstance(row['sampled_artists'], list) else row['sampled_artists']}"

        G.add_node(recommended_label, color="orange")
        G.add_node(sampled_label, color="gray")

        G.add_edge(selected_song_label, sampled_label)
        G.add_edge(recommended_label, sampled_label)

    nt = Network(height="690px", width="100%", directed=True)
    nt.from_nx(G)
    nt.set_options("""var options={ "physics":{ "solver":"forceAtlas2Based" } }""")
    html = nt.generate_html()
    components.html(html, height=700)