# Core Entities and Relationships for Music Sampling Knowledge Graph

## Overview
This document defines the core entities and relationships for the music sampling knowledge graph, integrating concepts from the Music Ontology while addressing the specific requirements for music sampling.

## Entity Classes and Hierarchies

### Primary Entities

1. **Song**
   - Definition: A musical composition that has been recorded and released
   - Properties: title, release_date, duration, popularity_score, isrc
   - Subclasses: 
     - OriginalSong (songs that are sampled by others)
     - DerivativeSong (songs that contain samples from others)
     - Note: A song can be both original and derivative

2. **Artist**
   - Definition: A person or group who creates or performs music
   - Properties: name, active_period, biography, location
   - Subclasses:
     - MusicGroup (bands, ensembles)
     - SoloArtist (individual musicians)
     - Producer (creators who may not perform)

3. **Sample**
   - Definition: A portion of one song that is used in another song
   - Properties: start_time, end_time, duration, modification_type, clearance_status
   - Note: This is a key entity specific to our sampling knowledge graph

4. **Genre**
   - Definition: A category that identifies music as belonging to a shared tradition or set of conventions
   - Properties: name, description, era, parent_genre
   - Note: Hierarchical structure to represent genre/subgenre relationships

5. **Album**
   - Definition: A collection of songs released together
   - Properties: title, release_date, label, format, cover_art

6. **Release**
   - Definition: A specific version or edition of a song or album
   - Properties: release_date, format, label, country

7. **Popularity**
   - Definition: Metrics indicating the commercial success or cultural impact of a song
   - Properties: stream_count, chart_position, sales_figures, listener_count

8. **TimePeriod**
   - Definition: A specific time range relevant to music history
   - Properties: start_year, end_year, name

### Secondary Entities

9. **Label**
   - Definition: A company that produces and distributes music
   - Properties: name, founding_date, location

10. **Instrument**
    - Definition: A musical device used in the creation or performance of music
    - Properties: name, type, family

11. **SampleTechnique**
    - Definition: The method used to incorporate a sample into a new song
    - Properties: name, description, first_used_date

12. **Event**
    - Definition: A significant occurrence in the music production process
    - Subclasses:
      - Composition (creation of a musical work)
      - Performance (live rendition of a musical work)
      - Recording (capturing of a performance)
      - SamplingEvent (act of incorporating a sample into a new work)

## Relationship Types

### Primary Relationships

1. **SAMPLES**
   - Definition: Indicates that one song samples another
   - Domain: Song
   - Range: Song
   - Properties: sample_timestamp, duration, clearance_status
   - Note: This is the core relationship for our knowledge graph

2. **HAS_SAMPLE**
   - Definition: Connects a song to a specific sample instance
   - Domain: Song
   - Range: Sample

3. **SAMPLED_IN**
   - Definition: Connects a sample to the song where it appears
   - Domain: Sample
   - Range: Song

4. **CREATED_BY**
   - Definition: Connects a song to its creator(s)
   - Domain: Song
   - Range: Artist

5. **PERFORMED_BY**
   - Definition: Connects a song to its performer(s)
   - Domain: Song
   - Range: Artist

6. **PRODUCED_BY**
   - Definition: Connects a song to its producer(s)
   - Domain: Song
   - Range: Artist (specifically Producer)

7. **BELONGS_TO_GENRE**
   - Definition: Categorizes a song within a musical genre
   - Domain: Song
   - Range: Genre

8. **RELEASED_IN**
   - Definition: Connects a song to its release period
   - Domain: Song
   - Range: TimePeriod

9. **PART_OF**
   - Definition: Indicates that a song is included in an album
   - Domain: Song
   - Range: Album

10. **HAS_POPULARITY**
    - Definition: Connects a song to its popularity metrics
    - Domain: Song
    - Range: Popularity

11. **INFLUENCED**
    - Definition: Indicates that one artist influenced another
    - Domain: Artist
    - Range: Artist

12. **COLLABORATED_WITH**
    - Definition: Indicates that artists worked together
    - Domain: Artist
    - Range: Artist

### Secondary Relationships

13. **RELEASED_BY**
    - Definition: Connects a song or album to its releasing label
    - Domain: Song or Album
    - Range: Label

14. **USES_TECHNIQUE**
    - Definition: Connects a sample to the technique used
    - Domain: Sample
    - Range: SampleTechnique

15. **RECORDED_USING**
    - Definition: Connects a song to instruments used in its creation
    - Domain: Song
    - Range: Instrument

16. **DERIVED_FROM**
    - Definition: Indicates that a song is a derivative work of another
    - Domain: Song
    - Range: Song
    - Note: Broader than SAMPLES, includes covers, remixes, etc.

17. **SAMPLED_AT_EVENT**
    - Definition: Connects a sample to the sampling event
    - Domain: Sample
    - Range: SamplingEvent

## Integration with Music Ontology

The defined entities and relationships extend and specialize the Music Ontology in the following ways:

1. **Extending mo:Signal and mo:Sound** with Sample entity to capture specific sampling information
2. **Specializing mo:MusicalWork** with OriginalSong and DerivativeSong to represent sampling relationships
3. **Utilizing mo:MusicArtist and mo:MusicGroup** as parent classes for our Artist entity
4. **Incorporating the event-based workflow model** from Music Ontology (Composition → Performance → Recording) and extending it with SamplingEvent
5. **Adopting mo:genre, mo:published_as, and mo:release** relationships while adding sampling-specific relationships

## Ontology Namespace

The music sampling ontology will use the following namespace:
- `ms:` for Music Sampling ontology (http://example.org/music-sampling-ontology#)

It will import and reference the following existing ontologies:
- `mo:` for Music Ontology (http://purl.org/ontology/mo/)
- `foaf:` for Friend of a Friend (http://xmlns.com/foaf/0.1/)
- `dc:` for Dublin Core (http://purl.org/dc/elements/1.1/)
- `event:` for Event Ontology (http://purl.org/NET/c4dm/event.owl#)
- `tl:` for Timeline Ontology (http://purl.org/NET/c4dm/timeline.owl#)
