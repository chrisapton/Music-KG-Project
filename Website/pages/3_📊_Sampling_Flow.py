import streamlit as st
import pandas as pd
from neo4j_utils import Neo4jConnection
import plotly.graph_objects as go
import plotly.express as px

# ─────────────────────── PAGE SETUP ───────────────────────
st.set_page_config(page_title="Sampling Flow", page_icon="📊", layout="wide")
st.title("📊 Genre-to-Genre Sampling Flow")
st.sidebar.header("Visualization Settings")

# ─────────────────────── CACHED CONNECTION ───────────────────────
@st.cache_resource
def get_conn():
    return Neo4jConnection("bolt://localhost:7687", "neo4j", "testpassword")

# ─────────────────────── CACHED DATA ───────────────────────
@st.cache_data
def load_sampling_data():
    query = """
    MATCH (original:Song)-[:BELONGS_TO_GENRE]->(g1:Genre)
    MATCH (sampled:Song)-[:SAMPLES]->(original)
    MATCH (sampled)-[:BELONGS_TO_GENRE]->(g2:Genre)
    RETURN g1.name AS source_genre, g2.name AS target_genre, count(*) AS count
    ORDER BY count DESC
    """
    return get_conn().query(query)


conn = get_conn()
data = load_sampling_data()

df = pd.DataFrame(data)
if df.empty:
    st.warning("No sampling data found.")
    st.stop()

top_n = st.sidebar.slider("Max number of flows to display", 5, 100, 25)
df = df.sort_values("count", ascending=False).head(top_n)

# Group and filter
df_grouped = df.groupby(["source_genre", "target_genre"], as_index=False)["count"].sum()

# Clean base genres
df_grouped["source_genre"] = df_grouped["source_genre"].str.strip()
df_grouped["target_genre"] = df_grouped["target_genre"].str.strip()

# Add labels
df_grouped["source_label"] = df_grouped["source_genre"] + " (Original)"
df_grouped["target_label"] = df_grouped["target_genre"] + " (Sampled)"

all_labels = pd.unique(df_grouped[["source_label", "target_label"]].values.ravel()).tolist()
label_to_index = {label: i for i, label in enumerate(all_labels)}

# Map to indexes
df_grouped["source_idx"] = df_grouped["source_label"].map(label_to_index)
df_grouped["target_idx"] = df_grouped["target_label"].map(label_to_index)

# Set positions: sources on left, targets on right
x_vals = []
y_vals = []
for i, label in enumerate(all_labels):
    x_vals.append(0.0 if "(Original)" in label else 1.0)
    y_vals.append(i / max(len(all_labels) - 1, 1))

# ─────────────────────── SELECT SOURCE/TARGET ───────────────────────
st.sidebar.subheader("Highlight by Node")
select_by = st.sidebar.radio("Select by", ["Source Genre", "Target Genre"])

if select_by == "Source Genre":
    selected_node = st.sidebar.selectbox("Select Source Genre", sorted(df_grouped["source_genre"].unique()))
    highlighted = (df_grouped["source_genre"] == selected_node)
else:
    selected_node = st.sidebar.selectbox("Select Target Genre", sorted(df_grouped["target_genre"].unique()))
    highlighted = (df_grouped["target_genre"] == selected_node)

highlight_color = px.colors.qualitative.Plotly[0]
colors = [highlight_color if h else "rgba(200,200,200,0.2)" for h in highlighted]

# ─────────────────────── DRAW SANKEY ───────────────────────
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
        color=colors,
        customdata=df_grouped[["source_genre", "target_genre", "count"]].values,
        hovertemplate="Original: %{customdata[0]}<br>Sampled: %{customdata[1]}<br>Count: %{customdata[2]}"
    )
)])

nodes_per_column = max(
    df_grouped["source_label"].nunique(),
    df_grouped["target_label"].nunique()
)
dynamic_height = int(nodes_per_column * 40 + 100)

fig.update_layout(
    title_text="🎵 Genre-to-Genre Sampling Flow",
    font=dict(size=16, family="Arial", color='blue'),
    height=dynamic_height,
)

fig.data[0].update(textfont=dict(color="black"))

st.plotly_chart(fig, use_container_width=True)

# ─────────────────────── BREAKDOWN CHART ───────────────────────
filtered = df[df["source_genre"] == selected_node] if select_by == "Source Genre" else df[df["target_genre"] == selected_node]
breakdown = filtered.groupby("target_genre" if select_by == "Source Genre" else "source_genre")["count"].sum().sort_values(ascending=False)
breakdown_percent = breakdown / breakdown.sum() * 100

breakdown_df = pd.DataFrame({"Genre": breakdown_percent.index, "Percent": breakdown_percent.values})

fig2 = px.pie(breakdown_df, names="Genre", values="Percent", title=f"Sampling Distribution from {selected_node}")
fig2.update_traces(textposition='inside', textinfo='percent+label')

st.plotly_chart(fig2, use_container_width=True)