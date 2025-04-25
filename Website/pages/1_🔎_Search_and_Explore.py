import streamlit as st
import pandas as pd
import altair as alt
from pyvis.network import Network
# from ipysigma import Sigma
import networkx as nx
import streamlit.components.v1 as components
from neo4j_utils import Neo4jConnection

# Neo4j connection
conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")

st.set_page_config(page_title="Search & Explore", page_icon="🔍", layout="wide")

# ─────────────────────── sidebar ───────────────────────
st.sidebar.header("Search Mode")
sidebar_search_type = st.sidebar.selectbox("Search Type", ["Artist", "Song"])

# ─────────────────────── main page ─────────────────────
st.markdown("# 🔍 Search & Explore")

# Read query params from URL
params = st.query_params
url_search_type = params.get("search_type", sidebar_search_type)
query = params.get("query", "")
artist_filter = params.get("artist_filter", "")
if "submitted" not in st.session_state:
    st.session_state.submitted = query != ""

with st.form("search_form"):
    if url_search_type == "Artist":
        query = st.text_input("Artist name", value=query)
        artist_filter = None
    else:
        query = st.text_input("Song title", value=query)
        artist_filter = st.text_input("Filter by artist (optional)", value=artist_filter)

    clicked_submit = st.form_submit_button("Search")
    if clicked_submit:
        st.session_state.submitted = True
        st.session_state.query = query
        st.session_state.artist_filter = artist_filter


if st.session_state.submitted:
    if not query:
        st.error("Please enter a search query.")
        conn.close()
        st.stop()

    # --- Artist Search -------------------------------------------------------
    if url_search_type == "Artist":
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
            OPTIONAL MATCH (a)<-[:HAS_ARTIST]-(s:Song)
            WHERE s IS NOT NULL
            OPTIONAL MATCH (s)-[r:SAMPLES]->(t:Song)

            OPTIONAL MATCH (s)-[:HAS_ARTIST]->(sa:Artist)
            OPTIONAL MATCH (s)-[:BELONGS_TO_GENRE]->(sg:Genre)
            OPTIONAL MATCH (s)-[:RELEASED_IN]->(sy:Year)

            OPTIONAL MATCH (t)-[:HAS_ARTIST]->(ta:Artist)
            OPTIONAL MATCH (t)-[:BELONGS_TO_GENRE]->(tg:Genre)
            OPTIONAL MATCH (t)-[:RELEASED_IN]->(ty:Year)

            RETURN 
                id(a) AS a_id, a.name AS a_name,
                id(s) AS s_id, s.title AS s_name,
                id(t) AS t_id, t.title AS t_name,
                type(r) AS rel_type,
                collect(DISTINCT sa.name) AS song_artists,
                s.release_date AS s_release_date,
                sy.value AS s_year,
                collect(DISTINCT sg.name) AS s_genres,
                collect(DISTINCT ta.name) AS t_artists,
                t.release_date AS t_release_date,
                ty.value AS t_year,
                collect(DISTINCT tg.name) AS t_genres
            LIMIT 200
            """,
            {"artist": artist}
        )

        G = nx.DiGraph()

        # Helpers
        def fmt_list(lst, limit=None):
            if not lst:
                return 'N/A'
            if limit:
                lst = lst[:limit]
            return ', '.join(str(x) for x in lst)
        
        def format_release(date_val, year_val):
            if date_val == None or date_val == "None":
                return str(year_val)
            else:
                return str(date_val)

        def safe_title(value):
            return value if value else "Untitled"

        # Add nodes and edges
        for rec in records:
            a_id = str(rec["a_id"])
            a_name = safe_title(rec["a_name"])
            s_id = str(rec["s_id"]) if rec["s_id"] is not None else None
            t_id = str(rec["t_id"]) if rec["t_id"] is not None else None

            # Artist node
            if not G.has_node(a_id):
                G.add_node(a_id, label=a_name, color="blue", type="Artist")

            # Song performed by artist
            if s_id is not None:
                if not G.has_node(s_id):
                    G.add_node(
                        s_id,
                        label=safe_title(rec["s_name"]),
                        color="green",
                        type="Song",
                        title=f"""Song: {safe_title(rec["s_name"])}
                                Artist(s): {fmt_list(rec.get("song_artists"))}
                                Release Date: {format_release(rec.get("s_release_date"), rec.get("s_year"))}
                                Genres: {fmt_list(rec.get("s_genres"), 3)}"""
                    )
                G.add_edge(s_id, a_id, color="blue")

            # Songs sampled by this song
            if t_id is not None:
                if not G.has_node(t_id):
                    G.add_node(
                        t_id,
                        label=safe_title(rec["t_name"]),
                        color="orange",
                        type="Song",
                        title=f"""Sampled Song: {safe_title(rec["t_name"])}
                                Artist(s): {fmt_list(rec.get("t_artists"))}
                                Release Date: {format_release(rec.get("t_release_date"), rec.get("t_year"))}
                                Genres: {fmt_list(rec.get("t_genres"), 3)}"""
                    )
                G.add_edge(s_id, t_id, label=rec["rel_type"])

        nt = Network(height="700px", width="100%", directed=True)
        nt.from_nx(G)
        nt.set_options("""var options={ "physics":{ "solver":"forceAtlas2Based" } }""")
        html = nt.generate_html()
        components.html(html, height=700, scrolling=True)

    else:
        # --- Song Search -------------------------------------------------------
        title = query
        # Basic song info
        try:
            if artist_filter in ("None", ""):
                artist_filter = None

            info = conn.query(
                """
                MATCH (s:Song {title:$title})
                OPTIONAL MATCH (s)-[:HAS_ARTIST]->(a:Artist)
                OPTIONAL MATCH (s)-[:BELONGS_TO_GENRE]->(g:Genre)
                OPTIONAL MATCH (s)-[:PART_OF_ALBUM]->(al:Album)
                OPTIONAL MATCH (s)-[:RELEASED_IN]->(y:Year)
                WITH s, al, collect(DISTINCT a.name) AS artists, collect(DISTINCT g.name) AS genres,
                    s.record_label AS label, s.release_date AS rd, y.value AS year
                WHERE $artist_filter IS NULL OR $artist_filter IN artists
                RETURN rd, year, al.title AS album, label, artists, genres, s.id AS song_id
                """,
                {"title": title, "artist_filter": artist_filter}
            )[0]
        except (IndexError, KeyError):
            st.error(f"Song '{title}' not found.")
            conn.close()
            st.stop()

        def format_release(date_val, year_val):
            if date_val is None or date_val == "None":
                return str(year_val) if year_val else "N/A"
            return str(date_val)

        rd = format_release(info.get("rd"), info.get("year"))
        album = info.get('album', 'N/A')
        label = info.get('label', 'N/A')
        artists = info.get('artists', [])
        genres = info.get('genres', [])
        song_id = info.get('song_id', None)

        st.markdown(f"**Song:** {title}")
        st.markdown(f"**Artist(s):** {', '.join(artists)}")
        st.markdown(f"**Album:** {album}")
        st.markdown(f"**Release Date:** {rd}")
        st.markdown(f"**Genres:** {', '.join(genres)}")
        st.markdown(f"**Record Label:** {label}")

        # Sampling stats
        outgoing = conn.query(
            """
            MATCH (s:Song {id:$song_id})-[r:SAMPLES]->()
            RETURN count(r) AS cnt
            """,
            {"song_id": song_id}
        )[0]['cnt']
        incoming = conn.query(
            """
            MATCH ()-[r:SAMPLES]->(s:Song {id:$song_id})
            RETURN count(r) AS cnt
            """,
            {"song_id": song_id}
        )[0]['cnt']
        chains = conn.query(
            """
            MATCH path=(o:Song)-[:SAMPLES*2]-(s:Song {id:$song_id})
            RETURN count(DISTINCT o) AS cnt
            """,
            {"song_id": song_id}
        )[0]['cnt']
        pagerank_score = conn.query(
            """
            MATCH (s:Song {id:$song_id})
            RETURN s.pagerank AS pr
            """,
            {"song_id": song_id}
        )[0]["pr"]
        pagerank_score = round(pagerank_score, 5) if pagerank_score is not None else "N/A"

        st.markdown("**🧬 Sampling Stats:**")
        st.write(f"- Sampled {outgoing} other songs")
        st.write(f"- Sampled by {incoming} songs")
        st.write(f"- Appears in {chains} sample chains")
        st.write(f"- PageRank Score: {pagerank_score}")


        # Songs This Track Sampled
        sampled = conn.query(
            """
            MATCH (s:Song {id:$song_id})-[:SAMPLES]->(t:Song)
            OPTIONAL MATCH (t)-[:HAS_ARTIST]->(a:Artist)
            WITH t, collect(DISTINCT a.name) AS artist_list
            RETURN
                t.title AS name,
                apoc.text.join(artist_list, ', ') AS artists,
                t.release_date AS rd
            ORDER BY rd DESC
            """,
            {"song_id": song_id}
        )
        st.markdown("**🎧 Songs This Track Sampled:**")
        with st.expander("See Songs Sampled by This Track"):
            for rec in sampled:
                st.write(f"- “{rec['name']}” by {rec['artists']} ({rec['rd']})")

        # Songs That Sampled This Track
        samp_by = conn.query(
            """
            MATCH (o:Song)-[r:SAMPLES]->(s:Song {id:$song_id})
            OPTIONAL MATCH (o)-[:HAS_ARTIST]->(a:Artist)
            WITH o, collect(DISTINCT a.name) AS artist_list
            RETURN
                o.title AS name,
                apoc.text.join(artist_list, ', ') AS artists,
                o.release_date AS rd
            ORDER BY rd DESC
            """,
            {"song_id": song_id}
        )
        st.markdown("**🔁 Songs That Sampled This Track:**")
        with st.expander("See Songs That Sampled This Track"):
            for rec in samp_by:
                st.write(f"- “{rec['name']}” by {rec['artists']} ({rec['rd']})")

        # Sample Usage Over Time
        df_time = pd.DataFrame(conn.query(
            """
            MATCH (o:Song)-[:SAMPLES]->(s:Song {id:$song_id})
            MATCH (o)-[:RELEASED_IN]->(y:Year)
            WITH y.value            AS year,
                 collect(o.title)   AS songs,          // list for the tooltip
                 count(*)           AS n               // total samples that year
            RETURN year, n, songs
            ORDER BY year
            """,
            {"song_id": song_id}
        ))
        st.markdown("**📈 Sample Usage Over Time:**")
        if df_time.empty:
            st.info("No sampling events.")
        else:
            df_time["songs_tooltip"] = df_time["songs"].apply(
                lambda lst: ", ".join(lst[:10]) + ("… (+%d more)" % (len(lst) - 15) if len(lst) > 15 else "")
            )

            bar = (
                alt.Chart(df_time)
                .mark_bar(color="#1f77b4")
                .encode(
                    x=alt.X("year:O", title="Year"),
                    y=alt.Y("n:Q", title="# of samples"),
                    tooltip=[
                        alt.Tooltip("year:O", title="Year"),
                        alt.Tooltip("n:Q", title="Samples"),
                        alt.Tooltip("songs_tooltip:N", title="Songs that sampled")
                    ]
                )
                .properties(width=700, height=350)
            )

            st.altair_chart(bar, use_container_width=True)


        if "depth" not in st.session_state:
            st.session_state.depth = 1

        depth = st.slider(
            "Sampling Depth",
            min_value=1,
            max_value=4,
            value=st.session_state.depth,
            key="depth_slider"
        )

        # Query recursive sample relationships up to selected depth

        artist_filter = " OR ".join([f'"{artist}" IN matched_artists' for artist in artists]) if artists else ""

        results = conn.query(
            f"""
            MATCH (s:Song {{title:$title}})
            OPTIONAL MATCH (s)-[:HAS_ARTIST]->(a:Artist)
            WITH s, collect(DISTINCT a.name) AS matched_artists
            WHERE {"TRUE" if not artists else artist_filter}

            CALL {{
                WITH s
                MATCH path = (s)-[:SAMPLES*1..{depth}]-(n)
                RETURN DISTINCT relationships(path) AS rels
            }}
            UNWIND rels AS r
            WITH DISTINCT r,
                startNode(r) AS src,
                endNode(r) AS tgt
            OPTIONAL MATCH (src)-[:HAS_ARTIST]->(a1:Artist)
            OPTIONAL MATCH (tgt)-[:HAS_ARTIST]->(a2:Artist)
            RETURN 
                id(src) AS src_id,
                src.title AS src_title,
                collect(DISTINCT a1.name) AS src_artists,
                id(tgt) AS tgt_id,
                tgt.title AS tgt_title,
                collect(DISTINCT a2.name) AS tgt_artists,
                type(r) AS rel_type
            """,
            {"title": title}
        )



        # STEP 1: Build graph for BFS
        G = nx.DiGraph()
        for rec in results:
            G.add_edge(rec["src_id"], rec["tgt_id"])

        # Find the root node (starting title)
        title_clean = title.strip().lower()
        root_id = None

        for rec in results:
            if rec["src_title"] and rec["src_title"].strip().lower() == title_clean:
                root_id = rec["src_id"]
                break
            elif rec["tgt_title"] and rec["tgt_title"].strip().lower() == title_clean:
                root_id = rec["tgt_id"]
                break


        # STEP 2: Compute node depths using BFS
        depths = {node: float("inf") for node in G.nodes}
        if root_id is not None:
            depths[root_id] = 0
            queue = [root_id]
            while queue:
                current = queue.pop(0)
                for neighbor in list(G.successors(current)) + list(G.predecessors(current)):
                    if depths[neighbor] > depths[current] + 1:
                        depths[neighbor] = depths[current] + 1
                        queue.append(neighbor)


        # STEP 3: Color function
        import math

        def get_color_by_depth(depth):
            colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#9467bd"]
            if depth is None or math.isinf(depth):
                return "#808080"  # Gray for unreachable nodes
            return colors[int(depth) % len(colors)]


        # STEP 4: Create pyvis network
        from pyvis.network import Network

        net = Network(height="550px", width="100%", notebook=False, directed=True)
        added_nodes = set()
        added_edges = set()

        for rec in results:
            src_id = rec["src_id"]
            tgt_id = rec["tgt_id"]
            src_title = rec["src_title"]
            tgt_title = rec["tgt_title"]
            src_artists = ", ".join(rec["src_artists"]) if rec["src_artists"] else "Unknown"
            tgt_artists = ", ".join(rec["tgt_artists"]) if rec["tgt_artists"] else "Unknown"
            rel_type = rec["rel_type"]

            for nid, title_val, artist_str in [
                (src_id, src_title, src_artists),
                (tgt_id, tgt_title, tgt_artists)
            ]:
                if nid not in added_nodes:
                    depth = depths.get(nid, 0)
                    color = "blue" if title_val == title else get_color_by_depth(depth)
                    tooltip = f"Song: {title_val}\nArtist(s): {artist_str}\nDepth: {depth}"
                    net.add_node(nid, label=title_val, color=color, title=tooltip)
                    added_nodes.add(nid)

            edge_key = (src_id, tgt_id)
            if rel_type == "SAMPLES" and edge_key not in added_edges:
                net.add_edge(
                    src_id,
                    tgt_id,
                    arrows="to",
                    color="black",
                    width=2,
                    smooth=True
                )
                added_edges.add(edge_key)

        # Display
        net.save_graph("song_graph.html")
        with open("song_graph.html", "r") as f:
            components.html(f.read(), height=550, scrolling=True)

conn.close()
