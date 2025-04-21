import streamlit as st
import pandas as pd
from neo4j_utils import Neo4jConnection
import plotly.graph_objects as go

# ─────────────────────── PAGE SETUP ───────────────────────
st.set_page_config(page_title="Sampling Timeline", page_icon="📈", layout="wide")
st.title("📈 Genre-to-Genre Sampling Flow")
st.sidebar.header("Visualization Settings")

# ─────────────────────── NEO4J QUERY ───────────────────────
conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")

query = """
MATCH (original:Song)-[:BELONGS_TO_GENRE]->(g1:Genre)
MATCH (sampled:Song)-[:SAMPLES]->(original)
MATCH (sampled)-[:BELONGS_TO_GENRE]->(g2:Genre)
RETURN g1.name AS source_genre, g2.name AS target_genre, count(*) AS count
ORDER BY count DESC
"""
data = conn.query(query)
conn.close()

df = pd.DataFrame(data)

# ─────────────────────── EMPTY DATA CASE ───────────────────────
if df.empty:
    st.warning("No sampling data found.")
    st.stop()

# ─────────────────────── SIDEBAR FILTERS ───────────────────────
max_count = int(df["count"].max())
min_count = st.sidebar.slider("Minimum number of samples", 1, max_count, min(5, max_count))
df = df[df["count"] >= min_count]

top_n = st.sidebar.slider("Max number of flows to display", 5, 100, 25)
df = df.sort_values("count", ascending=False).head(top_n)

import plotly.graph_objects as go

# Group and filter
df_grouped = df.groupby(["source_genre", "target_genre"], as_index=False)["count"].sum()

# Clean base genres
df_grouped["source_genre"] = df_grouped["source_genre"].str.strip()
df_grouped["target_genre"] = df_grouped["target_genre"].str.strip()

# Add "(Original)" and "(Sampled)" clearly
df_grouped["source_label"] = df_grouped["source_genre"] + " (Original)"
df_grouped["target_label"] = df_grouped["target_genre"] + " (Sampled)"

# Get all unique labels
all_labels = pd.unique(df_grouped[["source_label", "target_label"]].values.ravel()).tolist()
label_to_index = {label: i for i, label in enumerate(all_labels)}

# Map to indexes
df_grouped["source_idx"] = df_grouped["source_label"].map(label_to_index)
df_grouped["target_idx"] = df_grouped["target_label"].map(label_to_index)


# Set positions: sources on the left, targets on the right
x_vals = []
y_vals = []
for i, label in enumerate(all_labels):
    if "(Original)" in label:
        x_vals.append(0.0)
    else:
        x_vals.append(1.0)
    y_vals.append(i / max(len(all_labels) - 1, 1))

# Build the figure
fig = go.Figure(data=[go.Sankey(
    arrangement="fixed",
    node=dict(
        pad=20,
        thickness=20,
        line=dict(color="blue", width=0.5),
        label=all_labels,
        color="#ffa600",
        x=x_vals,
        y=y_vals
    ),
    link=dict(
        source=df_grouped["source_idx"],
        target=df_grouped["target_idx"],
        value=df_grouped["count"],
        color="rgba(100, 100, 255, 0.3)",
    )
)])

# Calculate height dynamically: 30–40px per node + padding
nodes_per_column = max(
    df_grouped["source_label"].nunique(),
    df_grouped["target_label"].nunique()
)
dynamic_height = int(nodes_per_column * 40 + 100)

fig.update_layout(
    title_text="🎵 Genre-to-Genre Sampling Flow (True 2-Column Layout)",
    font=dict(size=16, family="Arial", color = 'blue'),
    height=dynamic_height,
)

fig.data[0].update(textfont=dict(color="black")) # Example

st.plotly_chart(fig, use_container_width=True)







