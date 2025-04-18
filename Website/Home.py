import streamlit as st

st.set_page_config(
    page_title="Music KG Explorer",
    page_icon="🎶",
    layout="wide"
)

st.markdown("# 🎶 Music Sampling Knowledge Graph")
st.sidebar.success("Select a page above.")
st.write(
    """
    Welcome!  
    Use the **🔍 Search & Explore**, **📈 Sampling Timeline**,  
    or **🗺️ Genre‑to‑Genre Sampling Map** pages in the sidebar to explore.
    """
)
