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
    RETURN n, r, m
    LIMIT 50
    """
    results = conn.query(cypher_query, {"query": search_query})

    # Build Network graph
    net = Network(height="500px", width="100%", notebook=False)
    added_nodes = set()

    for record in results:
        n = record['n']
        m = record['m']
        r = record['r']

        for node in [n, m]:
            node_id = node.id
            node_label = list(node.labels)[0]
            node_name = node.get("name", "Unnamed")

            if node_id not in added_nodes:
                net.add_node(node_id, label=node_name, title=node_label)
                added_nodes.add(node_id)

        net.add_edge(n.id, m.id, label=r.type)

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
