# Music Sampling Knowledge Graph Project Requirements Analysis

## Project Domain & Goals
The project aims to create a knowledge graph focused on music sampling that will:
- Provide a comprehensive view of how songs and artists influence each other through sampling
- Enable users to explore relationships between songs
- Analyze how sampling impacts music trends
- Uncover connections across genres
- Offer insights into the cultural and historical significance of sampling in music

## Key Research Questions
1. How does sampling affect the popularity of older songs?
2. How do different genres influence each other through sampling?
3. How can we predict future sampling trends based on historical patterns?
4. How has sampling evolved over time?
5. What are emerging trends in music sampling?

## Data Sources
1. **WhoSampled**: Information on songs that sample other songs
2. **MusicBrainz**: Metadata such as release year, genre, and artist details
3. **Spotify API or last.fm**: Popularity metrics and related artist connections

## Preliminary Entity Types
1. Song
2. Artist
3. Genre
4. Year
5. Producer
6. Album
7. Popularity
8. Related Artist

## Preliminary Relationship Types
1. SAMPLES (Song → Song)
2. HAS_ARTIST (Song → Artist)
3. BELONGS_TO_GENRE (Song → Genre)
4. HAS_POPULARITY (Song → Popularity)
5. RELEASED_IN (Song → Year)
6. PRODUCED_BY (Song → Producer)
7. PART_OF (Song → Album)
8. RELATED_TO (Artist → Artist)

## Storage & Visualization
- Neo4j database for storage
- Neo4j visualization capabilities for interactive GUI

## Ontology Considerations
- Develop custom ontology tailored to specific needs
- Explore feasibility of using the Music Ontology (http://musicontology.com/)
