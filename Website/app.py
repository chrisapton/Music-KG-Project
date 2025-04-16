import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from neo4j_utils import Neo4jConnection

# Neo4j config
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "testpassword"

conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

st.title("🎶 Music Knowledge Graph Explorer")

# 🔍 Search input
col1, col2 = st.columns([1, 3])

with col1:
    node_type = st.selectbox("Type", ["Artist", "Song"], index=0, disabled=False, key="node_type")

with col2:
    search_query = st.text_input("Search for an artist or song")

if search_query:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(f"Results for: {search_query}")

    with col2:
        view_mode = st.radio(
            " ",  # Hide the label by using a space
            ["Visual", "Textual"],
            horizontal=True,
            label_visibility="collapsed"  # Optional: hides the label entirely
        )


    # Cypher query
    label = "Artist" if node_type == "Artist" else "Song"

    cypher_query = f"""
    MATCH (n:{label})-[r]-(m)
    WHERE toLower(n.name) CONTAINS toLower($query)
    RETURN id(n) AS n_id, labels(n) AS n_labels, n,
        id(m) AS m_id, labels(m) AS m_labels, m,
        type(r) AS rel_type
    LIMIT 50
    """

    results = conn.query(cypher_query, {"query": search_query})

    if view_mode == "Visual":
        # 🧠 Graph View
        net = Network(height="500px", width="100%", notebook=False)
        added_nodes = set()

        for record in results:
            n, m = record["n"], record["m"]
            n_id, m_id = record["n_id"], record["m_id"]
            n_labels, m_labels = record["n_labels"], record["m_labels"]
            r_type = record["rel_type"]

            for node, node_id, node_labels in [(n, n_id, n_labels), (m, m_id, m_labels)]:
                node_label = node_labels[0] if node_labels else "Node"
                node_name = node.get("name", node.get("title", "Unnamed"))

                if node_id not in added_nodes:
                    net.add_node(node_id, label=node_name, title=node_label)
                    added_nodes.add(node_id)

            net.add_edge(n_id, m_id, label=r_type)

        net.save_graph("graph.html")
        with open("graph.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=550, scrolling=True)

    else:
        # 📄 Textual View
        for record in results:
            for node, node_labels in [(record["n"], record["n_labels"]), (record["m"], record["m_labels"])]:
                node_label = node_labels[0] if node_labels else "Node"
                st.markdown(f"### {node_label}: {node.get('name', node.get('title', 'Unnamed'))}")
                for key, value in node.items():
                    st.write(f"**{key}**: {value}")
                st.markdown("---")

conn.close()

