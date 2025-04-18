import streamlit as st
import pandas as pd
import altair as alt
from pyvis.network import Network
# from ipysigma import Sigma
import networkx as nx
import streamlit.components.v1 as components
from neo4j_utils import Neo4jConnection

st.set_page_config(page_title="Search & Explore", page_icon="🔍", layout="wide")
st.markdown("# 🔍 Search & Explore")
st.sidebar.header("Search & Explore")

# Sidebar controls
search_type = st.sidebar.selectbox("Search Type", ["Artist", "Song"])
query = st.text_input(f"Enter {search_type} name or title")

# Neo4j connection
conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")

if query:
    ### ARTIST SEARCH ###
    if search_type == "Artist":
        artist = query
        try:
            artist_info = conn.query(
                """
                MATCH (a:Artist {name:$artist})
                RETURN a.wikipedia_summary AS summary
                """,
                {"artist": artist}
            )[0]
        except (IndexError, KeyError):
            st.error(f"Artist '{artist}' not found.")
            conn.close()
            st.stop()

        # Header
        st.markdown(f"## Artist: {artist}")

        col1, col2 = st.columns(2)
        with col1:
            summary = artist_info.get("summary", "No wiki summary available.")

            # Fetch top 3 genres based on artist's songs
            top_genres = conn.query(
                """
                MATCH (a:Artist {name:$artist})<-[:HAS_ARTIST]-(s:Song)-[:BELONGS_TO_GENRE]->(g:Genre)
                RETURN g.name AS genre, count(*) AS cnt
                ORDER BY cnt DESC LIMIT 3
                """,
                {"artist": artist}
            )

            st.markdown(f'### Basic Info for {artist}')
            # Top Genres
            st.markdown("**Genres:**")
            if top_genres:
                for rec in top_genres:
                    st.write(f"- {rec['genre']}")
            else:
                st.write("- N/A")

            st.markdown(f"**Wikipedia Summary:**")
            with st.expander("See Wikipedia Summary"):
                st.markdown(summary)

            # Song List
            sl = conn.query(
                """
                MATCH (a:Artist {name:$artist})<-[:HAS_ARTIST]-(s:Song)-[:RELEASED_IN]->(y:Year)
                RETURN s.title AS name, id(s) AS id, y.value AS year
                """,
                {"artist": artist}
            )
            st.markdown("**Song List:**")
            with st.expander("See Songs by Artist"):
                for rec in sl:
                    st.write(f"• {rec['name']} (ID: {rec['id']}, Release Year: {rec['year']})")

        with col2:
            # Sampling Stats
            sampled_by = conn.query(
                """
                MATCH (other:Song)-[:SAMPLES]->(:Song)-[:HAS_ARTIST]->(a:Artist {name:$artist})
                RETURN count(DISTINCT other) AS cnt
                """,
                {"artist": artist}
            )[0]["cnt"]
            sampled = conn.query(
                """
                MATCH (a:Artist {name:$artist})<-[:HAS_ARTIST]-(:Song)-[r:SAMPLES]->()
                RETURN count(r) AS cnt
                """,
                {"artist": artist}
            )[0]["cnt"]


            # Display Sampling Stats
            st.markdown("### Sampling Stats")
            st.write("**Number of songs sampled:**")
            st.write(f"- Songs sampled by *{artist}*: **{sampled_by}**")
            st.write(f"- Songs {artist} sampled: **{sampled}**")

            # Most Sampled Songs
            ms = conn.query(
                """
                MATCH (a:Artist {name:$artist})<-[:HAS_ARTIST]-(s:Song)-[r:SAMPLES]->()
                RETURN s.title AS song, count(r) AS cnt
                ORDER BY cnt DESC LIMIT 3
                """,
                {"artist": artist}
            )
            st.markdown("**Top Sampling Songs:**")
            for rec in ms:
                st.write(f"- “{rec['song']}” ({rec['cnt']} samples)")

            # Genres Sampled
            gs = pd.DataFrame(conn.query(
                """
                MATCH (a:Artist {name:$artist})<-[:HAS_ARTIST]-(s:Song)-[:SAMPLES]->(t:Song)-[:BELONGS_TO_GENRE]->(g:Genre)
                RETURN g.name AS genre, count(*) AS cnt
                ORDER BY cnt DESC LIMIT 3
                """,
                {"artist": artist}
            ))
            st.markdown("**Genres Sampled:**")
            if not gs.empty:
                total = gs["cnt"].sum()
                gs["pct"] = (gs["cnt"]/total*100).round(1)
                for _, row in gs.iterrows():
                    st.write(f"- {row['genre']} ({row['pct']}%)")
            else:
                st.write("- N/A")

            # Genres That Sample
            gts = pd.DataFrame(conn.query(
                """
                MATCH (t:Song)-[:BELONGS_TO_GENRE]->(g:Genre),
                      (t)-[:SAMPLES]->(:Song)-[:HAS_ARTIST]->(a:Artist {name:$artist})
                RETURN g.name AS genre, count(*) AS cnt
                ORDER BY cnt DESC LIMIT 3
                """,
                {"artist": artist}
            ))
            st.markdown(f"**Genres That Sample {artist}:**")
            if not gts.empty:
                total2 = gts["cnt"].sum()
                gts["pct"] = (gts["cnt"]/total2*100).round(1)
                for _, row in gts.iterrows():
                    st.write(f"- {row['genre']} ({row['pct']}%)")
            else:
                st.write("- N/A")

        # Build NetworkX graph for song
        st.markdown("### Artist-Song Sampling Network")
        records = conn.query(
            """
            MATCH (a:Artist {name:$artist})
            OPTIONAL MATCH (a)<-[p:HAS_ARTIST]-(s:Song)
            OPTIONAL MATCH (s)-[r:SAMPLES]->(t:Song)
            RETURN id(a) AS a_id, a.name AS a_name,
                   id(s) AS s_id, s.title AS s_name,
                   id(t) AS t_id, t.title AS t_name,
                   type(r) AS rel_type
            LIMIT 200
            """,
            {"artist": artist}
        )
        G = nx.DiGraph()
        # Add nodes and edges
        for rec in records:
            a_id = str(rec['a_id'])
            a_name = str(rec['a_name'])
            s_id = str(rec['s_id']) if rec['s_id'] is not None else None
            t_id = str(rec['t_id']) if rec['t_id'] is not None else None

            # Artist node
            if not G.has_node(a_id):
                G.add_node(a_id, label=a_name, color='blue', type='Artist')
            # Song performed by artist
            if s_id is not None:
                if not G.has_node(s_id):
                    G.add_node(s_id, label=rec['s_name'], color='green', type='Song')
                G.add_edge(s_id, a_id, color='blue')
            # Songs sampled by this song
            if t_id is not None:
                if not G.has_node(t_id):
                    G.add_node(t_id, label=rec['t_name'], color='orange', type='Song')
                G.add_edge(s_id, t_id, label=rec['rel_type'])

        nt = Network(height="700px", width="100%", directed=True)
        nt.from_nx(G)
        nt.set_options("""var options={ "physics":{ "solver":"forceAtlas2Based" } }""")
        html = nt.generate_html()

        components.html(html, height=700, scrolling=True)

    else:
        title = query
        # Basic song info
        info = conn.query(
            """
            MATCH (s:Song {title:$title})
            OPTIONAL MATCH (s)<-[:PERFORMS]-(a:Artist)
            OPTIONAL MATCH (s)-[:HAS_GENRE]->(g:Genre)
            RETURN s.release_date AS rd,
                   s.label AS label,
                   s.wiki_summary AS summary,
                   collect(DISTINCT a.name) AS artists,
                   collect(DISTINCT g.name) AS genres,
                   avg(a.popularity) AS artist_popularity,
                   id(s) AS song_id
            """,
            {"title": title}
        )[0]
        rd = info.get('rd', 'N/A')
        label = info.get('label', 'N/A')
        summary = info.get('summary', 'No summary.')
        artists = info.get('artists', [])
        genres = info.get('genres', [])
        pop = round(info.get('artist_popularity', 0), 1) if info.get('artist_popularity') else 'N/A'

        st.markdown(f"**Song:** {title}")
        st.markdown(f"**Artist(s):** {', '.join(artists)}")
        st.markdown(f"**Release Date:** {rd}")
        st.markdown(f"**Genres:** {', '.join(genres)}")
        st.markdown(f"**Label:** {label}")
        st.markdown(f"**Wikipedia Summary:** {summary}")
        st.markdown(f"**Artist Popularity:** {pop}")

        # Sampling stats
        outgoing = conn.query(
            """
            MATCH (s:Song {title:$title})-[r:SAMPLES]->()
            RETURN count(r) AS cnt
            """,
            {"title": title}
        )[0]['cnt']
        incoming = conn.query(
            """
            MATCH ()-[r:SAMPLES]->(s:Song {title:$title})
            RETURN count(r) AS cnt
            """,
            {"title": title}
        )[0]['cnt']
        chains = conn.query(
            """
            MATCH path=(o:Song)-[:SAMPLES*2]-(s:Song {title:$title})
            RETURN count(DISTINCT o) AS cnt
            """,
            {"title": title}
        )[0]['cnt']
        st.markdown("**🧬 Sampling Stats:**")
        st.write(f"- Sampled {outgoing} other songs")
        st.write(f"- Sampled by {incoming} songs")
        st.write(f"- Appears in {chains} sample chains")

        # Songs This Track Sampled
        sampled = conn.query(
            """
            MATCH (s:Song {title:$title})-[r:SAMPLES]->(t:Song)
            OPTIONAL MATCH (t)<-[:PERFORMS]-(a:Artist)
            RETURN t.title AS name, a.name AS artist, t.release_date AS rd
            ORDER BY rd
            """,
            {"title": title}
        )
        st.markdown("**🎧 Songs This Track Sampled:**")
        for rec in sampled:
            st.write(f"- “{rec['name']}” by {rec['artist']} ({rec['rd']})")

        # Songs That Sampled This Track
        samp_by = conn.query(
            """
            MATCH (o:Song)-[r:SAMPLES]->(s:Song {title:$title})
            OPTIONAL MATCH (o)<-[:PERFORMS]-(a:Artist)
            RETURN o.title AS name, a.name AS artist, o.release_date AS rd
            ORDER BY rd DESC
            """,
            {"title": title}
        )
        st.markdown("**🔁 Songs That Sampled This Track:**")
        for rec in samp_by:
            st.write(f"- “{rec['name']}” by {rec['artist']} ({rec['rd']})")

        # Sample Usage Over Time
        df_time = pd.DataFrame(conn.query(
            """
            MATCH ()-[r:SAMPLES]->(s:Song {title:$title})
            RETURN r.timestamp AS ts
            """,
            {"title": title}
        ))
        st.markdown("**📈 Sample Usage Over Time:**")
        if not df_time.empty:
            df_time["year"] = pd.to_datetime(df_time["ts"]).dt.year
            df_count = df_time["year"].value_counts().sort_index().reset_index()
            df_count.columns = ["year","count"]
            chart = alt.Chart(df_count).mark_line().encode(
                x="year:O", y="count:Q", tooltip=["year","count"]
            ).properties(width=700, height=300)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No sampling events.")

        # Graph Visualization
        results = conn.query(
            """
            MATCH (s:Song {title:$title})-[r]-(m)
            RETURN id(s) AS n_id, labels(s) AS n_labels, s,
                   id(m) AS m_id, labels(m) AS m_labels, m,
                   type(r) AS rel_type
            LIMIT 50
            """,
            {"title": title}
        )
        net = Network(height="500px", width="100%", notebook=False)
        added = set()
        for rec in results:
            nid = rec['n_id']; labs = rec['n_labels']
            label = rec['s'].get('name', rec['s'].get('title', ''))
            if nid not in added:
                net.add_node(nid, label=label, title=(labs[0] if labs else ''))
                added.add(nid)
            mid = rec['m_id']; mlabs = rec['m_labels']
            mlabel = rec['m'].get('name', rec['m'].get('title',''))
            if mid not in added:
                net.add_node(mid, label=mlabel, title=(mlabs[0] if mlabs else ''))
                added.add(mid)
            net.add_edge(nid, mid, label=rec['rel_type'])
        net.save_graph("song_graph.html")
        with open("song_graph.html","r") as f:
            components.html(f.read(), height=550, scrolling=True)

conn.close()
