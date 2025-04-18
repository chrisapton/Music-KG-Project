import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from neo4j_utils import Neo4jConnection

st.set_page_config(page_title="Search & Explore", page_icon="🔎")
st.markdown("# 🔍 Search & Explore")
st.sidebar.header("Search & Explore")

# Neo4j config
conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")

# ▶︎ Search UI
col1, col2 = st.columns([1, 3])
with col1:
    node_type = st.selectbox("Type", ["Artist", "Song"])
with col2:
    q = st.text_input("Search for an artist or song")

if q:
    view = st.radio("", ["Visual", "Textual"], horizontal=True, label_visibility="collapsed")
    label = "Artist" if node_type == "Artist" else "Song"
    cypher = f"""
      MATCH (n:{label})-[r]-(m)
      WHERE toLower(n.name) CONTAINS toLower($q)
      RETURN id(n) AS n_id, labels(n) AS n_labels, n,
             id(m) AS m_id, labels(m) AS m_labels, m,
             type(r) AS rel_type
      LIMIT 50
    """
    results = conn.query(cypher, {"q": q})

    if view == "Visual":
        net = Network(height="500px", width="100%", notebook=False)
        seen = set()
        for rec in results:
            for node, nid, labs in [(rec["n"], rec["n_id"], rec["n_labels"]),
                                    (rec["m"], rec["m_id"], rec["m_labels"])]:
                name = node.get("name", node.get("title", "Unnamed"))
                if nid not in seen:
                    net.add_node(nid, label=name, title=(labs[0] if labs else ""))
                    seen.add(nid)
            net.add_edge(rec["n_id"], rec["m_id"], label=rec["rel_type"])
        net.save_graph("graph.html")
        with open("graph.html") as f:
            components.html(f.read(), height=550, scrolling=True)
    else:
        for rec in results:
            for node, labs in [(rec["n"], rec["n_labels"]), (rec["m"], rec["m_labels"])]:
                lbl = labs[0] if labs else "Node"
                st.markdown(f"### {lbl}: {node.get('name','Unnamed')}")
                for k, v in node.items():
                    st.write(f"**{k}**: {v}")
                st.markdown("---")

conn.close()
