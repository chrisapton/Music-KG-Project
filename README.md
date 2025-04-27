# Music Sampling Knowledge Graph - Quick Start Guide

This guide explains **only** how to:
1. Run the Neo4j database
2. Inject data into Neo4j
3. Launch the Streamlit app

---

## 1. Running Neo4j

Navigate to the `KnowledgeGraph/neo4j` directory and run:

```bash
cd KnowledgeGraph/neo4j
docker compose up -d
```

- This will start Neo4j using the `docker-compose.yml` provided.
- Neo4j Browser will be available at http://localhost:7474  
  (Login with username `neo4j`, password `testpassword`).

Make sure Docker is installed before running this.

---

## 2. Injecting Data into Neo4j

Once Neo4j is running, from the root project directory:

```bash
python load_data.py
```

- This script will connect to `bolt://localhost:7687`.
- It loads all necessary nodes and relationships into the database.

**Important:** Ensure `load_data.py` uses the correct credentials (`neo4j` / `testpassword` by default).

---

## 3. Running the Streamlit App

From the project root directory:

```bash
cd Website
streamlit run Website/Home.py
```

- The app will open in your browser (usually at http://localhost:8501).
- Explore the knowledge graph via the web interface.

**Reminder:** Neo4j must be running before launching the Streamlit app.

---
