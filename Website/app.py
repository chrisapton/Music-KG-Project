import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from neo4j_utils import Neo4jConnection

# Setup Neo4j connection

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "testpassword"  # from your docker-compose.yml

conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)  # Replace with your creds

st.title("🎶 Music Knowledge Graph Explorer")

# Search bar
search_query = st.text_input("Search for an artist or song", "")

# When user types a query
if search_query:
    st.subheader(f"Results for: {search_query}")

    # Query Neo4j for nodes and relationships
    cypher_query = """
    MATCH (n)-[r]-(m)
    WHERE toLower(n.name) CONTAINS toLower($query) OR toLower(m.name) CONTAINS toLower($query)
    RETURN id(n) AS n_id, labels(n) AS n_labels, n,
        id(m) AS m_id, labels(m) AS m_labels, m,
        type(r) AS rel_type
    LIMIT 50

    """
    results = conn.query(cypher_query, {"query": search_query})

    # Build Network graph
    net = Network(height="500px", width="100%", notebook=False)
    added_nodes = set()

    for record in results:
        n = record["n"]
        m = record["m"]
        n_id = record["n_id"]
        m_id = record["m_id"]
        n_labels = record["n_labels"]
        m_labels = record["m_labels"]
        rel_type = record["rel_type"]

        for node, node_id, node_labels in [(n, n_id, n_labels), (m, m_id, m_labels)]:
            node_label = node_labels[0] if node_labels else "Node"
            node_name = node.get("name", node.get("title", "Unnamed"))

            if node_id not in added_nodes:
                net.add_node(node_id, label=node_name, title=node_label)
                added_nodes.add(node_id)

        net.add_edge(n_id, m_id, label=rel_type)


    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "centralGravity": 0.3,
          "springLength": 95
        },
        "minVelocity": 0.75
      }
    }
    """)

    net.save_graph("graph.html")

    # Display in Streamlit
    HtmlFile = open("graph.html", "r", encoding="utf-8")
    components.html(HtmlFile.read(), height=550, scrolling=True)

# Cleanup
conn.close()
