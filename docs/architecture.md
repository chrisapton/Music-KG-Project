## Project Directory Structure
```
music_sampling_kg/  
│  
├── data/                           # Data storage directory  
│   ├── raw/                        # Raw data from different sources  
│   │   ├── whosampled/             # Raw data scraped from WhoSampled  
│   │   ├── musicbrainz/            # Data retrieved from MusicBrainz API
│   │   └── popularity/             # Popularity data from Spotify/last.fm
│   │
│   ├── processed/                  # Cleaned and processed data
│   │   ├── entities/               # Processed entity data (songs, artists, etc.)
│   │   └── relationships/          # Processed relationship data
│   │
│   └── integrated/                 # Integrated data ready for Neo4j import
│
├── scrapers/                       # Web scraping and API integration modules
│   ├── whosampled/                 # WhoSampled scraping scripts
│   │   ├── __init__.py
│   │   ├── scraper.py              # Main scraper implementation
│   │   └── parser.py               # HTML parsing utilities
│   │
│   ├── musicbrainz/                # MusicBrainz API integration
│   │   ├── __init__.py
│   │   ├── client.py               # API client implementation
│   │   └── matcher.py              # Song matching utilities
│   │
│   └── popularity/                 # Popularity data collection
│       ├── __init__.py
│       ├── spotify.py              # Spotify API integration
│       └── lastfm.py               # Last.fm scraping (alternative)
│
├── knowledge_graph/                # Knowledge graph construction and management
│   ├── __init__.py
│   ├── ontology/                   # Ontology definition and management
│   │   ├── __init__.py
│   │   ├── schema.py               # Schema definition
│   │   └── validation.py           # Ontology validation utilities
│   │
│   ├── neo4j/                      # Neo4j database management
│   │   ├── __init__.py
│   │   ├── connection.py           # Database connection utilities
│   │   ├── import.py               # Data import scripts
│   │   └── queries.py              # Common Cypher query templates
│   │
│   └── etl/                        # ETL pipelines for KG construction
│       ├── __init__.py
│       ├── transform.py            # Data transformation utilities
│       └── load.py                 # Data loading utilities
│
├── analysis/                       # Analysis modules
│   ├── __init__.py
│   ├── temporal/                   # Temporal analysis
│   │   ├── __init__.py
│   │   └── trends.py               # Trend analysis utilities
│   │
│   ├── genre/                      # Genre analysis
│   │   ├── __init__.py
│   │   └── influence.py            # Genre influence analysis
│   │
│   └── popularity/                 # Popularity analysis
│       ├── __init__.py
│       └── impact.py               # Popularity impact analysis
│
├── ml/                             # Machine learning modules
│   ├── __init__.py
│   ├── embeddings/                 # Node embedding implementations
│   │   ├── __init__.py
│   │   ├── node2vec.py             # Node2Vec implementation
│   │   └── graphsage.py            # GraphSAGE implementation
│   │
│   ├── models/                     # ML model implementations
│   │   ├── __init__.py
│   │   ├── temporal_gnn.py         # Temporal GNN implementation
│   │   └── prediction.py           # Prediction model implementations
│   │
│   └── evaluation/                 # Model evaluation utilities
│       ├── __init__.py
│       └── metrics.py              # Evaluation metrics
│
├── visualization/                  # Visualization modules
│   ├── __init__.py
│   ├── static/                     # Static assets for visualization
│   │   ├── css/                    # CSS stylesheets
│   │   ├── js/                     # JavaScript files
│   │   └── images/                 # Image assets
│   │
│   ├── components/                 # Visualization components
│   │   ├── __init__.py
│   │   ├── graph.py                # Graph visualization components
│   │   ├── timeline.py             # Timeline visualization components
│   │   └── network.py              # Network visualization components
│   │
│   └── app/                        # Visualization application
│       ├── __init__.py
│       ├── routes.py               # Application routes
│       └── templates/              # HTML templates
│
├── api/                            # API layer
│   ├── __init__.py
│   ├── routes/                     # API routes
│   │   ├── __init__.py
│   │   ├── graph.py                # Graph API endpoints
│   │   ├── analysis.py             # Analysis API endpoints
│   │   └── prediction.py           # Prediction API endpoints
│   │
│   └── middleware/                 # API middleware
│       ├── __init__.py
│       ├── auth.py                 # Authentication middleware
│       └── logging.py              # Logging middleware
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── scrapers/                   # Scraper tests
│   ├── knowledge_graph/            # Knowledge graph tests
│   ├── analysis/                   # Analysis tests
│   ├── ml/                         # ML tests
│   └── visualization/              # Visualization tests
│
├── notebooks/                      # Jupyter notebooks for exploration and demonstration
│   ├── data_exploration.ipynb      # Data exploration notebook
│   ├── graph_analysis.ipynb        # Graph analysis notebook
│   └── ml_experiments.ipynb        # ML experimentation notebook
│
├── docs/                           # Documentation
│   ├── architecture/               # Architecture documentation
│   ├── api/                        # API documentation
│   ├── ontology/                   # Ontology documentation
│   └── user_guide/                 # User guide
│
├── scripts/                        # Utility scripts
│   ├── setup.sh                    # Environment setup script
│   ├── import_data.py              # Data import script
│   └── export_data.py              # Data export script
│
├── config/                         # Configuration files
│   ├── development.yaml            # Development configuration
│   ├── production.yaml             # Production configuration
│   └── testing.yaml                # Testing configuration
│
├── .gitignore                      # Git ignore file
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup script
├── README.md                       # Project README
└── LICENSE                         # Project license
```
