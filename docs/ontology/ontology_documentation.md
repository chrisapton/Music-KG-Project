# Music Sampling Knowledge Graph Ontology Documentation

## 1. Introduction

This document provides comprehensive documentation for the Music Sampling Knowledge Graph Ontology, which models the domain of music sampling and the relationships between songs, artists, and other music-related entities. The ontology is designed to support research questions about how songs and artists influence one another through sampling, how sampling impacts music trends, and how to uncover connections across genres.

### 1.1 Purpose and Scope

The Music Sampling Knowledge Graph Ontology aims to:
- Provide a comprehensive view of how songs and artists influence each other through sampling
- Enable exploration of relationships between songs
- Support analysis of how sampling impacts music trends
- Facilitate discovery of connections across genres
- Offer insights into the cultural and historical significance of sampling in music

### 1.2 Key Research Questions

The ontology is designed to address the following research questions:
1. How does sampling affect the popularity of older songs?
2. How do different genres influence each other through sampling?
3. How can we predict future sampling trends based on historical patterns?
4. How has sampling evolved over time?
5. What are emerging trends in music sampling?

### 1.3 Data Sources

The knowledge graph will integrate data from multiple sources:
- **WhoSampled**: Information on songs that sample other songs
- **MusicBrainz**: Metadata such as release year, genre, and artist details
- **Spotify API or last.fm**: Popularity metrics and related artist connections

## 2. Ontology Overview

The Music Sampling Knowledge Graph Ontology extends and specializes the Music Ontology (http://musicontology.com/) to focus specifically on sampling relationships between musical works. It incorporates concepts from the Music Ontology while adding sampling-specific entities, properties, and relationships.

### 2.1 Namespace

The music sampling ontology uses the following namespace:
- `ms:` for Music Sampling ontology (http://example.org/music-sampling-ontology#)

It imports and references the following existing ontologies:
- `mo:` for Music Ontology (http://purl.org/ontology/mo/)
- `foaf:` for Friend of a Friend (http://xmlns.com/foaf/0.1/)
- `dc:` for Dublin Core (http://purl.org/dc/elements/1.1/)
- `event:` for Event Ontology (http://purl.org/NET/c4dm/event.owl#)
- `tl:` for Timeline Ontology (http://purl.org/NET/c4dm/timeline.owl#)

## 3. Entity Classes

### 3.1 Primary Entities

#### 3.1.1 Song
- **Definition**: A musical composition that has been recorded and released
- **Properties**: title, release_date, duration, popularity_score, isrc, lyrics, bpm, key
- **Subclasses**: 
  - **OriginalSong**: Songs that are sampled by others
  - **DerivativeSong**: Songs that contain samples from others
  - **Note**: A song can be both original and derivative

#### 3.1.2 Artist
- **Definition**: A person or group who creates or performs music
- **Properties**: name, active_period_start, active_period_end, biography, location, mbid
- **Subclasses**:
  - **MusicGroup**: Bands, ensembles
  - **SoloArtist**: Individual musicians
  - **Producer**: Creators who may not perform

#### 3.1.3 Sample
- **Definition**: A portion of one song that is used in another song
- **Properties**: start_time, end_time, duration, modification_type, clearance_status, prominence, loop_count
- **Note**: This is a key entity specific to our sampling knowledge graph

#### 3.1.4 Genre
- **Definition**: A category that identifies music as belonging to a shared tradition or set of conventions
- **Properties**: name, description, era, parent_genre, origin_location, origin_year
- **Note**: Hierarchical structure to represent genre/subgenre relationships

#### 3.1.5 Album
- **Definition**: A collection of songs released together
- **Properties**: title, release_date, label, format, cover_art, mbid, total_tracks

#### 3.1.6 Release
- **Definition**: A specific version or edition of a song or album
- **Properties**: release_date, format, label, country, catalog_number, barcode

#### 3.1.7 Popularity
- **Definition**: Metrics indicating the commercial success or cultural impact of a song
- **Properties**: stream_count, chart_position, sales_figures, listener_count, peak_date, certification

#### 3.1.8 TimePeriod
- **Definition**: A specific time range relevant to music history
- **Properties**: start_year, end_year, name, description

### 3.2 Secondary Entities

#### 3.2.1 Label
- **Definition**: A company that produces and distributes music
- **Properties**: name, founding_date, location, parent_company, status

#### 3.2.2 Instrument
- **Definition**: A musical device used in the creation or performance of music
- **Properties**: name, type, family, year_introduced, manufacturer

#### 3.2.3 SampleTechnique
- **Definition**: The method used to incorporate a sample into a new song
- **Properties**: name, description, first_used_date, equipment, difficulty

#### 3.2.4 Event
- **Definition**: A significant occurrence in the music production process
- **Properties**: date, location, participants, description
- **Subclasses**:
  - **Composition**: Creation of a musical work
  - **Performance**: Live rendition of a musical work
  - **Recording**: Capturing of a performance
  - **SamplingEvent**: Act of incorporating a sample into a new work

## 4. Relationships

### 4.1 Primary Relationships

#### 4.1.1 SAMPLES
- **Definition**: Indicates that one song samples another
- **Domain**: Song
- **Range**: Song
- **Properties**: sample_timestamp, duration, clearance_status, sample_type, legal_case
- **Note**: This is the core relationship for our knowledge graph

#### 4.1.2 HAS_SAMPLE
- **Definition**: Connects a song to a specific sample instance
- **Domain**: Song
- **Range**: Sample

#### 4.1.3 SAMPLED_IN
- **Definition**: Connects a sample to the song where it appears
- **Domain**: Sample
- **Range**: Song

#### 4.1.4 CREATED_BY
- **Definition**: Connects a song to its creator(s)
- **Domain**: Song
- **Range**: Artist
- **Properties**: role, contribution_type, year

#### 4.1.5 PERFORMED_BY
- **Definition**: Connects a song to its performer(s)
- **Domain**: Song
- **Range**: Artist

#### 4.1.6 PRODUCED_BY
- **Definition**: Connects a song to its producer(s)
- **Domain**: Song
- **Range**: Artist (specifically Producer)

#### 4.1.7 BELONGS_TO_GENRE
- **Definition**: Categorizes a song within a musical genre
- **Domain**: Song
- **Range**: Genre
- **Properties**: confidence, primary, source

#### 4.1.8 RELEASED_IN
- **Definition**: Connects a song to its release period
- **Domain**: Song
- **Range**: TimePeriod

#### 4.1.9 PART_OF
- **Definition**: Indicates that a song is included in an album
- **Domain**: Song
- **Range**: Album

#### 4.1.10 HAS_POPULARITY
- **Definition**: Connects a song to its popularity metrics
- **Domain**: Song
- **Range**: Popularity

#### 4.1.11 INFLUENCED
- **Definition**: Indicates that one artist influenced another
- **Domain**: Artist
- **Range**: Artist
- **Properties**: strength, time_period, source, influence_type

#### 4.1.12 COLLABORATED_WITH
- **Definition**: Indicates that artists worked together
- **Domain**: Artist
- **Range**: Artist

### 4.2 Secondary Relationships

#### 4.2.1 RELEASED_BY
- **Definition**: Connects a song or album to its releasing label
- **Domain**: Song or Album
- **Range**: Label

#### 4.2.2 USES_TECHNIQUE
- **Definition**: Connects a sample to the technique used
- **Domain**: Sample
- **Range**: SampleTechnique

#### 4.2.3 RECORDED_USING
- **Definition**: Connects a song to instruments used in its creation
- **Domain**: Song
- **Range**: Instrument

#### 4.2.4 DERIVED_FROM
- **Definition**: Indicates that a song is a derivative work of another
- **Domain**: Song
- **Range**: Song
- **Note**: Broader than SAMPLES, includes covers, remixes, etc.

#### 4.2.5 SAMPLED_AT_EVENT
- **Definition**: Connects a sample to the sampling event
- **Domain**: Sample
- **Range**: SamplingEvent

## 5. Property Definitions

### 5.1 Data Types

| Data Type | Format | Description |
|-----------|--------|-------------|
| String | Text | Basic text string |
| Text | Long text | Extended text content |
| Integer | Whole number | Numeric value without decimals |
| Float | Decimal number | Numeric value with decimals |
| Date | YYYY-MM-DD | Calendar date |
| Boolean | true/false | Binary value |
| Enum | Predefined values | Selection from a fixed set of values |
| URL | Valid URL format | Web address |
| Reference | Entity identifier | Reference to another entity in the ontology |
| Array | List of values | Collection of values of the same type |

### 5.2 Property Constraints

| Constraint Type | Description | Example |
|-----------------|-------------|---------|
| Required | Property must have a value | title is Required |
| Min | Minimum numeric value | duration Min: 1 |
| Max | Maximum numeric value | popularity_score Max: 100.0 |
| Range | Valid range of values | Range: 0.0-1.0 |
| Format | Specific format requirement | Format: YYYY-MM-DD |
| Max length | Maximum string length | Max length: 200 |
| Values | Enumeration of allowed values | Values: ["CD", "Vinyl", "Cassette", "Digital", "Other"] |
| Default | Default value if not specified | Default: false |

### 5.3 Core Entity Properties

Detailed property definitions for each entity can be found in the [Property Definitions](property_definitions.md) document.

## 6. Integration with Music Ontology

The defined entities and relationships extend and specialize the Music Ontology in the following ways:

1. **Extending mo:Signal and mo:Sound** with Sample entity to capture specific sampling information
2. **Specializing mo:MusicalWork** with OriginalSong and DerivativeSong to represent sampling relationships
3. **Utilizing mo:MusicArtist and mo:MusicGroup** as parent classes for our Artist entity
4. **Incorporating the event-based workflow model** from Music Ontology (Composition → Performance → Recording) and extending it with SamplingEvent
5. **Adopting mo:genre, mo:published_as, and mo:release** relationships while adding sampling-specific relationships

## 7. Implementation

### 7.1 Storage

The knowledge graph will be implemented in Neo4j, a graph database that provides:
- Native graph storage and processing
- Cypher query language for graph traversal
- Visualization capabilities for exploring the knowledge graph

### 7.2 Data Integration Process

1. Extract sampling information from WhoSampled
2. Match songs to MusicBrainz entries to obtain metadata
3. Enrich with popularity data from Spotify API or last.fm
4. Transform data to conform to the ontology structure
5. Load data into Neo4j

### 7.3 Example Queries

#### 7.3.1 Find all songs that sample a specific song
```cypher
MATCH (s1:Song)-[:SAMPLES]->(s2:Song {title: "The Last Time"})
RETURN s1.title, s1.release_date
```

#### 7.3.2 Find genres that frequently sample from each other
```cypher
MATCH (s1:Song)-[:BELONGS_TO_GENRE]->(g1:Genre),
      (s2:Song)-[:BELONGS_TO_GENRE]->(g2:Genre),
      (s1)-[:SAMPLES]->(s2)
RETURN g1.name, g2.name, count(*) as sample_count
ORDER BY sample_count DESC
```

#### 7.3.3 Find the most sampled songs in a specific time period
```cypher
MATCH (s:Song)<-[r:SAMPLES]-()
WHERE s.release_date >= '1970-01-01' AND s.release_date <= '1979-12-31'
RETURN s.title, s.artist, count(r) as times_sampled
ORDER BY times_sampled DESC
LIMIT 10
```

## 8. Visualization

The ontology structure is visualized in the [Ontology Diagram](ontology_diagram_improved.png), which shows the entities, their hierarchies, and the relationships between them.

## 9. Future Extensions

Potential future extensions to the ontology include:
1. Integration with audio feature data (e.g., spectral characteristics, rhythm patterns)
2. Incorporation of cultural and historical context
3. Addition of user-generated content such as reviews and ratings
4. Expansion to include more detailed legal information about sampling clearance
5. Integration with music recommendation systems

## 10. Conclusion

The Music Sampling Knowledge Graph Ontology provides a comprehensive framework for modeling the domain of music sampling and the relationships between songs, artists, and other music-related entities. By integrating data from multiple sources and extending the Music Ontology with sampling-specific concepts, it enables researchers and music enthusiasts to explore the rich tapestry of influences and connections in the world of music sampling.

## Appendices

### Appendix A: Glossary

- **Sample**: A portion of one song that is used in another song
- **Sampling**: The act of taking a portion of one sound recording and reusing it in a different song
- **Clearance**: Legal permission to use a sample
- **ISRC**: International Standard Recording Code, a unique identifier for sound recordings
- **MusicBrainz Identifier (MBID)**: A unique identifier used by the MusicBrainz database

### Appendix B: References

1. Music Ontology: http://musicontology.com/
2. WhoSampled: https://www.whosampled.com/
3. MusicBrainz: https://musicbrainz.org/
4. Neo4j Graph Database: https://neo4j.com/
5. Friend of a Friend (FOAF) Ontology: http://xmlns.com/foaf/0.1/
6. Dublin Core Metadata Initiative: https://dublincore.org/
7. Event Ontology: http://motools.sourceforge.net/event/event.html
8. Timeline Ontology: http://motools.sourceforge.net/timeline/timeline.html
