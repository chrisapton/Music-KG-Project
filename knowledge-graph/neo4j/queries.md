## Load Data

### Constraints
```cypher
// Ensure unique IDs for core entities
CREATE CONSTRAINT song_id_unique IF NOT EXISTS
FOR (s:Song)
REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT artist_name_unique IF NOT EXISTS
FOR (a:Artist)
REQUIRE a.name IS UNIQUE;

CREATE CONSTRAINT album_title_unique IF NOT EXISTS
FOR (al:Album)
REQUIRE al.title IS UNIQUE;

CREATE CONSTRAINT year_value_unique IF NOT EXISTS
FOR (y:Year)
REQUIRE y.value IS UNIQUE;
```

### Tracks
```cypher
// Load WhoSampled tracks with proper relationships
LOAD CSV WITH HEADERS FROM 'file:///whosampled_tracks_2024.csv' AS row

MERGE (s:Song {id: row.whosampled_id})
SET s.title = row.title,
    s.url = row.url,
    s.record_label = row.record_label

// Album node
WITH s, row
WHERE row.album IS NOT NULL AND trim(row.album) <> ""
MERGE (al:Album {title: row.album})
MERGE (s)-[:PART_OF_ALBUM]->(al)

// Year node for temporal analysis
MERGE (y:Year {value: toInteger(row.release_year)})
MERGE (s)-[:RELEASED_IN]->(y)

// Artist relationships
WITH s, split(row.artist, ';') AS artistList
UNWIND artistList AS artistName
MERGE (a:Artist {name: trim(artistName)})
MERGE (s)-[:HAS_ARTIST]->(a)

```

### Sample Relationships
```cypher
LOAD CSV WITH HEADERS FROM 'file:///whosampled_relationships_2024.csv' AS row
MERGE (source:Song {id: row.source_id})
MERGE (target:Song {id: row.target_id})
MERGE (source)-[r:SAMPLES]->(target)
SET r.timestamp = datetime(row.timestamp),
    r.source_timestamps = split(row.timestamp_in_source, ';'),
    r.target_timestamps = split(row.timestamp_in_target, ';');
```
```cypher
LOAD CSV WITH HEADERS FROM 'file:///whosampled_relationships_2024.csv' AS row
MATCH (source:Song {id: row.source_id})
MATCH (target:Song {id: row.target_id})
MERGE (source)-[r:SAMPLES]->(target)
SET r.source_timestamps = split(row.timestamp_in_source, ';'),
    r.target_timestamps = split(row.timestamp_in_target, ';');
```

## Music Brainz Data
```cypher
// Load release dates
LOAD CSV WITH HEADERS FROM 'file:///musicbrainz_dates_2022.csv' AS row
MATCH (s:Song {id: row.id})
SET s.release_date = CASE 
        WHEN row.release_date <> '' THEN date(row.release_date)
        ELSE s.release_date
    END;
```
```cypher
// Load genres
LOAD CSV WITH HEADERS FROM 'file:///musicbrainz_genres_2022.csv' AS row
MATCH (s:Song {id: row.song_id})
MERGE (g:Genre {name: row.genre})
MERGE (s)-[:BELONGS_TO_GENRE]->(g);
```
```cypher
// Load artist summaries
LOAD CSV WITH HEADERS FROM 'file:///musicbrainz_summaries_2022.csv' AS row
MATCH (a:Artist {name: row.artist_name})
SET a.wikipedia_summary = row.wikipedia_summary;
```